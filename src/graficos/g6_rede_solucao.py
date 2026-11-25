"""Gráfico 6: a rede com as arestas ativadas na solução ótima.

Cinza fino = arestas candidatas não escolhidas; azul escuro = arestas ativadas. Nós: laranja =
especialista; azul = pessoa com pelo menos uma demanda atendida; cinza = nenhuma demanda atendida.
"""

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

from comum import (AZUL, CINZA, EIXO, LARANJA, MUDO, SUPERFICIE, TINTA, TINTA2, carregar, estilo, mc,
                   podar, resolver_fluxo, salvar)

B = 400


def main():
    inst = carregar()
    nos, fonte, dem, ex, cand = inst
    esp = set().union(*fonte.values())
    esc = podar(inst, resolver_fluxo(inst, B)[0])
    cob = mc.cobertura(fonte, dem, ex, esc)
    atendidos = set().union(*cob.values())
    n_cob = sum(len(v) for v in cob.values())

    G = nx.DiGraph()
    G.add_nodes_from(nos)
    G.add_edges_from(cand)
    pos = nx.kamada_kawai_layout(G.to_undirected())

    estilo()
    fig, ax = plt.subplots(figsize=(10, 8.4))
    ax.set_axis_off()
    outras = [e for e in cand if e not in set(esc)]
    nx.draw_networkx_edges(G, pos, edgelist=outras, edge_color=EIXO, width=0.7, arrows=True,
                           arrowsize=6, alpha=0.8, node_size=170, ax=ax)
    nx.draw_networkx_edges(G, pos, edgelist=esc, edge_color="#104281", width=2.4, arrows=True,
                           arrowsize=13, node_size=170, ax=ax)
    cor_no = [LARANJA if n in esp else (AZUL if n in atendidos else CINZA) for n in nos]
    nx.draw_networkx_nodes(G, pos, nodelist=nos, node_color=cor_no, node_size=170,
                           edgecolors=SUPERFICIE, linewidths=1.6, ax=ax)
    nx.draw_networkx_labels(G, pos, labels={n: str(n) for n in esp}, font_size=7.5,
                            font_color="#ffffff", font_weight="bold", ax=ax)
    ax.set_title(f"Rede com as {len(esc)} arestas ativadas (B = {B}): {n_cob} demandas atendidas",
                 loc="left", fontsize=12.5)
    legenda = [Line2D([], [], marker="o", ls="", color=LARANJA, label="Especialista (rótulo = id)", ms=9),
               Line2D([], [], marker="o", ls="", color=AZUL, label="Tem demanda atendida", ms=9),
               Line2D([], [], marker="o", ls="", color=CINZA, label="Nenhuma demanda atendida", ms=9),
               Line2D([], [], color="#104281", lw=2.4, label="Aresta ativada"),
               Line2D([], [], color=EIXO, lw=1, label="Candidata não escolhida")]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, 0.01), fontsize=9,
              labelcolor=TINTA2, ncol=3)
    return salvar(fig, "g6_rede_solucao.png")


if __name__ == "__main__":
    main()
