from gurobi_optimods import datasets
from gurobi_optimods.max_flow import max_flow
from gurobi_optimods.min_cut import min_cut
from pathlib import Path
from pprint import pprint
import matplotlib.pyplot as plt
import networkx as nx

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


#G = nx.Graph()

# G = nx.balanced_tree(3, 5)
# elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]

G = nx.karate_club_graph()

for n in funcionarios:
    pprint(n)
    if n[2] == "":
        continue
    
    dem = n[2].rsplit(", ")
    for d in dem:
        pprint(f"{n[0]}->{d}")
        G.add_edge(n[0], d, weight=1 )
    
arestas = [(u, v) for (u, v, d) in G.edges(data=True)]

pprint(arestas)

# elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0.5]
# esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0.5]
    
# pos = nx.spring_layout(G, seed=100)  # positions for all nodes - seed for reproducibility
pos = nx.nx_agraph.graphviz_layout(G, prog="twopi", args="")


# nodes
nx.draw_networkx_nodes(G, pos, node_size=70)

# edges
nx.draw_networkx_edges(G, pos, edgelist=arestas, width=1)


# nx.draw_networkx_edges(
#     G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
# )

# node labels
nx.draw_networkx_labels(G, pos, font_size=9, font_family="sans-serif")
# edge weight labels
edge_labels = nx.get_edge_attributes(G, "critic")
nx.draw_networkx_edge_labels(G, pos, edge_labels)

nx.draw_circular(G, with_labels=True)

ax = plt.gca()
ax.margins(0.08)
plt.axis("off")
plt.tight_layout()
plt.savefig("./img/network-func.png")



end = time.process_time()
print(f"\nTempo total: {end - start} segundos")
print(f"\n--- FIM ----")