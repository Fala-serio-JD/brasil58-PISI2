from custo import custoCaminho

def aptidao(rota, dicDistancias):
    resultado = custoCaminho(rota, dicDistancias)
    # DEAP exige que a aptidão seja uma tupla
    return (resultado,)