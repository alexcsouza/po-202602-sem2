from gurobi_optimods import datasets
from gurobi_optimods.max_flow import max_flow
from gurobi_optimods.min_cut import min_cut
from pathlib import Path
from pprint import pprint
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import gurobipy as gp
from gurobipy import GRB

import time
import csv


# Pasta de dados
csv_base_path = Path('./data/')

print(csv_base_path)


# Pasta de imagens
img_base_path = Path('./img/')

def load_list_csv(file_path):    
    file = open(file_path)
    reader = csv.reader(file)
    next(reader)
    return list(reader)


file_path_especialistas = f'{csv_base_path}/especialistas.csv'
especialistas = load_list_csv(file_path_especialistas)

file_path_demandantes = f'{csv_base_path}/demandantes.csv'
demandantes = load_list_csv(file_path_demandantes)

file_path_funcionarios = f'{csv_base_path}/funcionarios.csv'
funcionarios = load_list_csv(file_path_funcionarios)


start_total = time.process_time()
print(f"\n--- INÍCIO ---")
start = time.process_time()

pprint(especialistas)

pprint(demandantes)

pprint(funcionarios)


G = nx.DiGraph()

# G = nx.balanced_tree(3, 5)
# elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]

# G = nx.karate_club_graph()

# funcionarios = funcionarios[0:30]


for n in funcionarios:
    
    pprint(n)
    if n[2] == "":
        continue
    
    dem = n[2].rsplit(", ")
    n[2] = dem
    for d in dem:
        d = int(d)
        pprint(f"{n[0]}->{d}")
        G.add_edge(int(n[0]), int(d), weight=1 )
        
    
    
    

arestas = [(u, v) for (u, v, d) in G.edges(data=True)]

pprint(arestas)

# elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
# esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]
  
layers = dict(enumerate(nx.topological_generations(G)))
pos = nx.multipartite_layout(G, subset_key=layers)

# pos = nx.spring_layout(G, seed=100)  # positions for all nodes - seed for reproducibility
# pos = nx.nx_agraph.graphviz_layout(G, prog="twopi", args="")


# nodes
nx.draw_networkx_nodes(G, pos, node_size=60)

# edges
nx.draw_networkx_edges(G, pos, edgelist=arestas, width=1, arrows=True, arrowstyle="->")


# nx.draw_networkx_edges(
#     G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
# )

# node labels
nx.draw_networkx_labels(G, pos, font_size=5, font_family="sans-serif")

# edge weight labels
# edge_labels = nx.get_edge_attributes(G, "weight")
# nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=5)

# nx.draw_circular(G, with_labels=True)

ax = plt.gca()
ax.width = 1600
ax.height = 1200
ax.margins(0.08)
plt.axis("off")
# plt.tight_layout()
plt.savefig("./img/network-func.png")












# Example inputs
elements = [(u) for (u, v, d) in funcionarios]  # [0, 1, 2, 3, 4]
pprint(elements)
weights = np.random.randint(low=1, high=10, size=(len(elements)))
pprint(weights)
array_2d = np.array(G.edges())
subsets = {f'S{i}': row[2] for i, row in enumerate(funcionarios)}
pprint(subsets)
# subsets = {
#     "S1": [0, 1, 2],
#     "S2": [1, 3],
#     "S3": [2, 3, 4],
#     "S4": [0, 4],
# }
max_select = 30

# Map each element to the subsets that cover it
covering_subsets = {
    i: [j for j, elems in subsets.items() if i in elems] for i in elements
}

model = gp.Model("max_coverage")

x = model.addVars(subsets.keys(), vtype=GRB.BINARY, name="x")
y = model.addVars(elements, vtype=GRB.BINARY, name="y")

model.setObjective(
    gp.quicksum(weights[int(i)] * y[i] for i in elements), GRB.MAXIMIZE
)

model.addConstrs(
    (y[i] <= gp.quicksum(x[j] for j in covering_subsets[i]) for i in elements),
    name="cover",
)

model.addConstr(gp.quicksum(x[j] for j in subsets) <= max_select, name="budget")

model.optimize()

if model.SolCount > 0:
  selected = [j for j in subsets if x[j].X > 0.5]
  covered = [i for i in elements if y[i].X > 0.5]
  print("Selected subsets:", selected)
  print("Covered elements:", covered)
  print("Total covered weight:", model.ObjVal)







end = time.process_time()
print(f"\nTempo total: {end - start} segundos")
print(f"\n--- FIM ----")