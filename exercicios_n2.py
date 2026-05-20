"""
Teoria da Computacao - Exercicios Praticos em Python
Sprint Planning e Otimizacao Computacional (Knapsack)

Alunos: Eder Duarte Zerek, Jose Lucas Andrade Fonseca e Sidney Cardoso de Oliveira Junior
Professor: Diogo Vinicius Winck
Materia: Algoritmos Avancado
"""

import itertools
import random
import time
from typing import Dict, List, Optional, Tuple


TAREFAS = [
    {"id": 0, "nome": "Auth OAuth2",         "custo": 8,  "valor": 40},
    {"id": 1, "nome": "Dashboard metricas",  "custo": 13, "valor": 55},
    {"id": 2, "nome": "Exportar CSV",        "custo": 5,  "valor": 20},
    {"id": 3, "nome": "Refactor servico X",  "custo": 20, "valor": 35},
    {"id": 4, "nome": "API notificacoes",    "custo": 10, "valor": 60},
    {"id": 5, "nome": "Upgrade deps",        "custo": 3,  "valor": 15},
    {"id": 6, "nome": "Testes E2E checkout", "custo": 8,  "valor": 50},
    {"id": 7, "nome": "Rate limiting",       "custo": 6,  "valor": 45},
    {"id": 8, "nome": "Docs OpenAPI",        "custo": 4,  "valor": 25},
    {"id": 9, "nome": "Cache Redis",         "custo": 12, "valor": 70},
]

CAPACIDADE = 40


def avaliar_solucao(individuo: List[int], tarefas: List[Dict], capacidade: int) -> int:
    """Retorna o valor da solucao, ou 0 se estourar a capacidade."""
    custo = sum(tarefas[i]["custo"] for i in range(len(individuo)) if individuo[i] == 1)
    valor = sum(tarefas[i]["valor"] for i in range(len(individuo)) if individuo[i] == 1)
    if custo > capacidade:
        return 0
    return valor


# -- Ex 1: Busca Exaustiva --

def busca_exaustiva(
    tarefas: List[Dict],
    capacidade: int
) -> Tuple[List[int], int]:
    """Encontra a Sprint otima testando todas as combinacoes.
    Complexidade: O(2^n) - exponencial.
    """
    n = len(tarefas)
    melhor_individuo = [0] * n
    melhor_valor = 0

    # testa todas as combinacoes possiveis (0 = nao inclui, 1 = inclui)
    for combo in itertools.product([0, 1], repeat=n):
        custo = sum(tarefas[i]["custo"] for i in range(n) if combo[i] == 1)
        valor = sum(tarefas[i]["valor"] for i in range(n) if combo[i] == 1)
        if custo <= capacidade and valor > melhor_valor:
            melhor_valor = valor
            melhor_individuo = list(combo)

    return melhor_individuo, melhor_valor


# -- Ex 2: Greedy --

def greedy_knapsack(
    tarefas: List[Dict],
    capacidade: int
) -> Tuple[List[int], int]:
    """Heuristica gulosa: ordena por ROI decrescente e adiciona tarefas.
    ROI = valor / custo (valor por Story Point).
    Complexidade: O(n log n).
    """
    n = len(tarefas)
    individuo = [0] * n
    capacidade_restante = capacidade

    # ordena pelo melhor custo-beneficio e vai adicionando enquanto cabe
    indices = sorted(
        range(n),
        key=lambda i: tarefas[i]["valor"] / tarefas[i]["custo"],
        reverse=True,
    )

    for i in indices:
        if tarefas[i]["custo"] <= capacidade_restante:
            individuo[i] = 1
            capacidade_restante -= tarefas[i]["custo"]

    valor_total = sum(tarefas[i]["valor"] for i in range(n) if individuo[i] == 1)
    return individuo, valor_total


# -- Ex 3: Analise Empirica --

def medir_complexidade(
    tamanhos: List[int],
    capacidade: int = 30,
    repeticoes: int = 3
) -> Dict[int, float]:
    """Mede o tempo medio do brute force para diferentes n."""
    resultados = {}
    for n in tamanhos:
        tempos = []
        for _ in range(repeticoes):
            tarefas_rand = [
                {"custo": random.randint(1, 10), "valor": random.randint(5, 50)}
                for _ in range(n)
            ]
            t0 = time.perf_counter()
            busca_exaustiva(tarefas_rand, capacidade)
            tempos.append((time.perf_counter() - t0) * 1000)
        resultados[n] = sum(tempos) / len(tempos)
    return resultados


def calcular_razoes_crescimento(tempos: Dict[int, float]) -> None:
    """Imprime tabela de tempos e razoes de crescimento."""
    ns = sorted(tempos.keys())
    print(f"{'n':>4} | {'Tempo (ms)':>12} | {'Razao':>8} | {'2^n':>12}")
    print("-" * 48)

    tempo_anterior = None
    for n in ns:
        tempo_atual = tempos[n]
        if tempo_anterior is None or tempo_anterior == 0:
            razao_str = "  -  "
        else:
            razao = tempo_atual / tempo_anterior
            razao_str = f"{razao:.2f}x"
        print(f"{n:>4} | {tempo_atual:>12.3f} | {razao_str:>8} | {2**n:>12}")
        tempo_anterior = tempo_atual

    print("\nConclusao: quando n sobe de 2 em 2, o tempo aproximadamente quadruplica")
    print("(razao ~4x), o que bate com o crescimento exponencial O(2^n).")


# -- Ex 4: Hill Climbing --

def gerar_vizinhos(individuo: List[int]) -> List[List[int]]:
    """Gera todos os n vizinhos (solucoes a 1 bit de distancia)."""
    vizinhos = []
    for i in range(len(individuo)):
        viz = individuo[:]
        viz[i] = 1 - viz[i]
        vizinhos.append(viz)
    return vizinhos


def hill_climbing(
    tarefas: List[Dict],
    capacidade: int,
    solucao_inicial: Optional[List[int]] = None,
    max_iter: int = 1000,
    verbose: bool = False
) -> Tuple[List[int], int, int]:
    """Busca local: melhora iterativamente trocando 1 bit por vez.
    Retorna: (melhor_individuo, melhor_valor, n_iteracoes)
    """
    if solucao_inicial is None:
        atual, _ = greedy_knapsack(tarefas, capacidade)
    else:
        atual = solucao_inicial[:]

    atual_valor = avaliar_solucao(atual, tarefas, capacidade)
    n_iter = 0

    for it in range(max_iter):
        vizinhos = gerar_vizinhos(atual)
        melhor_viz = max(vizinhos, key=lambda v: avaliar_solucao(v, tarefas, capacidade))
        melhor_viz_valor = avaliar_solucao(melhor_viz, tarefas, capacidade)

        if melhor_viz_valor > atual_valor:
            atual = melhor_viz
            atual_valor = melhor_viz_valor
            n_iter = it + 1
            if verbose:
                print(f"  iter {it+1}: novo valor = {atual_valor}")
        else:
            n_iter = it
            break

    return atual, atual_valor, n_iter


# -- Comparacao final --

def imprimir_solucao(label: str, individuo: List[int], valor: int, tarefas: List[Dict]) -> None:
    selecionadas = [tarefas[i]["nome"] for i in range(len(individuo)) if individuo[i] == 1]
    custo = sum(tarefas[i]["custo"] for i in range(len(individuo)) if individuo[i] == 1)
    print(f"\n{label}")
    print(f"  Valor total: {valor} | Custo total: {custo}/{CAPACIDADE} SP")
    print(f"  Tarefas: {selecionadas}")


def comparar_abordagens(tarefas: List[Dict], capacidade: int) -> None:
    print("=" * 60)
    print("COMPARACAO DAS ABORDAGENS")
    print("=" * 60)

    t0 = time.perf_counter()
    ind_bf, val_bf = busca_exaustiva(tarefas, capacidade)
    tempo_bf = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    ind_gr, val_gr = greedy_knapsack(tarefas, capacidade)
    tempo_gr = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    ind_hc, val_hc, iters = hill_climbing(tarefas, capacidade)
    tempo_hc = (time.perf_counter() - t0) * 1000

    imprimir_solucao(f"Brute Force (tempo: {tempo_bf:.2f} ms)", ind_bf, val_bf, tarefas)
    imprimir_solucao(f"Greedy (tempo: {tempo_gr:.2f} ms)", ind_gr, val_gr, tarefas)
    imprimir_solucao(f"Hill Climbing (tempo: {tempo_hc:.2f} ms, iter: {iters})", ind_hc, val_hc, tarefas)

    print("\n" + "-" * 60)
    print(f"Gap Greedy vs Otimo:       {val_bf - val_gr} ({(val_bf-val_gr)/val_bf*100:.1f}%)")
    print(f"Gap Hill Climbing vs Otimo: {val_bf - val_hc} ({(val_bf-val_hc)/val_bf*100:.1f}%)")


# -- Main --

def main():
    random.seed(7)

    # Exercicio 1
    print("\n" + "=" * 60)
    print("EXERCICIO 1 - Busca Exaustiva")
    print("=" * 60)
    ind, val = busca_exaustiva(TAREFAS, CAPACIDADE)
    imprimir_solucao("Resultado Brute Force:", ind, val, TAREFAS)
    assert val > 0, "Brute force deve retornar valor positivo"
    assert sum(TAREFAS[i]["custo"] for i in range(len(ind)) if ind[i] == 1) <= CAPACIDADE
    print("\nEx 1 OK")

    # Exercicio 2
    print("\n" + "=" * 60)
    print("EXERCICIO 2 - Heuristica Gulosa")
    print("=" * 60)
    ind_g, val_g = greedy_knapsack(TAREFAS, CAPACIDADE)
    imprimir_solucao("Resultado Greedy:", ind_g, val_g, TAREFAS)

    tarefas_6 = TAREFAS[:6]
    _, val_bf6 = busca_exaustiva(tarefas_6, CAPACIDADE)
    _, val_gr6 = greedy_knapsack(tarefas_6, CAPACIDADE)
    print(f"\nComparacao com n=6: Brute Force = {val_bf6} | Greedy = {val_gr6}")
    assert val_gr6 <= val_bf6, "Greedy nunca deve superar o otimo"
    print("Ex 2 OK")

    # Exercicio 3
    print("\n" + "=" * 60)
    print("EXERCICIO 3 - Analise Empirica de Complexidade")
    print("=" * 60)
    tempos = medir_complexidade([5, 8, 10, 12, 14, 16])
    calcular_razoes_crescimento(tempos)

    # desafio: comparar quanto tempo cada um leva para n=15
    tarefas_15 = [
        {"custo": random.randint(1, 10), "valor": random.randint(5, 50)}
        for _ in range(15)
    ]
    t0 = time.perf_counter()
    busca_exaustiva(tarefas_15, 30)
    t_bf15 = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    greedy_knapsack(tarefas_15, 30)
    t_gr15 = (time.perf_counter() - t0) * 1000
    print(f"\n  n=15 -> BF: {t_bf15:.2f} ms | Greedy: {t_gr15:.4f} ms")
    print("Ex 3 OK")

    # Exercicio 4
    print("\n" + "=" * 60)
    print("EXERCICIO 4 - Hill Climbing")
    print("=" * 60)

    # Teste basico gerar_vizinhos
    vizs = gerar_vizinhos([1, 0, 1])
    assert vizs == [[0, 0, 1], [1, 1, 1], [1, 0, 0]], "gerar_vizinhos errado"

    ind_hc, val_hc, iters = hill_climbing(TAREFAS, CAPACIDADE, verbose=True)
    imprimir_solucao(f"Resultado Hill Climbing ({iters} iteracoes):", ind_hc, val_hc, TAREFAS)
    assert val_hc >= val_g, "Hill Climbing deve melhorar (ou empatar) com o greedy inicial"

    # Multiplos pontos de partida
    print("\n5 pontos de partida aleatorios:")
    resultados_aleatorios = []
    for k in range(5):
        n = len(TAREFAS)
        inicial = [random.randint(0, 1) for _ in range(n)]
        _, v, it = hill_climbing(TAREFAS, CAPACIDADE, solucao_inicial=inicial)
        resultados_aleatorios.append(v)
        print(f"  Start #{k+1}: valor final = {v} ({it} iter)")
    print(f"  -> valores distintos: {sorted(set(resultados_aleatorios), reverse=True)}")
    print("  -> minimos locais confirmados quando os valores diferem.")

    # desafio: rodar 5 vezes com inicio aleatorio e ficar com o melhor
    print("\nRandom restart (5 tentativas):")
    melhor_val_rr = 0
    for _ in range(5):
        inicio = [random.randint(0, 1) for _ in range(len(TAREFAS))]
        _, v, _ = hill_climbing(TAREFAS, CAPACIDADE, solucao_inicial=inicio)
        if v > melhor_val_rr:
            melhor_val_rr = v
    print(f"  melhor valor encontrado: {melhor_val_rr}")
    print("\nEx 4 OK")

    # Debrief final
    print("\n")
    comparar_abordagens(TAREFAS, CAPACIDADE)
    print("\nFIM")


if __name__ == "__main__":
    main()
