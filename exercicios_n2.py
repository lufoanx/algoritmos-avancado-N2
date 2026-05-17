"""
Teoria da Computacao - Exercicios Praticos em Python
Sprint Planning e Otimizacao Computacional (Knapsack)

Alunos: Jose Lucas Andrade Fonseca e Sidney Cardoso de Oliveira Junior
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


# ---------------------------------------------------------------------------
# Exercicio 1 - Busca Exaustiva (Brute Force)
# ---------------------------------------------------------------------------

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

    for combo in itertools.product([0, 1], repeat=n):
        custo = sum(tarefas[i]["custo"] for i in range(n) if combo[i] == 1)
        valor = sum(tarefas[i]["valor"] for i in range(n) if combo[i] == 1)
        if custo <= capacidade and valor > melhor_valor:
            melhor_valor = valor
            melhor_individuo = list(combo)

    return melhor_individuo, melhor_valor


# ---------------------------------------------------------------------------
# Exercicio 2 - Heuristica Gulosa (Greedy)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Exercicio 3 - Analise Empirica de Complexidade
# ---------------------------------------------------------------------------

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

    print("\nConclusao: a razao tende a ~4x quando n cresce de 2 em 2,")
    print("pois 2^(n+2) / 2^n = 4. Isso confirma o crescimento O(2^n).")


# ---------------------------------------------------------------------------
# Exercicio 4 - Hill Climbing (Busca Local)
# ---------------------------------------------------------------------------

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


def hill_climbing_random_restart(
    tarefas: List[Dict],
    capacidade: int,
    n_restarts: int = 5,
    max_iter: int = 1000
) -> Tuple[List[int], int]:
    """Hill Climbing com varios pontos de partida aleatorios."""
    n = len(tarefas)
    melhor_ind = [0] * n
    melhor_val = 0

    for _ in range(n_restarts):
        inicial = [random.randint(0, 1) for _ in range(n)]
        ind, val, _ = hill_climbing(tarefas, capacidade, solucao_inicial=inicial, max_iter=max_iter)
        if val > melhor_val:
            melhor_val = val
            melhor_ind = ind

    return melhor_ind, melhor_val


# ---------------------------------------------------------------------------
# Comparacao das abordagens
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main: testes e execucao
# ---------------------------------------------------------------------------

def main():
    random.seed(42)

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

    # Desafio Ex3: comparar greedy vs brute force para n=15
    print("\nDesafio - Greedy vs Brute Force para n=15:")
    tarefas_15 = [
        {"custo": random.randint(1, 10), "valor": random.randint(5, 50)}
        for _ in range(15)
    ]
    t0 = time.perf_counter()
    busca_exaustiva(tarefas_15, 30)
    t_bf = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    greedy_knapsack(tarefas_15, 30)
    t_gr = (time.perf_counter() - t0) * 1000
    print(f"  Brute Force: {t_bf:.2f} ms | Greedy: {t_gr:.4f} ms")
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

    # Desafio: random restart
    print("\nDesafio - Hill Climbing com random restart (n_restarts=5):")
    _, val_rr = hill_climbing_random_restart(TAREFAS, CAPACIDADE, n_restarts=5)
    print(f"  Valor com restart: {val_rr}")

    print("\nEx 4 OK")

    # Debrief final
    print("\n")
    comparar_abordagens(TAREFAS, CAPACIDADE)
    print("\nFIM")


if __name__ == "__main__":
    main()
