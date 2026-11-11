#from file import *

objArq = open("edgesbrasil58.tsp")
#se você quiser uma lista onde cada objeto será uma string
#grande representando uma linha do arquivo:
#listaLinhas = objArq.readlines() #obs: cada linha terah um enter junto com o ultimo elemento

distancias = {}

for i in range(1, 58): #linhas 1 a 57 pois a 58 nao terá aresta
	linha = objArq.readline() #le só uma linha do arquivo
	#transformando a linha em lista de strings:
	lista = linha.split() #obs: lista de strings (não int)

	for j in range(i+1, 59): #colunas i+1 a 58
		if len(lista) > 0:
			peso = int(lista.pop(0)) #obs: peso int, poderia ser float em outro problema
		else:
			print(f"Erro! linha {i} do arquivo não possui elementos suficientes")
			exit()
		#gravando a aresta em (i, j) e (j, i):
		distancias[(i,j)] = peso
		distancias[(j,i)] = peso
objArq.close()

#funcao que retorna o custo total do caminho:
def custoCaminho(permutacao, dicDistancias):
	#ex: permutacao = [5, 14, 2, 3, 7, ...]
	soma = 0
	for i in range(len(permutacao)-1):
		a = permutacao[i]
		b = permutacao[i+1]
		if (a,b) in dicDistancias:
			soma += dicDistancias[(a,b)]
		else:
			print(f"Erro! ({a},{b}) não existe no dicionario!")
			exit()
	soma += dicDistancias[(permutacao[-1],permutacao[0])]
	return soma
	
def inicializaPopulacao(tamanho, qtdeCidades):
	import random
	#criando uma lista com "tamanho" permutacoes aleatorias de cidades:
	lista = []
	for i in range(tamanho):
		individuo = list(range(1, qtdeCidades+1))
		random.shuffle(individuo)
		lista.append(individuo)
	return lista

def calculaAptidao(populacao, dicDistancias):
	listaAptidao = []
	for elem in populacao:
		listaAptidao.append(custoCaminho(elem, dicDistancias))
	return listaAptidao

		
	
