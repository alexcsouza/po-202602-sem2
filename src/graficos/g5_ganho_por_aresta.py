"""Gráfico 5: contribuição de cada aresta ativada (ganho marginal) na solução ótima.

Ganho marginal = demandas que deixam de ser atendidas se aquela aresta for retirada, mantendo as
demais. Em laranja, arestas entre dois especialistas (usadas como ponto de passagem). Como arestas
encadeadas se complementam, a soma dos ganhos pode passar do total atendido.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from comum import (AZUL, LARANJA, TINTA2, carregar, cobertas, estilo, ganho_marginal, podar,
                   resolver_fluxo, salvar, virgula)

B = 400


def main():
    inst = carregar()
    nos, fonte, dem, ex, cand = inst
    esp = set().union(*fonte.values())
    esc, n_cob, dt, ok = resolver_fluxo(inst, B)
    esc = podar(inst, esc)
    ganho = ganho_marginal(inst, esc)
    ordem = sorted(esc, key=lambda e: (ganho[e], -cand[e]))        # menor embaixo, maior em cima

    estilo()
    fig, ax = plt.subplots(figsize=(8.6, 0.42 * len(ordem) + 1.9))
    cores = [LARANJA if (u in esp and v in esp) else AZUL for u, v in ordem]
    y = range(len(ordem))
    ax.barh(y, [ganho[e] for e in ordem], color=cores, height=0.62)
    ax.set_yticks(list(y), [f"{u} → {v}   (custo {virgula(cand[(u, v)])})" for u, v in ordem], fontsize=9.5)
    for yi, e in zip(y, ordem):
        ax.text(ganho[e] + 0.12, yi, str(ganho[e]), va="center", fontsize=9, color=TINTA2)
    ax.set_xlabel("Demandas perdidas se a aresta for retirada")
    ax.set_title(f"Quais arestas sustentam a solução (B = {B}: {n_cob} demandas atendidas)")
    ax.xaxis.grid(True)
    ax.yaxis.grid(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, max(ganho.values()) + 1.2)
    ax.legend(handles=[Patch(color=AZUL, label="Aresta comum"),
                       Patch(color=LARANJA, label="Aresta entre dois especialistas")],
              loc="lower right", fontsize=9, labelcolor=TINTA2)
    return salvar(fig, "g5_ganho_por_aresta.png")


if __name__ == "__main__":
    main()
