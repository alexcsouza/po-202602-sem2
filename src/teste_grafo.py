import networkx as nx

import networkx as nx
import matplotlib.pyplot as plt

arestas = [
    (1, 2, 37.05),
    (1, 3, 36.85),
    (2, 4, 27.94),
    (2, 5, 36.81),
    (3, 6, 22.06),
    (3, 7, 29.26),
    (4, 8, 31.51),
    (4, 9, 22.1),
    (4, 10, 27.83),
    (5, 11, 19.99),
    (5, 12, 35.81),
    (6, 13, 31.96),
    (6, 14, 31.1),
    (6, 15, 26.72),
    (7, 16, 32.39),
    (7, 17, 31.54),
    (8, 18, 31.71),
    (8, 19, 36.3),
    (9, 14, 28.31),
    (9, 20, 19.31),
    (9, 21, 22.18),
    (10, 22, 31.19),
    (10, 23, 35.12),
    (11, 3, 28.05),
    (11, 24, 27.69),
    (11, 25, 36.53),
    (12, 9, 29.25),
    (12, 26, 23.14),
    (12, 27, 24.47),
    (12, 28, 18.1),
    (13, 14, 37.4),
    (13, 27, 25.09),
    (13, 29, 28.06),
    (13, 30, 24.12),
    (14, 3, 35.78),
    (14, 31, 39.91),
    (14, 32, 36.48),
    (14, 33, 33.57),
    (15, 34, 34.68),
    (15, 35, 29.28),
    (16, 6, 32.33),
    (16, 36, 19.54),
    (16, 37, 34.86),
    (16, 56, 32.88),
    (17, 38, 20.37),
    (17, 39, 24.4),
    (18, 40, 39.08),
    (18, 41, 36.64),
    (19, 42, 22.7),
    (19, 43, 38.39),
    (19, 60, 40.57),
    (20, 44, 28.34),
    (20, 45, 39.57),
    (21, 1, 30.21),
    (21, 29, 29.94),
    (21, 46, 27.24),
    (21, 47, 30.46),
    (21, 48, 24.38),
    (22, 48, 35.13),
    (22, 49, 23.94),
    (22, 53, 38.04),
    (23, 1, 37.83),
    (23, 50, 24.85),
    (23, 51, 18.33),
    (24, 16, 41.02),
]

G = nx.DiGraph()
G.add_weighted_edges_from(arestas)

# ... (código anterior que cria o grafo G) ...

# 1. Define o layout (posição dos nós)
# O spring_layout é um dos mais utilizados e evita sobreposição de nós.
pos = nx.spring_layout(G, seed=42)

# 2. Desenha os elementos do grafo
plt.figure(figsize=(15, 12)) # Define o tamanho da imagem

# Desenha os nós
nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')

# Desenha as arestas (com setas, pois é um grafo direcionado)
nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)

# Desenha os rótulos dos nós
nx.draw_networkx_labels(G, pos, font_size=10)

# 3. Adiciona os pesos das arestas como rótulos
edge_labels = nx.get_edge_attributes(G, 'weight')
# Formata os pesos para duas casas decimais para não poluir a imagem
edge_labels = {k: f"{v:.2f}" for k, v in edge_labels.items()}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

# 4. Finaliza e salva a imagem
plt.title("Grafo Direcionado e Ponderado")
plt.axis('off') # Remove os eixos (opcional, deixa o grafo mais limpo)
plt.tight_layout() # Ajusta o layout para não cortar elementos

# Salva a imagem em um arquivo
plt.savefig('grafo_ponderado.png', dpi=300, bbox_inches='tight')


# Exemplo de acesso ao peso:
# G[1][2]["weight"]  # 37.05