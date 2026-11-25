"""Gráfico 1: demandas atendidas em função do orçamento, modelo exato × guloso × aleatório.

Mostra o retorno decrescente do orçamento e quanto o modelo exato ganha sobre as alternativas simples.
Linha azul = modelo exato; laranja = guloso por caminhos; cinza = aleatório (média e faixa 10-90%).
"""

import numpy as np

from comum import (AZUL, CINZA, LARANJA, MUDO, TINTA2, aleatorio, carregar, cobertas, estilo,
                   guloso, maximo_atingivel, resolver_fluxo, rotulo, salvar, total_demandas)

ORCAMENTOS = [100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500]


def calcular():
    inst = carregar()
    linhas = []
    for B in ORCAMENTOS:
        esc, otimo, dt, ok = resolver_fluxo(inst, B)
        gul = cobertas(inst, guloso(inst, B))
        sorteio = aleatorio(inst, B)
        linhas.append((B, otimo, gul, float(np.mean(sorteio)),
                       float(np.percentile(sorteio, 10)), float(np.percentile(sorteio, 90)), ok))
        print(f"B={B:>5}: exato {otimo:3d} | guloso {gul:3d} | aleatório {np.mean(sorteio):5.1f}")
    return inst, linhas


def desenhar(inst, linhas):
    estilo()
    import matplotlib.pyplot as plt
    B = [l[0] for l in linhas]
    fig, ax = plt.subplots(figsize=(8.6, 5))
    ax.fill_between(B, [l[4] for l in linhas], [l[5] for l in linhas], color=CINZA, alpha=0.35, lw=0)
    ax.plot(B, [l[3] for l in linhas], color=MUDO, lw=2, marker="o", ms=5, mec="#fcfcfb", mew=1.5)
    ax.plot(B, [l[2] for l in linhas], color=LARANJA, lw=2, marker="o", ms=5, mec="#fcfcfb", mew=1.5)
    ax.plot(B, [l[1] for l in linhas], color=AZUL, lw=2.4, marker="o", ms=6, mec="#fcfcfb", mew=1.5)
    teto = maximo_atingivel(inst)
    ax.axhline(teto, color=MUDO, lw=1, ls=(0, (4, 3)))
    ax.text(B[0], teto + 1.2, f"máximo atingível com todas as arestas: {teto} de {total_demandas(inst)}",
            color=TINTA2, fontsize=9, va="bottom")
    i = B.index(1200)                      # onde exato e guloso estão bem separados
    rotulo(ax, B[i], linhas[i][1], "Modelo exato", AZUL, dx=-10, dy=10, ha="right")
    rotulo(ax, B[i], linhas[i][2], "Guloso por caminhos", LARANJA, dx=10, dy=-10, ha="left")
    rotulo(ax, B[-1], linhas[-1][3], "Aleatório (média; faixa 10–90%)", MUDO, dx=8, dy=0)
    ax.set_xticks(range(0, B[-1] + 1, 500))
    ax.set_xlim(0, B[-1] * 1.32)
    ax.set_ylim(0, teto * 1.12)
    ax.set_xlabel("Orçamento de ativação B")
    ax.set_ylabel("Demandas atendidas")
    ax.set_title("Quanto o orçamento rende: modelo exato × alternativas simples")
    ax.xaxis.grid(False)
    return salvar(fig, "g1_cobertura_vs_orcamento.png")


def main():
    inst, linhas = calcular()
    desenhar(inst, linhas)


if __name__ == "__main__":
    main()
