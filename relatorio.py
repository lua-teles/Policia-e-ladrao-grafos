"""Geracao do relatorio final da simulacao."""

from __future__ import annotations

from pathlib import Path


def _adicionar_secao(linhas: list[str], titulo: str) -> None:
    linhas.append(titulo)


def _formatar_caminho(caminho: list[int]) -> str:
    return " -> ".join(map(str, caminho))


def montar_relatorio(
    res: dict,
    k_minimo: int,
    corte: list[int],
    q_equipes: int,
) -> str:
    linhas: list[str] = []

    linhas.append("=" * 60)
    linhas.append("SISTEMA DE CAPTURA - RELATORIO FINAL")
    linhas.append("=" * 60)
    linhas.append(f"Resultado: {res['status']}")
    linhas.append(f"Rodadas:   {res['rodadas']}")
    linhas.append(f"Estrategia final: {res.get('estrategia', 'nao informada')}")
    linhas.append("")

    _adicionar_secao(linhas, "ANALISE TEORICA")
    linhas.append(f"Equipes minimas necessarias (Min-Cut): {k_minimo}")
    linhas.append(f"Vertices do corte minimo: {corte}")
    linhas.append(f"Equipes disponiveis: {q_equipes}")
    linhas.append(
        f"Equipes usadas na estrategia final: {res.get('equipes_necessarias', q_equipes)}"
    )
    if res.get("equipes_adicionais", 0) > 0:
        linhas.append(f"Equipes adicionais solicitadas: {res['equipes_adicionais']}")
    if q_equipes < k_minimo:
        linhas.append("Diagnostico: equipes insuficientes para bloqueio teorico.")
    elif q_equipes == k_minimo:
        linhas.append("Diagnostico: quantidade de equipes exatamente no limiar teorico.")
    else:
        linhas.append("Diagnostico: ha equipes acima do minimo teorico.")
    tentativa_inicial = res.get("tentativa_inicial")
    if tentativa_inicial is not None:
        linhas.append(
            "Tentativa inicial: "
            f"{tentativa_inicial['status']} em {tentativa_inicial['rodadas']} rodadas "
            f"com {tentativa_inicial['equipes']} equipe(s)."
        )
    linhas.append("")

    _adicionar_secao(linhas, "LADRAO")
    linhas.append("Caminho: " + _formatar_caminho(res["caminho_ladrao"]))
    if "equipe_captura" in res:
        linhas.append(
            f"Capturado pela equipe {res['equipe_captura']} na rodada {res['rodadas']}"
        )
    if "momento_captura" in res:
        linhas.append(f"Momento da captura: {res['momento_captura']}")
    linhas.append("")

    _adicionar_secao(linhas, "EQUIPES POLICIAIS")
    for i, caminho in res["caminhos_equipes"].items():
        linhas.append(f"Equipe {i}: " + _formatar_caminho(caminho))
    linhas.append("")

    _adicionar_secao(linhas, "NOTAS DE CORRETUDE E EFICIENCIA")
    linhas.append(
        "Bellman-Ford e usado por suportar arestas com peso negativo sem invalidar a otimizacao."
    )
    linhas.append(
        "Grafo reverso evita executar Bellman-Ford por equipe, reduzindo custo por rodada de O(Q*V*E) para O(V*E)."
    )
    linhas.append(
        "O min-cut com vertex split calcula o menor bloqueio estrutural permitindo posicionar equipes tambem nos portos."
    )
    linhas.append("=" * 60)

    return chr(10).join(linhas)


def gerar_relatorio(
    res: dict,
    k_minimo: int,
    corte: list[int],
    q_equipes: int,
    caminho_saida: str | None = None,
) -> str:
    texto = montar_relatorio(res, k_minimo, corte, q_equipes)
    print(texto)
    if caminho_saida:
        Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_saida, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
    return texto
