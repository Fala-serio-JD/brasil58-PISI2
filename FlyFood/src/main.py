import os
import random
import sys
import time

# Garante que os pacotes do repositório (pisi2) fiquem importáveis a partir
# de qualquer diretório em que este script for chamado. Isso é necessário
# para importar os operadores do projeto irmão brasil58.
RAIZ_REPOSITORIO = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)
if RAIZ_REPOSITORIO not in sys.path:
    sys.path.insert(0, RAIZ_REPOSITORIO)

# Operadores do A.G. reaproveitados do projeto brasil58 (mesmo código).
from pisi2.brasil58.src.app.OX import ox               # cruzamento Order Crossover
from pisi2.brasil58.src.app.INV import inv             # mutação por inversão de trecho
from pisi2.brasil58.src.app.custo import custoCaminho  # custo do circuito fechado

from leitura_entrada import ler_entrada, converter_para_ag

def inicializaPopulacao(tamanho, qtdePontos):
    """Cria 'tamanho' rotas aleatórias (permutações dos nós 1..qtdePontos).

    Cada rota é uma lista com todos os nós embaralhados — para o A.G., os
    nós são "cidades" iguais às do brasil58, só que em quantidade menor.
    """
    populacao = []
    for _ in range(tamanho):
        rota = list(range(1, qtdePontos + 1))
        random.shuffle(rota)
        populacao.append(rota)
    return populacao


def calculaAptidao(populacao, dicDistancias):
    """Custo de cada rota da população, na mesma ordem (menor = melhor).

    A aptidão usa o mesmo custoCaminho do brasil58: soma das distâncias
    entre nós consecutivos + a aresta que fecha o circuito.
    """
    return [custoCaminho(rota, dicDistancias) for rota in populacao]


def torneio(populacao, aptidoes, tamanhoTorneio=3):
    """Torneio simples: sorteia k rotas e devolve a de menor custo.

    Sortear poucos indivíduos e escolher o melhor deles dá preferência às
    boas rotas sem eliminar totalmente as demais (pressão seletiva suave).
    """
    competidores = random.sample(range(len(populacao)), min(tamanhoTorneio, len(populacao)))
    vencedor = min(competidores, key=lambda indice: aptidoes[indice])
    return populacao[vencedor]


def mutacaoInversao(rota, taxaMutacao):
    """Mutação por inversão com gatilho aleatório (decisões do grupo).

    Sorteia um número entre 0.0 e 1.0: se cair acima da taxa, devolve a
    rota intacta; caso contrário, inverte um trecho aleatório da rota
    (o trecho invertido desfaz cruzamentos de arestas ineficientes).
    """
    if random.random() > taxaMutacao:
        return rota
    return inv(rota)


def algoritmoGenetico(dicDistancias, qtdePontos, tamPop=100, geracoes=200,
                      probInversao=0.3, elite=2, semente=None, verboso=True):
    """Laço evolutivo do A.G. (fluxo definido nas decisões do grupo).

    Em cada geração:
      1. avalia a população atual (calculaAptidao);
      2. atualiza o recorde global (melhor rota e menor custo já vistos);
      3. copia a elite da geração para a nova população (elitismo), o que
         garante que a melhor solução não seja destruída pela reprodução;
      4. completa a nova população com filhos: torneio (k=3) escolhe dois
         pais, o cruzamento OX gera o filho e a mutação por inversão pode
         alterá-lo.

    Retorna (melhorRota, menorCusto, geracaoRecorde).
    """
    if semente is not None:
        random.seed(semente)

    # Recordes globais: melhor rota já vista e seu custo (inicia "infinito").
    populacao = inicializaPopulacao(tamPop, qtdePontos)
    melhorRota = None
    menorCusto = float("inf")
    geracaoRecorde = 0

    def atualizarRecorde(popAtual, aptAtual, geracao):
        """Guarda a melhor rota da geração se ela bater o recorde global."""
        nonlocal melhorRota, menorCusto, geracaoRecorde
        indiceMelhor = min(range(len(popAtual)), key=lambda i: aptAtual[i])
        if aptAtual[indiceMelhor] < menorCusto:
            menorCusto = aptAtual[indiceMelhor]
            melhorRota = list(popAtual[indiceMelhor])
            geracaoRecorde = geracao

    for geracao in range(1, geracoes + 1):
        # 1) Avaliação da população atual.
        aptidoes = calculaAptidao(populacao, dicDistancias)
        atualizarRecorde(populacao, aptidoes, geracao)

        if verboso and (geracao == 1 or geracao % 50 == 0):
            print(f"Geração {geracao:4d} | melhor da geração: {min(aptidoes)} | "
                  f"recorde global: {menorCusto}")

        # 2) Elitismo: as melhores rotas passam diretamente adiante.
        ordemMerito = sorted(range(len(populacao)), key=lambda i: aptidoes[i])
        novaPopulacao = [list(populacao[i]) for i in ordemMerito[:elite]]

        # 3) Reprodução: o resto da população é preenchido com filhos.
        while len(novaPopulacao) < tamPop:
            pai1 = torneio(populacao, aptidoes)
            pai2 = torneio(populacao, aptidoes)
            filho = ox(pai1, pai2)                      # cruzamento OX
            filho = mutacaoInversao(filho, probInversao)  # mutação (com taxa)
            novaPopulacao.append(filho)

        # 4) A nova geração substitui a antiga e o ciclo se repete.
        populacao = novaPopulacao

    # A última população gerada também concorre ao recorde.
    aptidoes = calculaAptidao(populacao, dicDistancias)
    atualizarRecorde(populacao, aptidoes, geracoes)

    return melhorRota, menorCusto, geracaoRecorde

def formatar_trajeto(rota, legenda):
    """Traduz a rota do A.G. para o trajeto começando em R.

    A rota é um circuito (lista de nós); giramos o circuito para começar
    no nó 1 (que sempre é o R) e acrescentamos o retorno ao fim:
    'R -> A -> D -> C -> B -> R'. O custo não muda com o giro.
    """
    posicaoOrigem = rota.index(1)                 # posição do nó 1 (R)
    ciclo = rota[posicaoOrigem:] + rota[:posicaoOrigem]
    rotulos = [legenda[no] for no in ciclo] + [legenda[1]]  # volta ao R
    return " -> ".join(rotulos)


def resolver_caminho_matriz(caminho):
    """Aceita caminhos relativos ao diretório atual ou ao projeto FlyFood.

    Permite chamar 'python src/main.py', 'python src/main.py matriz5.txt'
    ou 'python src/main.py entradas/matriz5.txt' de qualquer pasta.
    """
    raizFlyfood = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    alternativas = [
        caminho,
        os.path.join(raizFlyfood, caminho),
        os.path.join(raizFlyfood, "entradas", caminho),
    ]
    for alternativa in alternativas:
        if os.path.exists(alternativa):
            return alternativa
    return None


def main(caminhoMatriz=None, **parametrosAG):
    """Resolve UMA instância do FlyFood com o A.G. e imprime o resultado.

    parametrosAG aceita os mesmos argumentos nomeados de algoritmoGenetico
    (tamPop, geracoes, probInversao, elite, semente...), permitindo calibrar
    a execução sem alterar o código.
    """
    if caminhoMatriz is None:
        caminhoMatriz = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "entradas", "matriz1.txt")
    caminhoResolvido = resolver_caminho_matriz(caminhoMatriz)
    if caminhoResolvido is None:
        print(f"Matriz não encontrada: {caminhoMatriz}")
        return None

    # 1) Leitura da matriz e conversão para o formato do A.G.
    locais, pontosEntrega = ler_entrada(caminhoResolvido)
    if locais is None:
        return None
    dicDistancias, legenda = converter_para_ag(locais, pontosEntrega)

    # 2) Execução do Algoritmo Genético.
    inicio = time.time()
    melhorRota, custo, geracaoRecorde = algoritmoGenetico(
        dicDistancias, len(legenda), **parametrosAG
    )
    tempo = time.time() - inicio

    # 3) Apresentação do resultado (trajeto girado para começar no R).
    print(f"Matriz: {os.path.basename(caminhoResolvido)} "
          f"({len(pontosEntrega)} pontos de entrega)")
    print(f"Melhor trajeto: {formatar_trajeto(melhorRota, legenda)}")
    print(f"Distância total: {custo} dronômetros")
    print(f"Recorde alcançado na geração {geracaoRecorde}")
    print(f"Tempo de execução: {tempo:.4f} s")
    return melhorRota, custo


if __name__ == "__main__":
    # Aceita uma matriz pela linha de comando; se não vier nenhuma, usa a matriz1.
    matriz = sys.argv[1] if len(sys.argv) > 1 else None
    main(matriz)
