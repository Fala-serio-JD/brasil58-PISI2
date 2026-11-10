import os
import random
import time

from deap import base, creator, tools, algorithms

from INV import inv
from OX import ox

QTDE_CIDADES = 58
ARQUIVO_ARESTAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "docs", "edgesbrasil58.tsp"
)

def lerDistancias(caminho, qtdeCidades=QTDE_CIDADES):
    """Lê a matriz triangular superior e devolve o dicionário (i, j) -> peso."""
    distancias = {}
    with open(caminho) as arq:
        for i in range(1, qtdeCidades):
            lista = arq.readline().split()
            if len(lista) < qtdeCidades - i:
                print(f"Erro! linha {i} do arquivo não possui elementos suficientes")
                exit()
            for j in range(i + 1, qtdeCidades + 1):
                peso = int(lista.pop(0))
                distancias[(i, j)] = peso
                distancias[(j, i)] = peso
    return distancias

def custoCaminho(permutacao, dicDistancias):
    """Custo total do ciclo: soma pares consecutivos e retorno ao primeiro nó."""
    soma = 0
    for i in range(len(permutacao) - 1):
        a = permutacao[i]
        b = permutacao[i + 1]
        if (a, b) in dicDistancias:
            soma += dicDistancias[(a, b)]
        else:
            print(f"Erro! ({a},{b}) não existe no dicionario!")
            exit()
    soma += dicDistancias[(permutacao[-1], permutacao[0])]
    return soma


def inicializaPopulacao(tamanho, qtdeCidades):
    """Cria 'tamanho' permutações aleatórias de 1..qtdeCidades."""
    populacao = []
    for _ in range(tamanho):
        individuo = list(range(1, qtdeCidades + 1))
        random.shuffle(individuo)
        populacao.append(individuo)
    return populacao


def calculaAptidao(populacao, dicDistancias):
    """Lista de custos na mesma ordem da população."""
    return [custoCaminho(individuo, dicDistancias) for individuo in populacao]


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individuo", list, fitness=creator.FitnessMin)


def cruzamentoOX(ind1, ind2):
    """Adapta o OX do projeto ao DEAP (modifica os pais in-place)."""
    filho1 = ox(list(ind1), list(ind2))
    filho2 = ox(list(ind2), list(ind1))
    ind1[:] = filho1
    ind2[:] = filho2
    return ind1, ind2


def montaToolbox(dicDistancias, tamTorneio=3, tentativasInversao=20):
    toolbox = base.Toolbox()

    toolbox.register("populacao", lambda n: [
        creator.Individuo(ind) for ind in inicializaPopulacao(n, QTDE_CIDADES)
    ])

    toolbox.register("evaluate", lambda ind: (custoCaminho(ind, dicDistancias),))

    def mutacaoInversao(individuo):
        """
        Inversão com aceitação gulosa: sorteia trechos via inv() e só
        mantém a inversão se o custo diminuir (equivale a um 2-opt
        aleatório). Modifica o indivíduo in-place.
        """
        custo = custoCaminho(individuo, dicDistancias)
        for _ in range(tentativasInversao):
            candidato = inv(list(individuo))
            novoCusto = custoCaminho(candidato, dicDistancias)
            if novoCusto < custo:
                individuo[:] = candidato
                custo = novoCusto
        return (individuo,)

    toolbox.register("mate", cruzamentoOX)
    toolbox.register("mutate", mutacaoInversao)
    toolbox.register("select", tools.selTournament, tournsize=tamTorneio)
    return toolbox


def avalia(toolbox, individuos):
    """Avalia somente quem ainda não tem aptidão válida."""
    invalidos = [ind for ind in individuos if not ind.fitness.valid]
    for ind, fit in zip(invalidos, map(toolbox.evaluate, invalidos)):
        ind.fitness.values = fit


def algoritmoGenetico(dicDistancias, tamPop=200, geracoes=600,
                      probCruzamento=0.6, probInversao=0.4, elite=2,
                      semente=None, verboso=True):
    """
    Loop evolutivo com DEAP: varOr gera os filhos (cruzamento OX ou
    mutação por INVERSÃO), com elitismo e seleção por torneio.
    probCruzamento + probInversao <= 1.
    """
    if semente is not None:
        random.seed(semente)

    toolbox = montaToolbox(dicDistancias)
    populacao = toolbox.populacao(tamPop)
    avalia(toolbox, populacao)

    hof = tools.HallOfFame(1)
    hof.update(populacao)
    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", min)
    stats.register("media", lambda v: sum(v) / len(v))

    for g in range(1, geracoes + 1):
        filhos = algorithms.varOr(populacao, toolbox, tamPop,
                                  probCruzamento, probInversao)
        avalia(toolbox, filhos)

        conjunto = list({tuple(ind): ind for ind in populacao + filhos}.values())
        while len(conjunto) < tamPop:
            novo = creator.Individuo(inicializaPopulacao(1, QTDE_CIDADES)[0])
            novo.fitness.values = toolbox.evaluate(novo)
            conjunto.append(novo)
        novaPop = tools.selBest(conjunto, elite)
        novaPop += toolbox.select(conjunto, tamPop - elite)
        populacao = [creator.Individuo(ind) for ind in novaPop]
        for novo, velho in zip(populacao, novaPop):
            novo.fitness.values = velho.fitness.values

        hof.update(populacao)
        if verboso and (g == 1 or g % 50 == 0):
            reg = stats.compile(populacao)
            print(f"Geração {g:5d} | melhor: {hof[0].fitness.values[0]:.0f} | "
                  f"média: {reg['media']:.0f}")

    melhor = hof[0]
    return list(melhor), melhor.fitness.values[0]


def main():
    distancias = lerDistancias(ARQUIVO_ARESTAS)
    inicio = time.time()
    rota, custo = algoritmoGenetico(distancias)
    tempo = time.time() - inicio

    print("\nMelhor rota:", rota)
    print("Custo total:", custo, "(ótimo conhecido: 25395)")
    print(f"Tempo: {tempo:.2f} s")


if __name__ == "__main__":
    main()