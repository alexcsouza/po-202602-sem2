"""Gráfico 4: tempo de solução × tamanho da instância, formulação por fluxo × formulação em camadas.

Usa instâncias sintéticas de tamanho crescente (mesma estrutura dos CSV de exemplo, orçamento
proporcional ao número de pessoas, 3 sementes por tamanho). O ponto é a média, e a barra vai do
mínimo ao máximo. Ponto vazado = alguma execução parou no limite de tempo (sem prova de otimalidade).
Tamanhos que excedem a licença do Gurobi são pulados com aviso.
"""

import numpy as np
import matplotlib.pyplot as plt
import gurobipy as gp

from comum import (AZUL, LARANJA, SUPERFICIE, TINTA2, estilo, instancia_sintetica, resolver_fluxo,
                   resolver_saltos, rotulo, salvar)

TAMANHOS = [20, 30, 40, 50, 60, 70, 80]
SEMENTES = [0, 1, 2]
H = 3
TEMPO = 30.0


def medir(n):
    linha = {"fluxo": [], "saltos": []}
    for semente in SEMENTES:
        inst = instancia_sintetica(n, semente)
        B = 6.7 * n
        for nome, f in (("fluxo", lambda: resolver_fluxo(inst, B, tempo=TEMPO)),
                        ("saltos", lambda: resolver_saltos(inst, B, H, tempo=TEMPO))):
            try:
                _, cob, dt, ok = f()
            except gp.GurobiError:
                linha[nome] = None
                break
            if linha[nome] is not None:
                linha[nome].append((dt, ok))
        print(f"n={n} semente={semente}: " + ", ".join(
            f"{k}={'excede licença' if v is None else f'{v[-1][0]:.2f}s'}" for k, v in linha.items()))
    return linha


def main():
    dados = {"fluxo": {}, "saltos": {}}
    for n in TAMANHOS:
        linha = medir(n)
        for nome in dados:
            if linha[nome]:
                dados[nome][n] = linha[nome]

    estilo()
    fig, ax = plt.subplots(figsize=(8.6, 5))
    for nome, cor, texto in (("fluxo", AZUL, "Fluxo (sem limite de saltos)"),
                             ("saltos", LARANJA, f"Camadas (H = {H})")):
        ns = sorted(dados[nome])
        if not ns:
            continue
        med = [np.mean([t for t, _ in dados[nome][n]]) for n in ns]
        lo = [min(t for t, _ in dados[nome][n]) for n in ns]
        hi = [max(t for t, _ in dados[nome][n]) for n in ns]
        todas_ok = [all(ok for _, ok in dados[nome][n]) for n in ns]
        ax.plot(ns, med, color=cor, lw=2.2, zorder=2)
        ax.vlines(ns, lo, hi, color=cor, lw=1.4, alpha=0.7, zorder=2)
        for n, m, ok in zip(ns, med, todas_ok):
            ax.plot([n], [m], marker="o", ms=7, mfc=cor if ok else SUPERFICIE, mec=cor, mew=1.8, zorder=3)
        rotulo(ax, ns[-1], med[-1], texto, cor, dx=9)
    ax.set_yscale("log")
    ax.set_xticks(TAMANHOS)
    ax.set_xlim(TAMANHOS[0] - 3, TAMANHOS[-1] * 1.35)
    ax.set_xlabel("Número de pessoas na instância")
    ax.set_ylabel("Tempo de solução (s, escala log)")
    ax.set_title("Como o tempo de solução cresce com o tamanho da instância")
    ax.xaxis.grid(False)
    ax.text(0.01, 0.02, "ponto cheio: ótimo provado nas 3 sementes · ponto vazado: limite de tempo",
            transform=ax.transAxes, fontsize=8.5, color=TINTA2)
    return salvar(fig, "g4_escalabilidade.png")


if __name__ == "__main__":
    main()
