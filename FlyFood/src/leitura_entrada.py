# ==========================================================================
# Leitura e conversão das entradas do FlyFood
# ==========================================================================
# Este módulo tem duas responsabilidades:
#
#   1. ler_entrada:        lê o arquivo da matriz e devolve os pontos;
#   2. converter_para_ag:  converte esses pontos para o MESMO formato de
#                          dados usado pelo Algoritmo Genético (A.G.) do
#                          projeto brasil58 — um dicionário de distâncias
#                          no formato {(i, j): peso}.
#
# Com essa conversão, o A.G. consegue consumir as instâncias do FlyFood
# sem nenhuma alteração: para o algoritmo, cada ponto da matriz (R, A, B,
# C, ...) vira uma "cidade" numerada, exatamente como as 58 cidades do
# arquivo brazil58.tsp.


# Lê o arquivo da matriz e devolve os pontos
def ler_entrada(caminho_arquivo):
        try:
            # Abre o arquivo para leitura e o fecha automaticamante
            with open(caminho_arquivo, "r", encoding="utf-8") as f:

                # Leitura da linha do arquivo, remoção de espaços e converção para inteiro
                primeira_linha = f.readline()
                limpeza_espacos = primeira_linha.strip() 
                lista_linha_coluna = limpeza_espacos.split()
                qtd_linhas = int(lista_linha_coluna[0])
                qtd_colunas = int(lista_linha_coluna[1]) 

                # Criação do dicionário 
                locais = {}

                # Percorre as linhas restantes do arquivo e obtém o índice 
                for indice1, linha in enumerate(f):
                    limpeza_espacos2 = linha.strip()
                    lista_linhas_restantes = limpeza_espacos2.split()

                    # Obtém o índice das colunas
                    for indice2, i in enumerate(lista_linhas_restantes):
                        if i == "0":
                            pass
                        else:
                            locais[i] = (indice1, indice2)

                # Criação da lista sem o ponto de origem "R"
                lista_chaves = [chave for chave in locais if chave != "R"] 

                # Retorna todas as coordenadas e a lista dos pontos de entrega
                return locais, lista_chaves

        except FileNotFoundError:
            print("O arquivo solicitado não foi encontrado.")
            locais = lista_chaves = None
            return locais, lista_chaves


def distancia_manhattan(ponto_a, ponto_b):
    """Distância Manhattan entre dois pontos (linha, coluna) da matriz.

    O drone só anda na horizontal e na vertical, então a distância entre
    dois pontos é a soma dos deslocamentos em cada eixo (sem diagonais).
    """
    (linha_a, coluna_a), (linha_b, coluna_b) = ponto_a, ponto_b
    return abs(linha_a - linha_b) + abs(coluna_a - coluna_b)


def converter_para_ag(locais, pontos_de_entrega):
    """Converte os pontos da matriz FlyFood para o formato usado pelo A.G.

    O A.G. do brasil58 trabalha com dois dados:
      * um dicionário de distâncias no formato {(i, j): peso}, em que i e
        j são números inteiros que identificam as cidades (1 a 58 lá);
      * a quantidade de cidades.

    A conversão funciona assim:
      * o ponto 'R' (origem e retorno do drone) vira o nó 1;
      * os pontos de entrega, em ordem alfabética, viram os nós 2, 3, ...;
      * a distância entre cada par de nós é a distância Manhattan entre
        as coordenadas originais dos pontos na matriz.

    Como o trajeto do drone parte de R, visita todos os pontos de entrega
    e volta a R, ele é exatamente um CIRCUITO fechado passando por todos
    os nós — o mesmo problema que o A.G. resolve para as cidades do
    brazil58.tsp. O custo de um circuito não muda se ele for "girado"
    para começar em outro nó, então basta apresentar o circuito
    encontrado pelo A.G. começando pelo nó 1 (o R).

    Retorna:
      * dicDistancias: dicionário {(i, j): distancia} com todos os pares
        de nós (nos dois sentidos, pois a distância é simétrica — o mesmo
        padrão do lerDistancias do brasil58);
      * legenda: dicionário {numero_do_no: rotulo_original}, usado para
        traduzir a resposta do A.G. de volta aos nomes dos pontos (R, A,
        B, C, ...).
    """
    if "R" not in locais:
        raise ValueError("A matriz precisa conter o ponto 'R' (origem do drone).")

    # O nó 1 é sempre o R; os pontos de entrega seguem em ordem alfabética.
    rotulos = ["R"] + sorted(pontos_de_entrega)
    legenda = {numero: rotulo for numero, rotulo in enumerate(rotulos, start=1)}

    # Calcula a distância Manhattan entre todos os pares de nós.
    dicDistancias = {}
    for i in range(1, len(rotulos) + 1):
        for j in range(i + 1, len(rotulos) + 1):
            peso = distancia_manhattan(locais[legenda[i]], locais[legenda[j]])
            dicDistancias[(i, j)] = peso
            dicDistancias[(j, i)] = peso

    return dicDistancias, legenda