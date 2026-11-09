import os
import random
import time

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
    """Custo total do ciclo: soma pares consecutivos + retorno ao primeiro nó."""
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

def torneio(populacao, custos, k=3):
    """Seleciona o melhor (menor custo) entre k indivíduos sorteados."""
    candidatos = random.sample(range(len(populacao)), k)
    melhor = min(candidatos, key=lambda idx: custos[idx])
    return populacao[melhor]


def algoritmoGenetico(dicDistancias, tamPop=100, geracoes=2000,
                      probCruzamento=0.9, probInversao=0.3, elite=2,
                      semente=None, verboso=True):
    if semente is not None:
        random.seed(semente)

    populacao = inicializaPopulacao(tamPop, QTDE_CIDADES)
    custos = calculaAptidao(populacao, dicDistancias)

    melhorCusto = min(custos)
    melhorRota = populacao[custos.index(melhorCusto)][:]

    for g in range(1, geracoes + 1):
        ordem = sorted(range(tamPop), key=lambda idx: custos[idx])
        novaPop = [populacao[idx][:] for idx in ordem[:elite]]

        while len(novaPop) < tamPop:
            pai1 = torneio(populacao, custos)
            pai2 = torneio(populacao, custos)

            filho = ox(pai1, pai2) if random.random() < probCruzamento else pai1[:]

            if random.random() < probInversao:
                filho = inv(filho)

            novaPop.append(filho)

        populacao = novaPop
        custos = calculaAptidao(populacao, dicDistancias)

        custoGeracao = min(custos)
        if custoGeracao < melhorCusto:
            melhorCusto = custoGeracao
            melhorRota = populacao[custos.index(custoGeracao)][:]

        if verboso and (g % 100 == 0 or g == 1):
            print(f"Geração {g:5d} | melhor: {melhorCusto} | "
                  f"média: {sum(custos) / len(custos):.0f}")

    return melhorRota, melhorCusto


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