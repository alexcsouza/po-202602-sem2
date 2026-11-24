"""

dados:
  funcionarios.csv   id, text (nome), list     -> nós do grafo (100 pessoas)
  especialistas.csv  id, text (nome), list     -> list = ids das disciplinas que o especialista
                                                  domina (uma disciplina pode ter vários
                                                  especialistas). O nó dele é ligado a
                                                  funcionarios.csv pelo nome
  demandantes.csv    id, text (nome), list     -> list = ids das disciplinas de que o
                                                  demandante precisa
  arestas.csv        origem, destino, custo    -> arestas candidatas (ids de funcionarios.csv);
                                                  o conhecimento flui de origem para destino

Problema: com orçamento B, ativar arestas para maximizar o nº de demandas (demandante,
disciplina) atendidas, isto é, pares em que existe caminho de QUALQUER especialista da
disciplina até o demandante usando só arestas ativadas. Sem limite de saltos.

Formulação por fluxo, um fluxo por disciplina d (fontes S_d, demandantes D_d):
    max   sum_d sum_{v in D_d} w * r[d,v]
    s.a.  sum_e c_e x_e <= B
          sum_{e saindo de u} x_e <= K_u                      (se K_u for definido)
          fluxo que entra em v - fluxo que sai de v = r[d,v]  para v fora de S_d
          (os nós de S_d são fontes com oferta ilimitada)
          f[d,a] <= M_d * x_a      (arestas candidatas)
          f[d,a] <= M_d            (arestas já existentes, se houver)
          x_e binária, 0 <= r <= 1, f >= 0,   M_d = |D_d|
"""

import csv
from collections import defaultdict
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

RAIZ = Path(__file__).resolve().parents[2]     # raiz do projeto em src/ref
DATA = RAIZ / "data"


def ler(nome):
    with open(DATA / nome, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def ids_da_lista(texto):
    return [int(p) for p in texto.replace(";", ",").split(",") if p.strip()]


def carregar_dados():
    funcionarios = ler("funcionarios.csv")
    nomes = {r["text"].strip(): int(r["id"]) for r in funcionarios}
    if len(nomes) != len(funcionarios):
        raise ValueError("funcionarios.csv tem nomes repetidos; não dá para ligar as tabelas por nome")
    nos = [int(r["id"]) for r in funcionarios]

    def no_do(nome, arquivo):
        if nome.strip() not in nomes:
            raise ValueError(f"'{nome}' de {arquivo} não existe em funcionarios.csv")
        return nomes[nome.strip()]


    fonte = defaultdict(set)
    for r in ler("especialistas.csv"):
        no = no_do(r["text"], "especialistas.csv")
        discs = ids_da_lista(r["list"])
        if not discs:
            raise ValueError(f"especialista {r['text']} sem disciplina na coluna list")
        for d in discs:
            fonte[d].add(no)


    demandas = defaultdict(set)
    for r in ler("demandantes.csv"):
        v = no_do(r["text"], "demandantes.csv")
        for d in ids_da_lista(r["list"]):
            if d not in fonte:
                raise ValueError(f"demandante {r['text']} cita disciplina sem especialista: {d}")
            if v not in fonte[d]:
                demandas[d].add(v)

    candidatas = {}
    for r in ler("arestas.csv"):
        u, v, c, p = int(r["origem"]), int(r["destino"]), float(r["custo"]), float(r["peso"])
        if u not in nomes.values() or v not in nomes.values():
            raise ValueError(f"aresta com nó desconhecido: {u} -> {v}")
        if u != v:
            candidatas[(u, v)] = {"custo": c, "peso": p}

    existentes = []        # os CSV não trazem rede existente; todas as arestas são candidatas
    return nos, dict(fonte), dict(demandas), existentes, candidatas



def alcancaveis(adj, origens):
    visto, pilha = set(origens), list(origens)
    while pilha:
        u = pilha.pop()
        for v in adj.get(u, ()):
            if v not in visto:
                visto.add(v)
                pilha.append(v)
    return visto


def adjacencia(arcos, reverso=False):
    adj = defaultdict(list)
    for u, v in arcos:
        if reverso:
            u, v = v, u
        adj[u].append(v)
    return adj


def construir(nos, fonte, demandas, existentes, candidatas, B, K=None, peso=1.0):
    K = K or {}
    todos = list(existentes) + list(candidatas)
    adj, adj_rev = adjacencia(todos), adjacencia(todos, reverso=True)

    m = gp.Model("max_coverage")
    x = m.addVars(sorted(candidatas), vtype=GRB.BINARY, name="x")
    p = m.addVars(sorted(candidatas), vtype=GRB.BINARY, name="p")
    m.addConstr(gp.quicksum(candidatas[e]["custo"] * x[e] for e in x) <= B, "orcamento")
    m.addConstr(gp.quicksum(candidatas[e]["peso"]  * p[e] for e in p) >= 4, f"criticidade")
    
    for u, limite in K.items():
        saindo = [e for e in candidatas if e[0] == u]
        if saindo:
            m.addConstr(gp.quicksum(x[e] for e in saindo) <= limite, f"cap_{u}")
            # m.addConstr(gp.quicksum(p[e] for e in saindo) >= 0.3, f"peso_{u}")

    objetivo = gp.LinExpr()
    r = {}
    for d in sorted(demandas):
        S = fonte[d]
        # só importa o que sai dos especialistas e consegue chegar a algum demandante de d
        da_fonte = alcancaveis(adj, S)
        ate_dem = alcancaveis(adj_rev, demandas[d])
        dem = [v for v in sorted(demandas[d]) if v in da_fonte]
        arcos = [a for a in todos if a[0] in da_fonte and a[1] in ate_dem and a[1] not in S]
        if not dem:
            continue
        M = len(dem)

        f = {a: m.addVar(lb=0.0, ub=float(M), name=f"f[{d},{a[0]},{a[1]}]") for a in arcos}
        for a in arcos:
            if a in candidatas:
                m.addConstr(f[a] <= M * x[a], f"liga[{d},{a[0]},{a[1]}]")
        for v in dem:
            r[d, v] = m.addVar(lb=0.0, ub=1.0, name=f"r[{d},{v}]")
            objetivo += peso * r[d, v]
            # objetivo += candidatas[a]["peso"] * r[d, v]
            
        entra, sai = defaultdict(list), defaultdict(list)
        for a in arcos:
            sai[a[0]].append(f[a])
            entra[a[1]].append(f[a])
        for v in set(entra) | set(sai) | set(dem):
            if v in S:
                continue
            m.addConstr(gp.quicksum(entra[v]) - gp.quicksum(sai[v]) == (r[d, v] if (d, v) in r else 0),
                        f"conserva[{d},{v}]")

    m.setObjective(objetivo, GRB.MAXIMIZE)
    m.update()
    return m, x, r


def cobertura(fonte, demandas, existentes, escolhidas):

    adj = adjacencia(list(existentes) + list(escolhidas))
    return {d: demandas[d] & alcancaveis(adj, fonte[d]) for d in demandas}



def main(B, TEMPO_S, GAP, K, PESO, dados, options):
    nos, fonte, demandas, existentes, candidatas = dados 
    total = sum(len(v) for v in demandas.values())
    n_esp = len(set().union(*fonte.values()))
    print(f"{len(nos)} nós | {len(fonte)} disciplinas | {n_esp} especialistas | "
          f"{total} demandas (demandante, disciplina) "
          f"| {len(candidatas)} arestas candidatas | B = {B:g}")

    m, x, r = construir(nos, fonte, demandas, existentes, candidatas, B, K, PESO)
    m.Params.TimeLimit = TEMPO_S
    m.Params.MIPGap = GAP
    print(f"modelo: {m.NumVars} variáveis ({m.NumBinVars} binárias), {m.NumConstrs} restrições")
    try:
        m.optimize()
    except gp.GurobiError as erro:
        raise SystemExit(f"Gurobi não conseguiu resolver: {erro}\n"
                         "A licença gratuita limita o modelo a 2000 variáveis e 2000 restrições; "
                         "com este tamanho é preciso licença acadêmica ou comercial.")

    if m.SolCount == 0:
        raise RuntimeError(f"sem solução (status {m.Status})")
    escolhidas = [e for e in x if x[e].X > 0.5]
    cob = cobertura(fonte, demandas, existentes, escolhidas)
    cobertas = sum(len(v) for v in cob.values())
    custo = sum(candidatas[e]["custo"] for e in escolhidas)
    peso = sum(candidatas[e]["peso"] for e in escolhidas)
    limite_superior = m.ObjBound
    print(f"\nstatus: {'ÓTIMO' if m.Status == GRB.OPTIMAL else 'VIÁVEL (limite de tempo)'}"
          f" | limite superior {limite_superior:.2f}")
    print(f"arestas ativadas: {len(escolhidas)} | custo {custo:.2f}/ peso {peso:.2f}  / B = {B:g}")
    print(f"demandas cobertas: {cobertas} de {total}  (Gurobi: {m.ObjVal / PESO:.0f})")
    print(f"{'disciplina':<12}{'especialistas':>14}{'demandas':>10}{'cobertas':>10}")
    for d in sorted(demandas):
        print(f"{d:<12}{len(fonte[d]):>14}{len(demandas[d]):>10}{len(cob[d]):>10}")

    pasta = RAIZ / "resultados"
    pasta.mkdir(exist_ok=True)
    with open(pasta / "arestas_escolhidas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origem", "destino", "custo"])
        for u, v in sorted(escolhidas):
            w.writerow([u, v, candidatas[u, v]])
    print(f"\nsalvo em {pasta / 'arestas_escolhidas.csv'}")
    return {
        "escolhidas": escolhidas,
        "cobertas": cobertas,
        "total": total,
        "limite_superior": limite_superior
    }

if __name__ == "__main__":
    main()