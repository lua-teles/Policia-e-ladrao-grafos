"""Algoritmos de caminho minimo, conectividade e fluxo maximo/min-cut."""

from __future__ import annotations

from collections import deque

INF = float("inf")
CAP_INF = 10**9


def bellman_ford(
    adj: list[list[tuple[int, float]]],
    n: int,
    fonte: int,
    bloqueados: set[int] | None = None,
) -> tuple[list[float], list[int]]:
    bloqueados = bloqueados or set()
    dist = [INF] * n
    pred = [-1] * n
    dist[fonte] = 0.0

    for _ in range(n - 1):
        atualizado = False
        for u in range(n):
            if dist[u] == INF:
                continue
            if u in bloqueados and u != fonte:
                continue
            base = dist[u]
            for v, w in adj[u]:
                if v in bloqueados:
                    continue
                nd = base + w
                if nd < dist[v]:
                    dist[v] = nd
                    pred[v] = u
                    atualizado = True
        if not atualizado:
            break

    return dist, pred


def tem_ciclo_negativo(
    adj: list[list[tuple[int, float]]],
    n: int,
    fonte: int,
) -> bool:
    dist, _ = bellman_ford(adj, n, fonte)
    for u in range(n):
        if dist[u] == INF:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                return True
    return False


def tem_ciclo_negativo_global(
    adj: list[list[tuple[int, float]]],
    n: int,
) -> bool:
    # Equivale a adicionar uma superfonte com arestas de peso 0 para todos os vértices.
    dist = [0.0] * n

    for _ in range(n - 1):
        atualizado = False
        for u in range(n):
            base = dist[u]
            for v, w in adj[u]:
                nd = base + w
                if nd < dist[v]:
                    dist[v] = nd
                    atualizado = True
        if not atualizado:
            break

    for u in range(n):
        base = dist[u]
        for v, w in adj[u]:
            if base + w < dist[v]:
                return True

    return False


def reconstruir_caminho(pred: list[int], fonte: int, destino: int) -> list[int]:
    caminho = []
    atual = destino

    while atual != -1:
        caminho.append(atual)
        if atual == fonte:
            break
        atual = pred[atual]

    if not caminho or caminho[-1] != fonte:
        return []

    caminho.reverse()
    return caminho


def proximo_vertice(pred: list[int], fonte: int, destino: int) -> int | None:
    caminho = reconstruir_caminho(pred, fonte, destino)
    if len(caminho) < 2:
        return None
    return caminho[1]


def bfs_alcancaveis(
    adj: list[list[tuple[int, float]]],
    fonte: int,
) -> set[int]:
    visitados: set[int] = {fonte}
    fila = deque([fonte])

    while fila:
        u = fila.popleft()
        for v, _ in adj[u]:
            if v not in visitados:
                visitados.add(v)
                fila.append(v)

    return visitados


def construir_rede_fluxo(
    g,
    castelo: int,
    portos_alcancaveis: list[int],
) -> tuple[list[list[int]], int, int]:
    n_rede = 2 * g.n + 1
    t_estrela = n_rede - 1
    cap = [[0] * n_rede for _ in range(n_rede)]

    for v in range(g.n):
        v_in, v_out = 2 * v, 2 * v + 1
        cap[v_in][v_out] = CAP_INF if v == castelo else 1

    for u in range(g.n):
        u_out = 2 * u + 1
        for v, _ in g.adj[u]:
            v_in = 2 * v
            cap[u_out][v_in] = CAP_INF

    for p in portos_alcancaveis:
        p_out = 2 * p + 1
        cap[p_out][t_estrela] = CAP_INF

    return cap, n_rede, t_estrela


def _bfs_rede_residual(
    cap: list[list[int]],
    n: int,
    fonte: int,
    sorvedouro: int,
) -> list[int]:
    pai = [-1] * n
    visitado = [False] * n
    visitado[fonte] = True

    fila = deque([fonte])
    while fila and not visitado[sorvedouro]:
        u = fila.popleft()
        for v in range(n):
            if not visitado[v] and cap[u][v] > 0:
                visitado[v] = True
                pai[v] = u
                fila.append(v)

    return pai


def edmonds_karp(
    cap: list[list[int]],
    n: int,
    fonte: int,
    sorvedouro: int,
) -> tuple[int, list[list[int]]]:
    fluxo_total = 0

    while True:
        pai = _bfs_rede_residual(cap, n, fonte, sorvedouro)
        if pai[sorvedouro] == -1:
            break

        gargalo = CAP_INF
        v = sorvedouro
        while v != fonte:
            u = pai[v]
            gargalo = min(gargalo, cap[u][v])
            v = u

        v = sorvedouro
        while v != fonte:
            u = pai[v]
            cap[u][v] -= gargalo
            cap[v][u] += gargalo
            v = u

        fluxo_total += gargalo

    return fluxo_total, cap


def vertices_do_corte(
    cap_residual: list[list[int]],
    n: int,
    fonte: int,
    g,
) -> list[int]:
    alcancaveis: set[int] = {fonte}
    fila = deque([fonte])

    while fila:
        u = fila.popleft()
        for v in range(n):
            if v not in alcancaveis and cap_residual[u][v] > 0:
                alcancaveis.add(v)
                fila.append(v)

    corte = []
    for v in range(g.n):
        v_in, v_out = 2 * v, 2 * v + 1
        if v_in in alcancaveis and v_out not in alcancaveis:
            corte.append(v)

    return corte
