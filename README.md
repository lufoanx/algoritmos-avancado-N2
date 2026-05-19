# Algoritmos Avancado - Teoria computacional

Exercicios praticos da disciplina **Algoritmos Avancado** sobre Teoria da Computacao: Sprint Planning como problema do Knapsack.

## Alunos
- Jose Lucas Andrade Fonseca
- Sidney Cardoso de Oliveira Junior

## Professor
- Diogo Vinicius Winck

## Sobre

O projeto implementa 4 abordagens diferentes para resolver o problema da mochila (Knapsack) aplicado ao planejamento de sprint:

1. **Busca Exaustiva (Brute Force)** - O(2^n), garante o otimo mas nao escala.
2. **Heuristica Gulosa (Greedy)** - O(n log n), rapida mas pode perder valor.
3. **Analise Empirica de Complexidade** - mede a explosao exponencial.
4. **Hill Climbing (Busca Local)** - melhora o greedy mas fica preso em minimos locais.

## Como executar

Requer apenas Python 3.8+ (so usa biblioteca padrao).

```bash
python exercicios_n2.py
```

A execucao roda todos os 4 exercicios em sequencia, com os asserts e a comparacao final entre as abordagens.

## Estrutura

```
.
├── exercicios_n2.py   # Arquivo unico com todas as funcoes e o main
└── README.md
```

## Resultados observados

- **Ex 1 e 2**: para o conjunto de 10 tarefas do enunciado, Brute Force e Greedy chegam ao mesmo valor otimo (250 pontos de ROI, custo 40/40 SP).
- **Ex 3**: a razao de crescimento do tempo entre `n` e `n+2` se estabiliza em ~4x, confirmando O(2^n).
- **Ex 4**: com 5 pontos de partida aleatorios os valores finais ficaram diferentes (ex: 235, 215, 210), mostrando que o hill climbing trava em solucoes diferentes dependendo de onde começa. O random restart ajudou a encontrar um valor melhor.

## Conclusao

Na pratica da pra ver que nenhuma das tres abordagens resolve bem quando o problema cresce. O brute force trava rapido, greedy e hill climbing dao resultados diferentes dependendo da instancia. Faz sentido estudar algo mais robusto na proxima aula.
