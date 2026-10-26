import random

def ox(pai1, pai2):
    # Quantidade de cidades de cada pai (vão ter o mesmo tamanho)
    n = len(pai1)

    # Sorteia duas posições diferentes e bota em ordem crescente
    ponto1, ponto2 = sorted(random.sample(range(n), 2))
    # Cria a lista filha com o mesmo tamanho 
    filho = [None] * n 

    # Recorta o trecho que vai para o filho
    trecho = pai1[ponto1:ponto2+1]
    filho[ponto1:ponto2+1] = trecho
    # Vai começar do fim do corte e dar a volta até o começo do corte
    fatia_pai2 = pai2[ponto2+1:] + pai2[:ponto2+1]
    # Guarda só quem não está no trecho retirado
    restantes = [cidade for cidade in fatia_pai2 if cidade not in trecho]

    # Preenche o filho com as cidades restantes
    for k, cidade in enumerate(restantes):
        filho[(ponto2 + 1 + k) % n] = cidade

    return filho 

if __name__ == "__main__":
    filho = ox([1,2,3,4,5,6,7,8], [3,7,5,1,6,8,2,4])
    print(filho)
    print(sorted(filho))
