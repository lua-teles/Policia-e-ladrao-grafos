import sys
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter

try:
    import networkx as nx
    NETWORKX_DISPONIVEL = True
except ImportError:
    NETWORKX_DISPONIVEL = False

from grafo import ler_entrada
from algoritmos import (
    bfs_alcancaveis, construir_rede_fluxo,
    edmonds_karp, vertices_do_corte, tem_ciclo_negativo_global
)
from simulacao import simular_com_rastreamento

# Cores
COR_NORMAL   = "#cccccc"
COR_CASTELO  = "#9b59b6"
COR_PORTO    = "#2ecc71"
COR_CORTE    = "#e67e22"
COR_LADRAO   = "#e74c3c"
COR_POLICIA  = "#3498db"
COR_SOBREPOS = "#ff00ff"
COR_ARESTA   = "#aaaaaa"
COR_FUNDO    = "#1a1a2e"
COR_TEXTO    = "#ffffff"

def gerar_animacao(entrada_path, saida_path, fps=1):
    entrada = ler_entrada(entrada_path)
    g, castelo, portos, equipes = entrada.grafo, entrada.castelo, entrada.portos, entrada.equipes

    if tem_ciclo_negativo_global(g.adj, g.n):
        print("Erro: Ciclo negativo alcançável detectado.")
        return

    alcancaveis = bfs_alcancaveis(g.adj, castelo)
    portos_validos = [p for p in portos if p in alcancaveis]
    portos_set = set(portos_validos)

    if castelo in portos_set:
        corte = []
    else:
        cap, n_rede, t = construir_rede_fluxo(g, castelo, portos_validos)
        _, residual = edmonds_karp(cap, n_rede, 2 * castelo + 1, t)
        corte = vertices_do_corte(residual, n_rede, 2 * castelo + 1, g)
    corte_set = set(corte)

    if NETWORKX_DISPONIVEL:
        G = nx.DiGraph()
        for v in range(g.n):
            G.add_node(v)
        for u in range(g.n):
            for v, w in g.adj[u]:
                G.add_edge(u, v, weight=w)

        try:
            pos = nx.kamada_kawai_layout(G)
        except Exception:
            pos = nx.spring_layout(G, seed=42, k=2.0)
    else:
        G = None
        import math
        pos = {i: (math.cos(2*math.pi*i/g.n), math.sin(2*math.pi*i/g.n)) for i in range(g.n)}

    frames = simular_com_rastreamento(g, castelo, portos_validos, equipes)

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(COR_FUNDO)

    # Legenda fixa
    patches = [
        mpatches.Patch(color=COR_CASTELO, label="Castelo (Início)"),
        mpatches.Patch(color=COR_PORTO,   label="Porto (Fuga)"),
        mpatches.Patch(color=COR_CORTE,   label="Corte Mínimo"),
        mpatches.Patch(color=COR_LADRAO,  label="Ladrão"),
        mpatches.Patch(color=COR_POLICIA, label="Polícia"),
        mpatches.Patch(color=COR_SOBREPOS,label="Captura"),
    ]

    def update(frame_idx):
        ax.clear()
        ax.axis("off")
        ax.set_facecolor(COR_FUNDO)
        f = frames[frame_idx]
        pos_ladrao = f["pos_ladrao"]
        equipes_frame = list(f["pos_equipes"])
        pos_equipes = set(equipes_frame)

        colors = []
        node_iterable = G.nodes if NETWORKX_DISPONIVEL else range(g.n)
        for v in node_iterable:
            if v == pos_ladrao and v in pos_equipes:
                colors.append(COR_SOBREPOS)
            elif v == pos_ladrao:
                colors.append(COR_LADRAO)
            elif v in pos_equipes:
                colors.append(COR_POLICIA)
            elif v == castelo:
                colors.append(COR_CASTELO)
            elif v in portos_set:
                colors.append(COR_PORTO)
            elif v in corte_set:
                colors.append(COR_CORTE)
            else:
                colors.append(COR_NORMAL)

        if NETWORKX_DISPONIVEL:
            nx.draw(G, pos, ax=ax, node_color=colors, with_labels=True, 
                    node_size=600, font_size=10, font_color="black", font_weight="bold",
                    edge_color=COR_ARESTA, width=1.5, node_shape='o',
                    arrowsize=15)
            
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax, label_pos=0.3, rotate=False)
        else:
            for u in range(g.n):
                xu, yu = pos[u]
                for v, w in g.adj[u]:
                    xv, yv = pos[v]
                    ax.annotate("", xy=(xv, yv), xytext=(xu, yu),
                        arrowprops=dict(arrowstyle="-|>", color=COR_ARESTA, lw=0.8))
                    mx, my = (xu+xv)/2, (yu+yv)/2
                    ax.text(mx, my, f"{w:g}", fontsize=6, color="#888888", ha="center")
            for v in range(g.n):
                c = plt.Circle(pos[v], 0.07, color=colors[v], zorder=3)
                ax.add_patch(c)
                ax.text(pos[v][0], pos[v][1], str(v), color="black", ha="center", va="center", zorder=4)

        ax.set_title(f["titulo"], color=COR_TEXTO, fontsize=12, pad=10)
        ax.legend(handles=patches, loc="upper left", fontsize=9, facecolor="#2a2a3e", labelcolor=COR_TEXTO)
        info_texto = (
            f"Ladrão: {pos_ladrao}\n"
            f"Equipes: {equipes_frame if equipes_frame else 'nenhuma'}"
        )
        ax.text(
            0.98,
            0.02,
            info_texto,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            color=COR_TEXTO,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#2a2a3e", edgecolor="#666666"),
        )

    anim = FuncAnimation(fig, update, frames=len(frames), interval=1000//fps)
    anim.save(saida_path, writer=PillowWriter(fps=fps))
    print(f"Animação gerada: {saida_path} ({len(frames)} frames)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada")
    parser.add_argument("saida")
    parser.add_argument("--fps", type=int, default=1)
    args = parser.parse_args()
    gerar_animacao(args.entrada, args.saida, args.fps)
