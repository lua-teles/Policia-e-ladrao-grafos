"""Ponto de entrada do sistema de captura do ladrao."""

from __future__ import annotations

import sys

from algoritmos import (
    bfs_alcancaveis,
    construir_rede_fluxo,
    edmonds_karp,
    tem_ciclo_negativo_global,
    vertices_do_corte,
)
from grafo import ler_entrada
from relatorio import gerar_relatorio
from simulacao import simular


def _foi_capturado(status: str) -> bool:
    return status.startswith("PRESO")


def _resultado_sem_porto(castelo: int, equipes: list[int]) -> dict:
    return {
        "status": "PRESO_SEM_PORTO_ALCANCAVEL",
        "rodadas": 0,
        "caminho_ladrao": [castelo],
        "caminhos_equipes": {i: [pos] for i, pos in enumerate(equipes)},
        "estrategia": "estrutura do grafo",
        "equipes_necessarias": 0,
    }


def _calcular_corte_minimo(g, castelo: int, portos_validos: list[int]) -> tuple[int, list[int]]:
    cap, n_rede, t_estrela = construir_rede_fluxo(g, castelo, portos_validos)
    fonte_fluxo = 2 * castelo + 1
    k_minimo, residual = edmonds_karp(cap, n_rede, fonte_fluxo, t_estrela)
    corte = vertices_do_corte(residual, n_rede, fonte_fluxo, g)
    return k_minimo, corte


def _simular_estrategia(
    g,
    castelo: int,
    portos_validos: list[int],
    equipes: list[int],
    estrategia: str,
    equipes_disponiveis: int,
    tentativa_inicial: dict | None = None,
) -> dict:
    resultado = simular(g, castelo, portos_validos, equipes)
    resultado["estrategia"] = estrategia
    resultado["equipes_necessarias"] = len(equipes)
    resultado["equipes_adicionais"] = max(0, len(equipes) - equipes_disponiveis)
    if tentativa_inicial is not None:
        resultado["tentativa_inicial"] = tentativa_inicial
    return resultado


def _formatar_adjacencias(g) -> list[str]:
    linhas = []
    for u in range(g.n):
        destinos = [f"{v}({w:g})" for v, w in g.adj[u]]
        descricao = ", ".join(destinos) if destinos else "sem saida"
        linhas.append(f"{u}: {descricao}")
    return linhas


def _formatar_equipes_iniciais(equipes: list[int]) -> str:
    if not equipes:
        return "nenhuma equipe"
    return ", ".join(
        f"equipe {indice} em {posicao}"
        for indice, posicao in enumerate(equipes)
    )


def _imprimir_contexto_inicial(
    g,
    castelo: int,
    portos: list[int],
    equipes: list[int],
) -> None:
    print("=" * 60)
    print("CENARIO DE ENTRADA")
    print("=" * 60)
    print(f"Vertices: {g.n}")
    print(f"Castelo: {castelo}")
    print(f"Portos: {portos}")
    print(f"Equipes iniciais: {_formatar_equipes_iniciais(equipes)}")
    print("Grafo:")
    for linha in _formatar_adjacencias(g):
        print(f"  {linha}")
    print("")


def _imprimir_simulacao(res: dict) -> None:
    print("=" * 60)
    print(f"SIMULACAO: {res.get('estrategia', 'nao informada').upper()}")
    print("=" * 60)
    for evento in res.get("eventos", []):
        print(evento)
    print("")


def main(caminho_entrada: str, caminho_saida: str | None = None) -> int:
    try:
        entrada = ler_entrada(caminho_entrada)
    except Exception as exc:
        print(f"ERRO ao ler entrada: {exc}")
        return 1

    g = entrada.grafo
    castelo = entrada.castelo
    portos = entrada.portos
    equipes = entrada.equipes

    _imprimir_contexto_inicial(g, castelo, portos, equipes)

    if tem_ciclo_negativo_global(g.adj, g.n):
        print("ERRO: ciclo negativo detectado. Entrada invalida.")
        return 1

    alcancaveis = bfs_alcancaveis(g.adj, castelo)
    portos_validos = [p for p in portos if p in alcancaveis]

    if not portos_validos:
        print("Ladrao nao tem rota ate nenhum porto alcancavel. Preso por estrutura.")
        res_sem_porto = _resultado_sem_porto(castelo, equipes)
        res_sem_porto["eventos"] = [
            f"Estado inicial: ladrão em {castelo}; equipes em {equipes}",
            "Nenhum porto é alcançável a partir do castelo.",
        ]
        _imprimir_simulacao(res_sem_porto)
        gerar_relatorio(res_sem_porto, 0, [], len(equipes), caminho_saida)
        return 0

    k_minimo, corte = _calcular_corte_minimo(g, castelo, portos_validos)

    if len(equipes) < k_minimo:
        print(
            "Captura potencialmente inviavel: "
            f"{len(equipes)} equipes disponiveis, minimo teorico {k_minimo}."
        )
        print(f"Vertices recomendados para bloqueio: {corte}")

    res_inicial = _simular_estrategia(
        g,
        castelo,
        portos_validos,
        equipes,
        "posicoes iniciais informadas",
        len(equipes),
    )
    _imprimir_simulacao(res_inicial)

    res_final = res_inicial

    if res_inicial["status"] == "ESCAPOU" and corte:
        tentativa_inicial = {
            "status": res_inicial["status"],
            "rodadas": res_inicial["rodadas"],
            "equipes": len(equipes),
        }
        res_replanejado = _simular_estrategia(
            g,
            castelo,
            portos_validos,
            list(corte),
            "reposicionamento no corte minimo",
            len(equipes),
            tentativa_inicial=tentativa_inicial,
        )
        _imprimir_simulacao(res_replanejado)
        if _foi_capturado(res_replanejado["status"]):
            res_final = res_replanejado

    gerar_relatorio(res_final, k_minimo, corte, len(equipes), caminho_saida)
        
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in {2, 3}:
        caminho_entrada = "entrada.txt"
        caminho_saida = "saida.txt"
    else:
        caminho_entrada = sys.argv[1]
        caminho_saida = sys.argv[2] if len(sys.argv) == 3 else None

    raise SystemExit(main(caminho_entrada, caminho_saida))
