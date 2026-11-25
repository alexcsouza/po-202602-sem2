"""Gráfico 2: demandas atendidas por disciplina para três orçamentos (múltiplos pequenos).

Barra cinza = demandas da disciplina; barra azul = atendidas na solução ótima. Mostra como o modelo
distribui o orçamento entre as disciplinas, e que algumas ficam de fora quando o orçamento é curto.
"""

import numpy as np

import matplotlib.pyplot as plt
from comum import (AZUL, CINZA, SUPERFICIE, TINTA2, carregar, cobertas, estilo, mc, resolver_fluxo,
                   salvar, total_demandas)

ORCAMENTOS = [400, 800, 1200]


def main():
    inst = carregar()
    nos, fonte, dem, ex, cand = inst
    estilo()
    discs = sorted(dem)
    fig, eixos = plt.subplots(1, len(ORCAMENTOS), figsize=(11.5, 4.4), sharey=True)
    for ax, B in zip(eixos, ORCAMENTOS):
        esc, n_cob, dt, ok = resolver_fluxo(inst, B)
        cob = mc.cobertura(fonte, dem, ex, esc)
        x = np.arange(len(discs))
        ax.bar(x - 0.2, [len(dem[d]) for d in discs], 0.38, color=CINZA, ec=SUPERFICIE, lw=1.5,
               label="Demandas da disciplina")
        ax.bar(x + 0.2, [len(cob[d]) for d in discs], 0.38, color=AZUL, ec=SUPERFICIE, lw=1.5,
               label="Atendidas na solução")
        ax.set_xticks(x, [f"D{d}" for d in discs])
        ax.set_title(f"B = {B}: {n_cob} de {total_demandas(inst)} ({100 * n_cob / total_demandas(inst):.0f}%)",
                     fontsize=11)
        ax.xaxis.grid(False)
        ax.tick_params(axis="x", length=0)
    eixos[0].set_ylabel("Número de demandas")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    esquerda = eixos[0].get_position().x0
    fig.text(esquerda, 0.965, "Atendimento por disciplina conforme o orçamento", ha="left", va="top",
             fontsize=13, fontweight="bold", color="#0b0b0b")
    manipuladores, nomes = eixos[0].get_legend_handles_labels()
    fig.legend(manipuladores, nomes, loc="upper right", ncol=2, fontsize=9.5, labelcolor=TINTA2,
               bbox_to_anchor=(eixos[-1].get_position().x1, 0.975))
    return salvar(fig, "g2_cobertura_por_disciplina.png")


if __name__ == "__main__":
    main()
