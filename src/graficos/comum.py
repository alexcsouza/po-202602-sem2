"""Código compartilhado pelos gráficos: estilo, resolução dos modelos e métodos de comparação.

Os dados vêm de data/*.csv, lidos por src/ref/max_coverage_gurobi.py. Os gráficos são
gravados em resultados/graficos/.
"""

import heapq
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "resultados" / "graficos"
sys.path.insert(0, str(RAIZ / "src" / "ref"))

import gurobipy as gp                      # noqa: E402
from gurobipy import GRB                   # noqa: E402
import gurobi_max_coverage as mc           # noqa: E402

# ----------------------------------------------------------------------------
# Estilo (paleta validada: azul e laranja nas posições 1 e 2; rampa azul para escalas ordenadas)
# ----------------------------------------------------------------------------
SUPERFICIE, TINTA, TINTA2, MUDO = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRADE, EIXO = "#e1e0d9", "#c3c2b7"
AZUL, LARANJA = "#2a78d6", "#eb6834"
CINZA = "#b4b3ad"                                            # contexto / de-ênfase
RAMPA_AZUL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]   # escala ordenada


def estilo():
    plt.rcParams.update({
        "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
        "font.family": "sans-serif", "font.size": 10,
        "text.color": TINTA2, "axes.labelcolor": TINTA2, "xtick.color": MUDO, "ytick.color": MUDO,
        "axes.edgecolor": EIXO, "axes.linewidth": 1.0,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRADE, "grid.linewidth": 0.8,
        "axes.axisbelow": True, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.titlecolor": TINTA, "axes.titlelocation": "left",
        "legend.frameon": False, "lines.solid_capstyle": "round",
    })


def salvar(fig, nome):
    SAIDA.mkdir(parents=True, exist_ok=True)
    caminho = SAIDA / nome
    fig.savefig(caminho, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"gráfico salvo em {caminho}")
    return caminho


def milhar(ax, eixo="x"):
    f = FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", "."))
    (ax.xaxis if eixo == "x" else ax.yaxis).set_major_formatter(f)


def virgula(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def rotulo(ax, x, y, texto, cor, dx=6, dy=0, **kw):
    """Rótulo direto ao lado de uma série (texto em tinta secundária; cor só na marca)."""
    ax.annotate(texto, (x, y), xytext=(dx, dy), textcoords="offset points", va="center",
                color=TINTA2, fontsize=9.5, **kw)
    ax.plot([x], [y], marker="o", ms=0, color=cor)


# ----------------------------------------------------------------------------
# Instância e cobertura
# ----------------------------------------------------------------------------
def carregar():
    """(nos, fonte, demandas, existentes, candidatas) a partir de data/*.csv."""
    return mc.carregar_dados()


def total_demandas(inst):
    return sum(len(v) for v in inst[2].values())


def cobertas(inst, esc):
    nos, fonte, dem, ex, cand = inst
    return sum(len(v) for v in mc.cobertura(fonte, dem, ex, esc).values())


def maximo_atingivel(inst):
    nos, fonte, dem, ex, cand = inst
    return cobertas(inst, list(cand))


def niveis(adj, fontes, H):
    visto, fronteira, saida = set(fontes), set(fontes), [set(fontes)]
    for _ in range(H):
        novos = {v for u in fronteira for v in adj.get(u, ()) if v not in visto}
        visto |= novos
        fronteira = novos
        saida.append(set(visto))
    return saida


def cobertas_saltos(inst, esc, H):
    nos, fonte, dem, ex, cand = inst
    adj = mc.adjacencia(list(ex) + list(esc))
    return sum(len(dem[d] & niveis(adj, fonte[d], H)[-1]) for d in dem)


def podar(inst, esc):
    """Remove arestas sem efeito (empates do solver), das mais caras para as mais baratas."""
    nos, fonte, dem, ex, cand = inst
    esc = list(esc)
    base = cobertas(inst, esc)
    for e in sorted(esc, key=lambda e: -cand[e]):
        resto = [f for f in esc if f != e]
        if cobertas(inst, resto) >= base:
            esc = resto
    return esc


def ganho_marginal(inst, esc):
    base = cobertas(inst, esc)
    return {e: base - cobertas(inst, [f for f in esc if f != e]) for e in esc}


# ----------------------------------------------------------------------------
# Modelos exatos
# ----------------------------------------------------------------------------
def resolver_fluxo(inst, B, K=None, tempo=60.0, gap=1e-4):
    """Formulação por fluxo (sem limite de saltos). Devolve (arestas, demandas, tempo_s, ótimo?)."""
    nos, fonte, dem, ex, cand = inst
    m, x, r = mc.construir(nos, fonte, dem, ex, cand, B, K)
    m.Params.OutputFlag = 0
    m.Params.TimeLimit = tempo
    m.Params.MIPGap = gap
    t0 = time.time()
    m.optimize()
    dt = time.time() - t0
    esc = [e for e in x if x[e].X > 0.5]
    return esc, cobertas(inst, esc), dt, m.Status == GRB.OPTIMAL


def resolver_saltos(inst, B, H, K=None, tempo=60.0, gap=1e-4):
    """Formulação em camadas com limite de H saltos. Mesmo retorno de resolver_fluxo."""
    nos, fonte, dem, ex, cand = inst
    todos = list(ex) + list(cand)
    adj_E, adj_T = mc.adjacencia(ex), mc.adjacencia(todos)
    pred_E, pred_C = defaultdict(list), defaultdict(list)
    for u, v in ex:
        pred_E[v].append(u)
    for u, v in cand:
        pred_C[v].append(u)

    m = gp.Model("saltos")
    m.Params.OutputFlag = 0
    m.Params.TimeLimit = tempo
    m.Params.MIPGap = gap
    x = m.addVars(sorted(cand), vtype=GRB.BINARY, name="x")
    m.addConstr(gp.quicksum(cand[e] * x[e] for e in x) <= B)
    for u, lim in (K or {}).items():
        saindo = [e for e in cand if e[0] == u]
        if saindo:
            m.addConstr(gp.quicksum(x[e] for e in saindo) <= lim)

    obj = gp.LinExpr()
    for d in sorted(dem):
        S = fonte[d]
        lb, ub = niveis(adj_E, S, H), niveis(adj_T, S, H)   # só existentes / com todas ativadas
        r = {}
        for t in range(1, H + 1):
            for v in ub[t] - lb[t]:
                r[v, t] = m.addVar(lb=0.0, ub=1.0, name=f"r[{d},{v},{t}]")

        def val(v, t):
            if v in lb[t]:
                return 1.0
            if v not in ub[t]:
                return 0.0
            return r[v, t]

        for t in range(1, H + 1):
            for v in ub[t] - lb[t]:
                const, termos = 0.0, []
                for a in [val(v, t - 1)] + [val(u, t - 1) for u in pred_E[v]]:
                    if isinstance(a, float):
                        const += a
                    else:
                        termos.append(a)
                for u in pred_C[v]:
                    ru = val(u, t - 1)
                    if isinstance(ru, float):
                        if ru > 0.0:
                            termos.append(x[u, v])
                    else:
                        y = m.addVar(lb=0.0, ub=1.0)
                        m.addConstr(y <= x[u, v])
                        m.addConstr(y <= ru)
                        termos.append(y)
                if const < 1.0:
                    m.addConstr(r[v, t] <= const + gp.quicksum(termos))
                prev = val(v, t - 1)
                if not isinstance(prev, float):
                    m.addConstr(r[v, t] >= prev)
        for v in dem[d]:
            a = val(v, H)
            obj += a
    m.setObjective(obj, GRB.MAXIMIZE)
    t0 = time.time()
    m.optimize()
    dt = time.time() - t0
    esc = [e for e in x if x[e].X > 0.5]
    n_cob = cobertas_saltos(inst, esc, H)
    return esc, n_cob, dt, m.Status == GRB.OPTIMAL


# ----------------------------------------------------------------------------
# Métodos de comparação
# ----------------------------------------------------------------------------
def guloso(inst, B, K=None):
    """Guloso por caminhos: a cada passo escolhe o caminho mais barato (Dijkstra a partir dos nós já
    alcançados) até uma demanda ainda não atendida que maximize ganho/custo. Considera caminhos, e
    não arestas isoladas, porque uma aresta sozinha pode não atender nenhuma demanda."""
    import heapq
    nos, fonte, dem, ex, cand = inst
    esc, gasto = [], 0.0
    atual = cobertas(inst, esc)
    uso = defaultdict(int)
    while True:
        escolhido = set(esc)
        melhor = None
        cobertura = mc.cobertura(fonte, dem, ex, esc)
        adj = defaultdict(list)
        for u, v in list(ex) + esc:
            adj[u].append((v, 0.0, None))
        for e, c in cand.items():
            if e not in escolhido:
                adj[e[0]].append((e[1], c, e))
        vistos = set()
        for d in sorted(dem):
            alcancados = mc.alcancaveis(mc.adjacencia(list(ex) + esc), fonte[d])
            dist, pai = {v: 0.0 for v in alcancados}, {}
            fila = [(0.0, v) for v in alcancados]
            heapq.heapify(fila)
            while fila:
                dv, u = heapq.heappop(fila)
                if dv > dist.get(u, 1e18):
                    continue
                for v, c, e in adj[u]:
                    if dv + c < dist.get(v, 1e18):
                        dist[v] = dv + c
                        pai[v] = (u, e)
                        heapq.heappush(fila, (dv + c, v))
            for v in dem[d] - cobertura[d]:
                if v not in dist:
                    continue
                caminho, u = [], v
                while u in pai:
                    u, e = pai[u]
                    if e is not None:
                        caminho.append(e)
                if not caminho or tuple(sorted(caminho)) in vistos:
                    continue
                vistos.add(tuple(sorted(caminho)))
                custo = sum(cand[e] for e in caminho)
                if gasto + custo > B + 1e-9:
                    continue
                if K and any(uso[u] + sum(1 for e in caminho if e[0] == u) > K[u] for u in K):
                    continue
                ganho = cobertas(inst, esc + caminho) - atual
                if ganho <= 0:
                    continue
                chave = (ganho / custo, ganho)
                if melhor is None or chave > melhor[0]:
                    melhor = (chave, caminho, custo, ganho)
        if melhor is None:
            return esc
        _, caminho, custo, ganho = melhor
        for e in caminho:
            esc.append(e)
            uso[e[0]] += 1
        gasto += custo
        atual += ganho


def aleatorio(inst, B, amostras=200, semente=0):
    """Ordem aleatória das arestas, incluindo cada uma que ainda couber no orçamento.
    Devolve a lista de demandas atendidas em cada amostra."""
    nos, fonte, dem, ex, cand = inst
    rng = random.Random(semente)
    arestas = list(cand)
    saida = []
    for _ in range(amostras):
        rng.shuffle(arestas)
        gasto, esc = 0.0, []
        for e in arestas:
            if gasto + cand[e] <= B:
                esc.append(e)
                gasto += cand[e]
        saida.append(cobertas(inst, esc))
    return saida


# ----------------------------------------------------------------------------
# Instâncias sintéticas de tamanho variável (para o gráfico de escalabilidade)
# ----------------------------------------------------------------------------
def instancia_sintetica(n, semente=0):
    """Mesma estrutura dos CSV de exemplo: árvore dirigida + arestas de retorno, 2 a 3 especialistas
    por disciplina, nº de disciplinas proporcional ao nº de pessoas."""
    rng = random.Random(semente)
    n_disc = max(2, n // 10)
    cand, prox, fila = {}, 2, [1]
    while prox <= n:
        p = fila.pop(0)
        for _ in range(rng.choice([2, 2, 3])):
            if prox > n:
                break
            cand[(p, prox)] = round(rng.uniform(18, 40), 2)
            fila.append(prox)
            prox += 1
    while len(cand) < int(1.55 * n):
        u, v = rng.randint(min(8, n), n), rng.randint(1, n)
        if u != v and (u, v) not in cand:
            cand[(u, v)] = round(rng.uniform(24, 47), 2)
    topo = list(range(2, max(8, n // 2)))
    fonte = {d: set(rng.sample(topo, rng.choice([2, 3]))) for d in range(1, n_disc + 1)}
    esp = set().union(*fonte.values())
    dem = {d: set() for d in fonte}
    for v in range(1, n + 1):
        if v in esp:
            continue
        for d in rng.sample(sorted(fonte), rng.choice([1, 2, 2, 3] if n_disc >= 3 else [1, 2])):
            dem[d].add(v)
    return list(range(1, n + 1)), fonte, dem, [], cand
