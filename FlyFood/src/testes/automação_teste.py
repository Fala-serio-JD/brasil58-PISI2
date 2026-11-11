import os
import shutil
import sys
import time

sys.dont_write_bytecode = True
# Permite rodar este arquivo de qualquer diretório (a pasta src do FlyFood).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import algoritmoGenetico, formatar_trajeto
from leitura_entrada import ler_entrada, converter_para_ag

# ---------------------------------------------------------------------------
# Configuração da bateria
# ---------------------------------------------------------------------------

# Custos ótimos conhecidos (1ª VA) e quantidade de pontos de entrega.
OTIMOS_CONHECIDOS = {
    "matriz1": {"custo": 14, "pontos": 4},
    "matriz2": {"custo": 22, "pontos": 6},
    "matriz3": {"custo": 26, "pontos": 8},
    "matriz4": {"custo": 38, "pontos": 10},
    "matriz5": {"custo": 50, "pontos": 12},
}

NUMERO_DE_REPETICOES = 5

# Cenários calibrados para o contexto do FlyFood (instâncias de 4 a 12
# pontos de entrega), no mesmo estilo dos cenários do brasil58.
CENARIOS = [
    {"nome": "Cenario 1 - Execucao Rapida", "tamPop": 20, "probInversao": 0.1, "geracoes": 50},
    {"nome": "Cenario 2 - Parametros Base", "tamPop": 50, "probInversao": 0.3, "geracoes": 200},
    {"nome": "Cenario 3 - Alta Mutacao", "tamPop": 50, "probInversao": 0.8, "geracoes": 200},
    {"nome": "Cenario 4 - Populacao Extensa", "tamPop": 200, "probInversao": 0.3, "geracoes": 200},
]

PASTA_ENTRADAS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "entradas"))
PASTA_RELATORIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatórios")
PASTA_PROJETO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LARGURA = 100

class SaidaDuplicada:
    """Escreve o texto simultaneamente no terminal e no arquivo de relatório."""

    def __init__(self, *destinos):
        self.destinos = destinos

    def write(self, texto):
        for destino in self.destinos:
            destino.write(texto)
        return len(texto)

    def flush(self):
        for destino in self.destinos:
            destino.flush()


def proximo_arquivo_relatorio():
    """Devolve o próximo nome livre (relatorio1.txt, relatorio2.txt, ...)."""
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    numero = 1
    while True:
        caminho = os.path.join(PASTA_RELATORIOS, f"relatorio{numero}.txt")
        if not os.path.exists(caminho):
            return caminho
        numero += 1


def limpar_pycache():
    """Remove pastas __pycache__ criadas durante os testes."""
    for pasta_atual, subpastas, _ in os.walk(PASTA_PROJETO):
        if "__pycache__" in subpastas:
            shutil.rmtree(os.path.join(pasta_atual, "__pycache__"), ignore_errors=True)
            subpastas.remove("__pycache__")

def executar_bateria():
    arquivo_relatorio = proximo_arquivo_relatorio()

    lista_otimos = ", ".join(
        f"{nome}={dados['custo']}" for nome, dados in OTIMOS_CONHECIDOS.items()
    )
    cabecalho = (
        "==========================================================\n"
        " RELATORIO DE TESTES - ALGORITMO GENETICO (FLYFOOD)\n"
        f" Otimo conhecido por instancia (1a VA): {lista_otimos} (dronometros)\n"
        f" Repeticoes por cenario/instancia: {NUMERO_DE_REPETICOES}\n"
        "=========================================================="
    )

    with open(arquivo_relatorio, "w", encoding="utf-8") as arquivo:
        saida = SaidaDuplicada(sys.stdout, arquivo)

        def imprimir(*valores):
            print(*valores, file=saida)

        imprimir(cabecalho)

        imprimir("\nCENARIOS E PARAMETROS")
        for cenario in CENARIOS:
            imprimir(
                f"- {cenario['nome']}: tamPop={cenario['tamPop']}, "
                f"probInversao={cenario['probInversao']}, geracoes={cenario['geracoes']}, "
                "elite=2 (padrao), torneio=3 (padrao)"
            )
        imprimir()

        # Conversão das 5 matrizes para o formato do A.G. (feita uma única vez,
        # fora da medição de tempo, como o carregamento das distâncias no brasil58).
        instancias = {}
        for nome, dados in OTIMOS_CONHECIDOS.items():
            locais, pontosEntrega = ler_entrada(
                os.path.join(PASTA_ENTRADAS, f"{nome}.txt")
            )
            dicDistancias, legenda = converter_para_ag(locais, pontosEntrega)
            instancias[nome] = {"distancias": dicDistancias, "legenda": legenda}

        # dados_tabela guarda, por cenário: gap médio (%) por instância,
        # total de execuções que atingiram o ótimo e tempo médio geral.
        dados_tabela = []
        rotas_das_melhores = {}

        for cenario in CENARIOS:
            imprimir(f"\n[Iniciando] {cenario['nome']}...")

            tempos_cenario = []
            gaps_cenario = {}
            acertos_cenario = 0
            execucoes_cenario = 0

            for nome, dados_otimo in OTIMOS_CONHECIDOS.items():
                instancia = instancias[nome]
                custos = []
                tempos = []
                geracoes = []
                melhor_rota = None
                melhor_custo_absoluto = float("inf")

                for i in range(NUMERO_DE_REPETICOES):
                    inicio = time.time()
                    rota, custo, geracaoRecorde = algoritmoGenetico(
                        instancia["distancias"],
                        len(instancia["legenda"]),
                        tamPop=cenario["tamPop"],
                        probInversao=cenario["probInversao"],
                        geracoes=cenario["geracoes"],
                        verboso=False,
                    )
                    tempo_gasto = time.time() - inicio

                    custos.append(custo)
                    tempos.append(tempo_gasto)
                    geracoes.append(geracaoRecorde)
                    if custo == dados_otimo["custo"]:
                        acertos_cenario += 1
                    execucoes_cenario += 1

                    # Guarda a rota da melhor execução (para exibir no relatório).
                    if custo <= melhor_custo_absoluto:
                        melhor_custo_absoluto = custo
                        melhor_rota = rota

                    imprimir(
                        f"  -> {nome} ({dados_otimo['pontos']} pontos) | "
                        f"Teste {i+1}/{NUMERO_DE_REPETICOES} | Custo: {custo} | "
                        f"Geracao do recorde: {geracaoRecorde} | Tempo: {tempo_gasto:.4f}s"
                    )

                otimo = dados_otimo["custo"]
                melhor_custo = min(custos)
                pior_custo = max(custos)
                media_custo = sum(custos) / len(custos)
                media_geracoes = sum(geracoes) / len(geracoes)
                gap = ((melhor_custo - otimo) / otimo) * 100
                gap_medio = ((media_custo - otimo) / otimo) * 100
                tempos_cenario += tempos
                gaps_cenario[nome] = gap_medio
                rotas_das_melhores[(cenario["nome"], nome)] = (
                    melhor_rota, melhor_custo, instancia["legenda"]
                )

                imprimir(
                    f"\nRESULTADOS {cenario['nome']} - {nome}\n"
                    f"  - Otimo conhecido: {otimo} dronometros\n"
                    f"  - Melhor Custo: {melhor_custo} | Pior Custo: {pior_custo} | "
                    f"Custo Medio: {media_custo:.1f}\n"
                    f"  - Melhor rota: {formatar_trajeto(melhor_rota, instancia['legenda'])}\n"
                    f"  - Geracao media do recorde: {media_geracoes:.0f}\n"
                    f"  - Tempo Medio: {sum(tempos)/len(tempos):.4f}s\n"
                    f"  - Gap do melhor p/ otimo: +{gap:.2f}% | gap medio: +{gap_medio:.2f}%\n"
                    "----------------------------------------------------------"
                )

            dados_tabela.append([
                cenario["nome"],
                dict(gaps_cenario),
                sum(tempos_cenario) / len(tempos_cenario),
                acertos_cenario,
                execucoes_cenario,
            ])

        # ------------------------------------------------------------------
        # Tabela geral: gap MEDIO (%) de cada cenário por instancia (o gap
        # do melhor custo e 0.00% nas instancias pequenas mesmo em cenarios
        # fracos, pois 5 repeticoes bastam para algum acerto; o gap medio e
        # o numero de acertos mostram a confiabilidade real de cada cenario).
        # ------------------------------------------------------------------
        nomes_instancias = list(OTIMOS_CONHECIDOS.keys())
        tabela = "\n" + "=" * LARGURA + "\n"
        cabecalho_tabela = f"{'CENARIO':<30}"
        for nome in nomes_instancias:
            cabecalho_tabela += f" | {nome.upper()[:7]:>7}"
        cabecalho_tabela += f" | {'ACERTOS':>7} | {'T.MEDIO':>7}\n"
        tabela += cabecalho_tabela
        tabela += "-" * LARGURA + "\n"

        for nome_cenario, gaps, tempo_medio, acertos, execucoes in dados_tabela:
            linha = f"{nome_cenario:<30}"
            for nome in nomes_instancias:
                linha += f" | {gaps[nome]:+6.2f}%"
            linha += f" | {acertos:>4}/{execucoes:<2} | {tempo_medio:6.3f}s"
            tabela += linha + "\n"

        tabela += "=" * LARGURA + "\n"

        # Síntese: melhor cenário = menor soma de gaps medios; empate decide
        # o menor tempo medio por execucao.
        vencedor = None
        for nome_cenario, gaps, tempo_medio, acertos, execucoes in dados_tabela:
            soma_gaps = sum(gaps.values())
            chave = (soma_gaps, tempo_medio)
            if vencedor is None or chave < vencedor[0]:
                vencedor = (chave, nome_cenario, gaps, tempo_medio, acertos, execucoes)

        imprimir(tabela)
        imprimir(
            "\nSINTESE GERAL\n"
            f"Melhor configuracao: {vencedor[1]} (menor gap medio somado;\n"
            f"empate resolvido pelo menor tempo medio)\n"
            f"Execucoes no otimo nesta configuracao: {vencedor[4]}/{vencedor[5]}\n"
            f"Tempo medio por execucao: {vencedor[3]:.4f}s\n"
            "Custos otimos encontrados (1a VA -> A.G.):\n"
        )
        for nome, dados_otimo in OTIMOS_CONHECIDOS.items():
            rota, custo, legenda = rotas_das_melhores[(vencedor[1], nome)]
            imprimir(
                f"  - {nome}: {dados_otimo['custo']} -> {custo} dronometros | "
                f"{formatar_trajeto(rota, legenda)}"
            )
        imprimir(
            "\nObservacoes metodologicas:\n"
            "  - O A.G. e estocastico: custos variam entre repeticoes; o gap\n"
            "    do bloco de resultados considera o MELHOR custo obtido, e a\n"
            "    tabela geral considera o gap MEDIO das repeticoes.\n"
            "  - Circuitos otimos equivalentes (girados ou invertidos) tem o\n"
            "    mesmo custo; a rota exibida pode diferir da 1a VA por isso.\n"
            "  - Conversao das matrizes feita uma unica vez fora do cronometro\n"
            "    (mesmo criterio do carregamento das distancias no brasil58)."
        )

    print(f"\n[OK] Relatorio salvo em: {arquivo_relatorio}")


def rodar_bateria_de_testes():
    try:
        executar_bateria()
    finally:
        limpar_pycache()


if __name__ == "__main__":
    rodar_bateria_de_testes()
