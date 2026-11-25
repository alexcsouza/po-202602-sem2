"""Gráfico 3: efeito do limite de saltos H na cobertura.

Compara a formulação em camadas (H = 2, 3, 4, 5) com a formulação por fluxo (sem limite de saltos).
H é uma escala ordenada, então as linhas usam uma rampa de uma só matiz (azul): quanto mais escuro,
maior o H. Mostra o quanto a exigência de proximidade reduz a difusão possível.
"""

import matplotlib.pyplot as plt
import gurobipy as gp

from comum import (RAMPA_AZUL, TINTA2, carregar, estilo, resolver_fluxo, resolver_saltos, rotulo,
                   salvar, total_demandas)

ORCAMENTOS = [200, 400, 600, 800, 1000, 1200]
LIMITES = [2, 3, 4, 5]               # com licença completa pode-se incluir 6, 8...


def main():
    inst = carregar()
    resultados = {}                       # rótulo -> lista de demandas atendidas
    for H in LIMITES:
        serie = []
        try:
            for B in ORCAMENTOS:
                _, n_cob, dt, ok = resolver_saltos(inst, B, H, tempo=60)
                serie.append(n_cob)
                print(f"H={H} B={B}: {n_cob} {'(ótimo)' if ok else '(limite de tempo)'} {dt:.1f}s")
        except gp.GurobiError as erro:
            print(f"[aviso] H={H} pulado: modelo grande demais para a licença do Gurobi ({erro})")
            continue
        resultados[f"H = {H}"] = serie
    serie = []
    for B in ORCAMENTOS:
        _, n_cob, dt, ok = resolver_fluxo(inst, B, tempo=60)
        serie.append(n_cob)
        print(f"sem limite B={B}: {n_cob} {dt:.1f}s")
    resultados["sem limite"] = serie

    # sanidade: com mais saltos permitidos nunca se atende menos
    nomes = list(resultados)
    for a, b in zip(nomes, nomes[1:]):
        assert all(x <= y for x, y in zip(resultados[a], resultados[b])), f"{a} > {b}"

    estilo()
    fig, ax = plt.subplots(figsize=(8.6, 5))
    passos = [round(i * (len(RAMPA_AZUL) - 1) / max(1, len(nomes) - 1)) for i in range(len(nomes))]
    for nome, cor in zip(nomes, [RAMPA_AZUL[p] for p in passos]):
        y = resultados[nome]
        ax.plot(ORCAMENTOS, y, color=cor, lw=2.2, marker="o", ms=5.5, mec="#fcfcfb", mew=1.4)
        rotulo(ax, ORCAMENTOS[-1], y[-1], nome, cor, dx=8)
    ax.set_xticks(ORCAMENTOS)
    ax.set_xlim(ORCAMENTOS[0] * 0.8, ORCAMENTOS[-1] * 1.18)
    ax.set_ylim(0, None)
    ax.set_xlabel("Orçamento de ativação B")
    ax.set_ylabel(f"Demandas atendidas (de {total_demandas(inst)})")
    ax.set_title("Quanto a exigência de proximidade (limite de saltos) reduz a difusão")
    ax.xaxis.grid(False)
    return salvar(fig, "g3_limite_de_saltos.png")


if __name__ == "__main__":
    main()
