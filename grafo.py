"""Estruturas de grafo e leitura de entrada para o sistema de captura."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EntradaProblema:
    grafo: "Grafo"
    castelo: int
    portos: list[int]
    equipes: list[int]


class Grafo:
    def __init__(self, n: int) -> None:
        if n <= 0:
            raise ValueError("Numero de vertices deve ser positivo.")
        self.n = n
        self.adj: list[list[tuple[int, float]]] = [[] for _ in range(n)]
        self.adj_rev: list[list[tuple[int, float]]] = [[] for _ in range(n)]

    def adicionar_aresta(self, u: int, v: int, w: float) -> None:
        self._validar_vertice(u)
        self._validar_vertice(v)
        self.adj[u].append((v, w))
        self.adj_rev[v].append((u, w))

    def vizinhos_saida(self, u: int) -> list[int]:
        self._validar_vertice(u)
        return [v for v, _ in self.adj[u]]

    def _validar_vertice(self, v: int) -> None:
        if not (0 <= v < self.n):
            raise ValueError(f"Vertice fora do intervalo [0, {self.n - 1}]: {v}")


def _parse_linha_ints(linha: str, contexto: str) -> list[int]:
    texto = linha.strip()

    if contexto == "cabecalho":
        if texto.startswith("=") or "SISTEMA DE CAPTURA" in texto:
            raise ValueError(
                "Arquivo informado parece ser um relatorio de saida, nao um arquivo de entrada. "
                "Use um arquivo no formato 'n m' na primeira linha."
            )

    try:
        return list(map(int, linha.split()))
    except ValueError as exc:
        raise ValueError(f"Linha invalida em {contexto}: '{texto}'") from exc


def ler_entrada(caminho: str) -> EntradaProblema:
    with open(caminho, "r", encoding="utf-8") as f:
        cabecalho = _parse_linha_ints(f.readline(), "cabecalho")
        if len(cabecalho) != 2:
            raise ValueError("Cabecalho deve ter formato: n m")
        n, m = cabecalho
        if m < 0:
            raise ValueError("Numero de arestas nao pode ser negativo.")

        g = Grafo(n)

        for i in range(m):
            linha = f.readline().strip().split()
            if len(linha) != 3:
                raise ValueError(f"Aresta {i + 1} invalida. Esperado: u v w")
            u_s, v_s, w_s = linha
            try:
                u = int(u_s)
                v = int(v_s)
                w = float(w_s)
            except ValueError as exc:
                raise ValueError(f"Aresta {i + 1} contem valores invalidos.") from exc
            g.adicionar_aresta(u, v, w)

        linha_castelo = f.readline()
        if not linha_castelo:
            raise ValueError("Arquivo incompleto: faltou linha do castelo.")
        castelo = int(linha_castelo.strip())
        g._validar_vertice(castelo)

        linha_portos = _parse_linha_ints(f.readline(), "portos")
        if not linha_portos:
            raise ValueError("Linha de portos vazia.")
        k = linha_portos[0]
        portos = linha_portos[1:]
        if k != len(portos):
            raise ValueError("Quantidade de portos (k) nao confere com a lista informada.")
        for p in portos:
            g._validar_vertice(p)
            if p == castelo:
                raise ValueError("Vertices de saida devem ser diferentes do local do roubo.")

        linha_equipes = _parse_linha_ints(f.readline(), "equipes")
        if not linha_equipes:
            raise ValueError("Linha de equipes vazia.")
        q = linha_equipes[0]
        equipes = linha_equipes[1:]
        if q != len(equipes):
            raise ValueError("Quantidade de equipes (q) nao confere com a lista informada.")
        for e in equipes:
            g._validar_vertice(e)

    return EntradaProblema(grafo=g, castelo=castelo, portos=portos, equipes=equipes)
