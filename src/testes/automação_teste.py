import os
import shutil
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from main import algoritmoGenetico, lerDistancias, ARQUIVO_ARESTAS

OTIMO_CONHECIDO = 25395
NUMERO_DE_REPETICOES = 5  
PASTA_RELATORIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatórios")
PASTA_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class SaidaDuplicada:
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
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)
    numero = 1
    while True:
        caminho = os.path.join(PASTA_RELATORIOS, f"relatorio{numero}.txt")
        if not os.path.exists(caminho):
            return caminho
        numero += 1


def limpar_pycache():
    for pasta_atual, subpastas, _ in os.walk(PASTA_SRC):
        if "__pycache__" in subpastas:
            shutil.rmtree(os.path.join(pasta_atual, "__pycache__"), ignore_errors=True)
            subpastas.remove("__pycache__")


def executar_bateria():
    cenarios = [
        {"nome": "Cenario 1 - Execucao Rapida", "tamPop": 50, "probInversao": 0.1, "geracoes": 1000},
        {"nome": "Cenario 2 - Parametros Base", "tamPop": 100, "probInversao": 0.3, "geracoes": 2000},
        {"nome": "Cenario 3 - Alta Mutacao", "tamPop": 100, "probInversao": 0.8, "geracoes": 2000},
        {"nome": "Cenario 4 - Populacao Extensa", "tamPop": 300, "probInversao": 0.3, "geracoes": 2000}
    ]

    arquivo_relatorio = proximo_arquivo_relatorio()
    cabecalho = (
        "==========================================================\n"
        " RELATORIO DE TESTES - ALGORITMO GENETICO (BRAZIL58.TSP)\n"
        f" Alvo (Menor custo conhecido): {OTIMO_CONHECIDO}\n"
        f" Repeticoes por cenario: {NUMERO_DE_REPETICOES}\n"
        "=========================================================="
    )

    with open(arquivo_relatorio, "w", encoding="utf-8") as arquivo:
        saida = SaidaDuplicada(sys.stdout, arquivo)

        def imprimir_relatorio(*valores):
            print(*valores, file=saida)

        imprimir_relatorio(cabecalho)
        imprimir_relatorio("\nCENARIOS E PARAMETROS")
        for cenario in cenarios:
            imprimir_relatorio(
                f"- {cenario['nome']}: tamPop={cenario['tamPop']}, "
                f"probInversao={cenario['probInversao']}, geracoes={cenario['geracoes']}, "
                "probCruzamento=0.9 (padrao), elite=2 (padrao)"
            )
        imprimir_relatorio()

        distancias = lerDistancias(ARQUIVO_ARESTAS)
        melhor_custo_geral = float("inf")
        cenario_vencedor = ""
        dados_tabela = []

        for cenario in cenarios:
            imprimir_relatorio(f"\n[Iniciando] {cenario['nome']}...")
            custos = []
            tempos = []

            for i in range(NUMERO_DE_REPETICOES):
                inicio = time.time()
                _, custo = algoritmoGenetico(
                    distancias,
                    tamPop=cenario["tamPop"],
                    probInversao=cenario["probInversao"],
                    geracoes=cenario["geracoes"],
                    verboso=False
                )
                tempo_gasto = time.time() - inicio
                custos.append(custo)
                tempos.append(tempo_gasto)
                imprimir_relatorio(
                    f"  -> Teste {i+1}/{NUMERO_DE_REPETICOES} | "
                    f"Custo: {custo} | Tempo: {tempo_gasto:.2f}s"
                )

            melhor_custo = min(custos)
            pior_custo = max(custos)
            tempo_melhor = tempos[custos.index(melhor_custo)]
            tempo_pior = tempos[custos.index(pior_custo)]
            media_custo = sum(custos) / len(custos)
            media_tempo = sum(tempos) / len(tempos)
            erro_percentual = ((melhor_custo - OTIMO_CONHECIDO) / OTIMO_CONHECIDO) * 100

            if melhor_custo < melhor_custo_geral:
                melhor_custo_geral = melhor_custo
                cenario_vencedor = cenario["nome"]

            dados_tabela.append([
                cenario["nome"], melhor_custo, pior_custo,
                media_custo, tempo_melhor, tempo_pior, media_tempo, erro_percentual
            ])

            imprimir_relatorio(
                f"\nRESULTADOS: {cenario['nome']}\n"
                f"  - Parametros: Populacao={cenario['tamPop']}, "
                f"Inversao={cenario['probInversao']}, Geracoes={cenario['geracoes']}\n"
                f"  - Melhor Custo: {melhor_custo} (Tempo: {tempo_melhor:.2f}s)\n"
                f"  - Pior Custo:   {pior_custo} (Tempo: {tempo_pior:.2f}s)\n"
                f"  - Custo Medio:  {media_custo:.0f}\n"
                f"  - Tempo Medio:  {media_tempo:.2f}s\n"
                f"  - Gap para o Otimo: +{erro_percentual:.2f}%\n"
                "----------------------------------------------------------"
            )

        tabela = "\n" + "=" * 95 + "\n"
        tabela += (
            f"{'CENARIO':<30} | {'MELHOR':<7} | {'PIOR':<7} | {'MEDIA C.':<8} | "
            f"{'T. MELHOR':<9} | {'T. PIOR':<8} | {'T. MEDIA':<8} | {'GAP %'}\n"
        )
        tabela += "-" * 95 + "\n"

        for linha in dados_tabela:
            tabela += (
                f"{linha[0]:<30} | {linha[1]:<7} | {linha[2]:<7} | "
                f"{linha[3]:<8.0f} | {linha[4]:<8.2f}s | {linha[5]:<7.2f}s | "
                f"{linha[6]:<7.2f}s | +{linha[7]:.2f}%\n"
            )

        tabela += "=" * 95 + "\n"
        resumo_geral = (
            f"\nSINTESE GERAL\n"
            f"Melhor configuracao: {cenario_vencedor}\n"
            f"Menor custo atingido: {melhor_custo_geral} (Otimo global: {OTIMO_CONHECIDO})\n"
        )
        imprimir_relatorio(tabela + resumo_geral)


def rodar_bateria_de_testes():
    try:
        executar_bateria()
    finally:
        limpar_pycache()

if __name__ == "__main__":
    rodar_bateria_de_testes()