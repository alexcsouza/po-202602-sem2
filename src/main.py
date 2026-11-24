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
from ref.grapho import *
from ref.gurobi_max_coverage import *

import time
import csv
from configparser import ConfigParser  # ver. < 3.0

# instantiate
config = ConfigParser()

# parse existing file
config.read('gurobi.lic')
options = {
    "WLSACCESSID": config.get("license",'WLSACCESSID'),
    "WLSSECRET": config.get("license",'WLSACCESSID'),
    "LICENSEID": config.getint("license",'LICENSEID'),
}

# Pasta de dados
csv_base_path = Path('./data/')

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






B = 200.0              # orçamento total de ativação (mesma unidade da coluna custo)
TEMPO_S = 300          # limite de tempo do solver
GAP = 1e-4
K = {}                 # máx. de arestas novas saindo de um nó, ex.: {7: 1}; vazio = sem limite
PESO = 1.0             # criticidade de cada demanda (não há coluna de peso nos CSV)

dados = carregar_dados()

nos, fonte, demandas, existentes, candidatas = dados

#with gp.Env(params=options) as env, gp.Model(env=env) as m:
resultado = main(B, TEMPO_S, GAP, K, PESO, dados, options)



# arestas = gerar_arestas(funcionarios)
# nos = [(u) for (u, v, d) in funcionarios] 
# marcados = [1, 90, 10]
# gerar_grafo(arestas, nos, marcados)
# 
# 
# # Example inputs
# weights = np.random.randint(low=1, high=10, size=(len(nos)))
# pprint(weights)
# subsets = {f'{i}': row[2] for i, row in enumerate(funcionarios)}
# max_select = 30
# 
# # Map each element to the subsets that cover it
# covering_subsets = {
#     i: [j for j, elems in subsets.items() if i in elems] for i in nos
# }
# 
# model = gp.Model("max_coverage")
# 
# x = model.addVars(subsets.keys(), vtype=GRB.BINARY, name="x")
# y = model.addVars(nos, vtype=GRB.BINARY, name="y")
# 
# model.setObjective(
#     gp.quicksum(weights[int(i)] * y[i] for i in nos), GRB.MAXIMIZE
# )
# 
# model.addConstrs(
#     (y[i] <= gp.quicksum(x[j] for j in covering_subsets[i]) for i in nos),
#     name="cover",
# )
# 
# model.addConstr(gp.quicksum(x[j] for j in subsets) <= max_select, name="budget")
# 
# model.optimize()
# 
# if model.SolCount > 0:
#   selected = [j for j in subsets if x[j].X > 0.5]
#   covered = [i for i in nos if y[i].X > 0.5]
#   print("Selected subsets:", selected)
#   print("Covered nos:", covered)
#   print("Total covered weight:", model.ObjVal)
  

end = time.process_time()
print(f"\nTempo total: {end - start} segundos")
print(f"\n--- FIM ----")