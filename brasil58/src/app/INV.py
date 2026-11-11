import random 

def inv(individuo):
    n = len(individuo)
    ponto1, ponto2 = sorted(random.sample(range(n), 2))
    trecho = individuo[ponto1:ponto2+1]
    trecho_invertido = trecho[::-1]
    uniao_trechos = individuo[:ponto1] + trecho_invertido + individuo[ponto2+1:]
    return uniao_trechos  