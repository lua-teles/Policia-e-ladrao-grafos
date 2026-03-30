"""Simulacao rodada a rodada da perseguicao."""

from __future__ import annotations

from algoritmos import INF, bellman_ford, proximo_vertice, reconstruir_caminho


MAX_MULTIPLICADOR_RODADAS = 2


def _formatar_equipes(posicoes_equipes: list[int]) -> str:
    if not posicoes_equipes:
        return "nenhuma equipe"
    return ", ".join(
        f"equipe {indice} em {posicao}"
        for indice, posicao in enumerate(posicoes_equipes)
    )


def _formatar_caminho(caminho: list[int]) -> str:
    return " -> ".join(map(str, caminho))


def resultado(
    status: str,
    rodada: int,
    historico_ladrao: list[int],
    historico_equipes: dict[int, list[int]],
    eventos: list[str],
    equipe: int | None = None,
    momento: str | None = None,
) -> dict:
    res = {
        "status": status,
        "rodadas": rodada,
        "caminho_ladrao": historico_ladrao,
        "caminhos_equipes": historico_equipes,
        "eventos": eventos,
    }
    if equipe is not None:
        res["equipe_captura"] = equipe
    if momento is not None:
        res["momento_captura"] = momento
    return res


def verificar_cerco(g, pos_ladrao: int, posicoes_equipes: list[int]) -> bool:
    vizinhos = g.vizinhos_saida(pos_ladrao)
    if not vizinhos:
        return True
    ocupados = set(posicoes_equipes)
    return all(v in ocupados for v in vizinhos)


def _escolher_porto_alvo(dist: list[float], portos: list[int]) -> int | None:
    candidatos = [p for p in portos if dist[p] < INF]
    if not candidatos:
        return None
    return min(candidatos, key=lambda p: dist[p])


def _equipe_no_vertice(pos_ladrao: int, posicoes_equipes: list[int]) -> int | None:
    for i, pos in enumerate(posicoes_equipes):
        if pos == pos_ladrao:
            return i
    return None


def _resultado_captura(
    rodada: int,
    historico_ladrao: list[int],
    historico_equipes: dict[int, list[int]],
    eventos: list[str],
    equipe: int,
    momento: str,
) -> dict:
    return resultado(
        "PRESO_ALCANCE",
        rodada,
        historico_ladrao,
        historico_equipes,
        eventos,
        equipe=equipe,
        momento=momento,
    )


def _caminho_por_pred_reverso(pred_rev: list[int], origem: int, destino: int) -> list[int]:
    caminho = [origem]
    atual = origem

    while atual != destino:
        proximo = pred_rev[atual]
        if proximo == -1:
            return []
        atual = proximo
        caminho.append(atual)

    return caminho


def simular(g, castelo: int, portos: list[int], equipes_pos: list[int]) -> dict:
    pos_ladrao = castelo
    portos_set = set(portos)

    historico_ladrao = [castelo]
    pos_equipes = list(equipes_pos)
    historico_equipes = {i: [pos] for i, pos in enumerate(pos_equipes)}
    eventos = [
        f"Estado inicial: ladrão em {pos_ladrao}; {_formatar_equipes(pos_equipes)}"
    ]

    equipe_inicial = _equipe_no_vertice(pos_ladrao, pos_equipes)
    if equipe_inicial is not None:
        eventos.append(f"Rodada 0: equipe {equipe_inicial} já está no vértice {pos_ladrao}")
        return _resultado_captura(
            0,
            historico_ladrao,
            historico_equipes,
            eventos,
            equipe_inicial,
            "inicio da simulacao",
        )

    rodada = 0
    max_rodadas = g.n * MAX_MULTIPLICADOR_RODADAS

    while True:
        rodada += 1

        if rodada > max_rodadas:
            eventos.append(f"Rodada {rodada}: limite de rodadas excedido")
            return resultado("INDEFINIDO", rodada, historico_ladrao, historico_equipes, eventos)

        if verificar_cerco(g, pos_ladrao, pos_equipes):
            eventos.append(f"Rodada {rodada}: ladrão cercado em {pos_ladrao} antes de se mover")
            return resultado(
                "PRESO_CERCO",
                rodada,
                historico_ladrao,
                historico_equipes,
                eventos,
                momento="antes do movimento do ladrao",
            )

        ocupados = set(pos_equipes)
        dist_lad, pred_lad = bellman_ford(g.adj, g.n, pos_ladrao, bloqueados=ocupados)
        porto_alvo = _escolher_porto_alvo(dist_lad, portos)
        portos_ordenados = sorted(portos, key=lambda porto: porto)
        avaliacoes_portos = []
        for porto in portos_ordenados:
            if dist_lad[porto] == INF:
                avaliacoes_portos.append(f"porto {porto}: bloqueado ou inalcançável")
            else:
                caminho_porto = reconstruir_caminho(pred_lad, pos_ladrao, porto)
                avaliacoes_portos.append(
                    f"porto {porto}: custo {dist_lad[porto]:g}, caminho {_formatar_caminho(caminho_porto)}"
                )
        eventos.append(
            f"Rodada {rodada}: avaliação do ladrão sobre os portos -> "
            + " | ".join(avaliacoes_portos)
        )

        if porto_alvo is None:
            eventos.append(
                f"Rodada {rodada}: sem rota disponível até porto evitando vértices ocupados"
            )
            return resultado(
                "PRESO_SEM_ROTA",
                rodada,
                historico_ladrao,
                historico_equipes,
                eventos,
                momento="antes do movimento do ladrao",
            )

        prox_ladrao = proximo_vertice(pred_lad, pos_ladrao, porto_alvo)
        if prox_ladrao is None:
            eventos.append(f"Rodada {rodada}: não foi possível reconstruir movimento do ladrão")
            return resultado(
                "PRESO_SEM_ROTA",
                rodada,
                historico_ladrao,
                historico_equipes,
                eventos,
                momento="antes do movimento do ladrao",
            )

        caminho_escolhido = reconstruir_caminho(pred_lad, pos_ladrao, porto_alvo)
        eventos.append(
            f"Rodada {rodada}: ladrão escolhe o porto {porto_alvo} por ter menor custo atual "
            f"({dist_lad[porto_alvo]:g}) pelo caminho {_formatar_caminho(caminho_escolhido)}"
        )
        pos_ladrao = prox_ladrao
        historico_ladrao.append(pos_ladrao)
        eventos.append(f"Rodada {rodada}: ladrão move para {pos_ladrao} mirando o porto {porto_alvo}")

        equipe_no_destino = _equipe_no_vertice(pos_ladrao, pos_equipes)
        if equipe_no_destino is not None:
            eventos.append(
                f"Rodada {rodada}: ladrão entrou no vértice ocupado pela equipe {equipe_no_destino}"
            )
            return _resultado_captura(
                rodada,
                historico_ladrao,
                historico_equipes,
                eventos,
                equipe_no_destino,
                "apos o movimento do ladrao",
            )

        if pos_ladrao in portos_set:
            eventos.append(f"Rodada {rodada}: ladrão escapou pelo porto {pos_ladrao}")
            return resultado("ESCAPOU", rodada, historico_ladrao, historico_equipes, eventos)

        if verificar_cerco(g, pos_ladrao, pos_equipes):
            eventos.append(f"Rodada {rodada}: ladrão cercado em {pos_ladrao} após se mover")
            return resultado(
                "PRESO_CERCO",
                rodada,
                historico_ladrao,
                historico_equipes,
                eventos,
                momento="apos o movimento do ladrao",
            )

        dist_rev, pred_rev = bellman_ford(g.adj_rev, g.n, pos_ladrao)
        explicacoes_policia = []
        for i, pos in enumerate(pos_equipes):
            if dist_rev[pos] == INF:
                explicacoes_policia.append(
                    f"equipe {i} em {pos}: sem rota até o ladrão em {pos_ladrao}"
                )
                continue
            caminho_policial = _caminho_por_pred_reverso(pred_rev, pos, pos_ladrao)
            if not caminho_policial:
                explicacoes_policia.append(
                    f"equipe {i} em {pos}: sem caminho reconstruível até o ladrão"
                )
                continue
            explicacoes_policia.append(
                f"equipe {i} em {pos}: custo {dist_rev[pos]:g}, caminho {_formatar_caminho(caminho_policial)}"
            )
        if explicacoes_policia:
            eventos.append(
                f"Rodada {rodada}: avaliação das equipes -> " + " | ".join(explicacoes_policia)
            )
        else:
            eventos.append(f"Rodada {rodada}: não há equipes para reagir ao movimento do ladrão")

        for subpasso in range(2):
            movimentos = []
            # pos reflete as posições após os sub-passos anteriores
            for i, pos in enumerate(pos_equipes):
                if pos == pos_ladrao:
                    eventos.append(
                        f"Rodada {rodada}, subpasso {subpasso + 1}: equipe {i} já estava com o ladrão"
                    )
                    return _resultado_captura(
                        rodada,
                        historico_ladrao,
                        historico_equipes,
                        eventos,
                        i,
                        f"rodada {rodada}, subpasso policial {subpasso + 1}",
                    )

                if dist_rev[pos] == INF:
                    continue

                prox_policial = pred_rev[pos]
                if prox_policial == -1:
                    continue

                pos_equipes[i] = prox_policial
                historico_equipes[i].append(prox_policial)
                movimentos.append(
                    f"equipe {i}: {pos} -> {prox_policial} para reduzir a distância até {pos_ladrao}"
                )

                if pos_equipes[i] == pos_ladrao:
                    eventos.append(
                        f"Rodada {rodada}, subpasso {subpasso + 1}: "
                        f"equipe {i} alcançou o ladrão em {pos_ladrao}"
                    )
                    return _resultado_captura(
                        rodada,
                        historico_ladrao,
                        historico_equipes,
                        eventos,
                        i,
                        f"rodada {rodada}, subpasso policial {subpasso + 1}",
                    )

            if movimentos:
                eventos.append(
                    f"Rodada {rodada}, subpasso {subpasso + 1}: " + "; ".join(movimentos)
                )


def simular_com_rastreamento(g, castelo, portos, equipes_pos):
    """
    Igual a simular(), mas retorna lista de frames para visualização.
    Cada frame é um dict com pos_ladrao, pos_equipes e titulo.
    """
    pos_ladrao  = castelo
    portos_set  = set(portos)
    pos_equipes = list(equipes_pos)
    frames      = []

    def capturar(titulo):
        frames.append({
            "pos_ladrao":  pos_ladrao,
            "pos_equipes": list(pos_equipes),
            "titulo":      titulo,
        })

    capturar(
        "Rodada 0: Estado inicial | "
        f"Ladrao em {pos_ladrao} | {_formatar_equipes(pos_equipes)}"
    )

    equipe_inicial = _equipe_no_vertice(pos_ladrao, pos_equipes)
    if equipe_inicial is not None:
        capturar(f"Rodada 0: PRESO por alcance inicial (equipe {equipe_inicial})")
        return frames

    rodada = 0
    max_rodadas = g.n * MAX_MULTIPLICADOR_RODADAS
    
    while True:
        rodada += 1

        if rodada > max_rodadas:
            capturar(f"Rodada {rodada}: INDEFINIDO")
            return frames

        if verificar_cerco(g, pos_ladrao, pos_equipes):
            capturar(f"Rodada {rodada}: PRESO por cerco")
            break

        dist_lad, pred_lad = bellman_ford(g.adj, g.n, pos_ladrao, bloqueados=set(pos_equipes))
        porto_alvo = _escolher_porto_alvo(dist_lad, portos)

        if porto_alvo is None:
            capturar(f"Rodada {rodada}: PRESO sem rota")
            break

        prox = proximo_vertice(pred_lad, pos_ladrao, porto_alvo)
        if prox is None:
            capturar(f"Rodada {rodada}: PRESO sem rota")
            break

        pos_ladrao = prox
        capturar(f"Rodada {rodada}: Ladrão move para {pos_ladrao}")

        equipe_no_destino = _equipe_no_vertice(pos_ladrao, pos_equipes)
        if equipe_no_destino is not None:
            capturar(f"Rodada {rodada}: PRESO ao entrar no vértice da equipe {equipe_no_destino}")
            break

        if pos_ladrao in portos_set:
            capturar(f"Rodada {rodada}: ESCAPOU pelo porto {pos_ladrao}")
            break

        if verificar_cerco(g, pos_ladrao, pos_equipes):
            capturar(f"Rodada {rodada}: PRESO por cerco após movimento")
            break

        dist_rev, pred_rev = bellman_ford(g.adj_rev, g.n, pos_ladrao)

        for subpasso in range(2):
            capturas = []
            # pos reflete as posições após os sub-passos anteriores
            for i, pos in enumerate(pos_equipes):
                if pos == pos_ladrao:
                    capturar(f"Rodada {rodada} sub{subpasso+1}: PRESO por alcance (equipe {i})")
                    return frames

                if dist_rev[pos] == INF:
                    continue

                prox_pol = pred_rev[pos]
                if prox_pol == -1:
                    continue

                pos_equipes[i] = prox_pol
                capturas.append(i)

                if pos_equipes[i] == pos_ladrao:
                    capturar(f"Rodada {rodada} sub{subpasso+1}: PRESO por alcance (equipe {i})")
                    return frames

            if capturas:
                capturar(f"Rodada {rodada} sub{subpasso+1}: Polícia move (equipes {capturas})")

    return frames
