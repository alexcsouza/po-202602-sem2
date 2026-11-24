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


# file_path_especialistas = f'{csv_base_path}/especialistas.csv'
# especialistas = load_list_csv(file_path_especialistas)
# 
# file_path_demandantes = f'{csv_base_path}/demandantes.csv'
# demandantes = load_list_csv(file_path_demandantes)
# 
# file_path_funcionarios = f'{csv_base_path}/funcionarios.csv'
# funcionarios = load_list_csv(file_path_funcionarios)


start_total = time.process_time()
print(f"\n--- INÍCIO ---")
start = time.process_time()

B = 1000.0              # orçamento total de ativação (mesma unidade da coluna custo)
TEMPO_S = 300          # limite de tempo do solver
GAP = 1e-4
K = {}                 # máx. de arestas novas saindo de um nó, ex.: {7: 1}; vazio = sem limite
PESO = 1.0             # criticidade de cada demanda (não há coluna de peso nos CSV)

dados = carregar_dados("1")
nos, fonte, demandas, existentes, candidatas = dados
gerar_grafo(candidatas.keys(), nos, [], "1-rede")
resultado = main(B, TEMPO_S, GAP, K, PESO, dados, options, "1")
gerar_grafo(candidatas.keys(), nos, resultado["escolhidas"], "1-resultado")

dados = carregar_dados("2")
pprint(dados)
nos, fonte, demandas, existentes, candidatas = dados
gerar_grafo(candidatas.keys(),nos, [], "2-rede")
resultado = main(B, TEMPO_S, GAP, K, PESO, dados, options, "2")
gerar_grafo(candidatas.keys(), nos, resultado["escolhidas"], "2-resultado")



end = time.process_time()
print(f"\nTempo total: {end - start} segundos")
print(f"\n--- FIM ----")