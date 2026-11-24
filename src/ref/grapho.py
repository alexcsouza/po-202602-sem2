import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint

def get_data(m):
    # Suponha que 'm' seja seu modelo Gurobi já otimizado
    # m = gp.Model("max_coverage")
    # ... (construção do modelo) ...
    # m.optimize()

    # 1. Recupere todas as variáveis
    vars = m.getVars()

    # 2. Identifique os conjuntos a partir dos nomes das variáveis
    # (Isso depende da convenção de nomes que você usou ao criar as variáveis)
    # Exemplo: se você criou y[j] com name=f"y_{j}" e x[i] com name=f"x_{i}"
    instalacoes = set()
    clientes = set()
    for v in vars:
        if v.VarName.startswith("y_"):
            instalacoes.add(v.VarName.split("_")[1])
        elif v.VarName.startswith("x_"):
            clientes.add(v.VarName.split("_")[1])

    # 3. Recupere os valores da solução (após otimização)
    # O atributo .X contém o valor da variável na solução ótima
    solucao_y = {v.VarName: v.X for v in vars if v.VarName.startswith("y_")}
    solucao_x = {v.VarName: v.X for v in vars if v.VarName.startswith("x_")}

    return {"x": solucao_x, "y": solucao_y}

def generate_graph(m, clientes, instalacoes):
    G = nx.Graph()

    # Adicione os nós com atributos para diferenciá-los visualmente
    # Nós de instalação (bipartite=0)
    for j in instalacoes:
        G.add_node(f"y_{j}", bipartite=0, tipo="instalacao", label=f"Instalação {j}")   

    # Nós de cliente (bipartite=1)
    for i in clientes:
        G.add_node(f"x_{i}", bipartite=1, tipo="cliente", label=f"Cliente {i}") 

    # Adicione as arestas de cobertura.
    # Você pode extrair essa informação das restrições do Gurobi ou da matriz de cobertura original.
    # Se você tem a matriz 'a' (dicionário ou DataFrame) que define a_{ij}, use-a:
    # for i in clientes:
    #     for j in instalacoes:
    #         if a[i][j] == 1:  # Se a instalação j cobre o cliente i
    #             G.add_edge(f"y_{j}", f"x_{i}")    

    # Alternativa: extrair das restrições de cobertura do Gurobi.
    # As restrições de cobertura têm a forma: x[i] <= sum(y[j] for j in cobertura[i])
    # Você pode inspecionar o lado esquerdo (LHS) de cada restrição para encontrar quais variáveis y_ aparecem.
    for constr in m.getConstrs():
        if constr.ConstrName.startswith("cobertura_"):
            # O nome da restrição pode conter o índice do cliente, ex: "cobertura_0"
            i = constr.ConstrName.split("_")[1]
            # Obtenha a expressão linear da restriçãodata.y
            expr = m.getRow(constr)
            # Percorra os termos da expressão para encontrar as variáveis y_j
            for term in expr:
                var = term.getVar()
                if var.VarName.startswith("y_"):
                    j = var.VarName.split("_")[1]
                    G.add_edge(f"y_{j}", f"x_{i}")

    return G

def generate_graph_visualization(G, solucao_x, solucao_y):
    # Defina as posições usando o layout bipartido
    pos = nx.multipartite_layout(G, nodes=[n for n, d in G.nodes(data=True) if d['bipartite'] == 0])

    # Defina cores e tamanhos com base no tipo de nó e na solução
    cores = []
    tamanhos = []
    for node, data in G.nodes(data=True):
        if data['tipo'] == 'instalacao':
            # Destaque as instalações selecionadas na solução
            if solucao_y.get(node, 0) > 0.5:
                cores.append('gold')  # Instalação selecionada
                tamanhos.append(1000)
            else:
                cores.append('lightgray')  # Instalação não selecionada
                tamanhos.append(500)
        else:  # cliente
            # Destaque os clientes cobertos
            if solucao_x.get(node, 0) > 0.5:
                cores.append('skyblue')  # Cliente coberto
                tamanhos.append(500)
            else:
                cores.append('lightcoral')  # Cliente não coberto
                tamanhos.append(300)

    # Desenhe o grafo
    plt.figure(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, node_color=cores, node_size=tamanhos, alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, labels={n: d['label'] for n, d in G.nodes(data=True)}, font_size=10)

    plt.title("Visualização da Solução do Modelo de Cobertura Máxima", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    return plt


def gerar_arestas(funcionarios):

    edges = []
    for n in funcionarios:
            pprint(n)
            if n[2] == "":
                continue
            
            dem = n[2].rsplit(", ")
            n[2] = dem
            for d in dem:
                d = int(d)
                pprint(f"{n[0]}->{d}")
                edges.append((int(n[0]), int(d), 1))
    return edges

def gerar_grafo(arestas, nos, marcados):
    G = nx.DiGraph()
    node_colors = ["blue"] * (len(nos) - 1) 
    for u, v, w in arestas:
        G.add_edge(u, v, weight=w)
        if(u in marcados):
            node_colors[u] = 'red'

        if(v in marcados):
            node_colors[v] = 'red'
                        


    # arestas = [(u, v, w) for (u, v, w) in G.edges(data=True)]
    pprint(len(arestas))
    pprint(len(node_colors))    
    layers = dict(enumerate(nx.topological_generations(G)))
    pos = nx.multipartite_layout(G, subset_key=layers)

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=60, node_color=node_colors)
    
    # edges
    nx.draw_networkx_edges(G, pos, edgelist=arestas, width=1, arrows=True, arrowstyle="->")
    
    # node labels
    nx.draw_networkx_labels(G, pos, font_size=5, font_family="sans-serif")
    
    ax = plt.gca()
    ax.width = 1600
    ax.height = 1200
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("./img/network-func.png")