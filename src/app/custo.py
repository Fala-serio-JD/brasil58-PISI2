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