# FlyFood

Projeto da disciplina PISI2 — Desenvolvimento de um algoritmo de roteamento para entregas com drones.

## Contexto

No ano de 2030, o trânsito está caótico e as empresas de delivery não conseguem mais fazer entregas em um tempo aceitável. Um ex-aluno do BSI-UFRPE cria a empresa **FlyFood**, que realiza entregas utilizando drones.

Os drones podem sair do local de origem do pedido com vários pedidos no compartimento de carga e entregá-los em vários endereços espalhados pela cidade. Porém, a capacidade das baterias ainda é um problema, então é preciso otimizar ao máximo o trajeto do drone para concluir todas as entregas dentro do ciclo da bateria.

O objetivo é elaborar um **algoritmo de roteamento**: um algoritmo capaz de definir o menor trajeto para a realização de todas as entregas do drone.

## Modelagem

Para abstrair as questões de encontrar endereços e obter coordenadas GPS, o problema utiliza uma **matriz** que representa os pontos da cidade:

- O ponto R é considerado, por convenção, a **origem** e o **retorno**, sendo representado pela coord. (0, 0).
- Cada ponto de entrega é identificado por uma letra ('A', 'B', 'C', 'D', ...).

O drone **não anda na diagonal** — ele só percorre a matriz na horizontal ou na vertical. A distância é medida em **dronômetros**.

## Formato de entrada

O arquivo de entrada segue o formato texto abaixo: a primeira linha traz a quantidade de linhas e colunas da matriz, e as linhas seguintes representam a matriz em si, com "0" indicando posições vazias. Exemplo (entradas/matriz1.txt):

```text
4 5
0 0 0 0 D
0 A 0 0 0
0 0 0 0 C
R 0 B 0 0
```


## Solução atual: Algoritmo Genético (A.G.)

Este projeto era originalmente resolvido por permutação pura (força bruta e busca com poda), conforme o relatório da 1ª VA ("FlyFood — abordagem permutativa"). A solução atual substitui a permutação por um **Algoritmo Genético**, o mesmo tipo de solução adotada no projeto irmão `brasil58` (arquivo `brazil58.tsp`):

- **Operadores reaproveitados do brasil58**: cruzamento OX (`OX.py`), mutação por inversão (`INV.py`) e cálculo do custo do circuito (`custo.py`);
- **Conversão de dados** (`converter_para_ag` em `src/leitura_entrada.py`): transforma a matriz do FlyFood no mesmo formato consumido pelo A.G. do brasil58 — um dicionário de distâncias `{(i, j): peso}`, em que o ponto `R` vira o nó 1 e os pontos de entrega viram os nós 2, 3, ...;
- **Laço evolutivo em Python puro** (sem dependências externas), conforme as decisões do grupo: avaliação → recorde global → elitismo → torneio (k=3) → cruzamento OX → mutação por inversão.

## Saída esperada

src/main.py — **Algoritmo Genético**:

```text
Melhor trajeto: R -> A -> D -> C -> B -> R
Distância total: 14 dronômetros
Recorde alcançado na geração 1
Tempo de execução: 0.0123 s
```

Também é possível passar outra matriz pela linha de comando (`python src/main.py matriz5.txt` — o nome é resolvido na pasta `entradas`).

## Estrutura do projeto

```text
FlyFood/
├── entradas/
│   ├── matriz1.txt      (4 pontos de entrega)
│   ├── matriz2.txt      (6 pontos de entrega)
│   ├── matriz3.txt      (8 pontos de entrega)
│   ├── matriz4.txt      (10 pontos de entrega)
│   └── matriz5.txt      (12 pontos de entrega)
├── src/
│   ├── leitura_entrada.py   # leitura da matriz + conversão para o formato do A.G.
│   ├── main.py              # Algoritmo Genético (A.G.) — roteamento das entregas
│   └── testes/
│       ├── automação_teste.py   # bateria de testes (mesmo padrão do brasil58)
│       └── relatórios/          # saídas automáticas dos testes (.txt)
├── .gitignore
└── README.md
```


## Como rodar o projeto 

**Pré-requisito**: ter o Python 3 instalado. O FlyFood não usa bibliotecas externas — mas, como ele importa os operadores do projeto irmão `brasil58`, ambos devem estar lado a lado na mesma pasta raiz (como ocorre neste repositório `pisi2`).

1. Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/RichardCarmo/FlyFood.git
cd FlyFood
``` 

2. Rodando o Algoritmo Genético (src/main.py), com a matriz1 por padrão:

```bash
python src/main.py
```

3. Rodando com outra matriz (opcional):

```bash
python src/main.py matriz5.txt
```

4. Rodando a bateria de testes automatizada (gera relatórios em `src/testes/relatórios/`):

```bash
python src/testes/automação_teste.py
```