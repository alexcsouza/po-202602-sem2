from gurobi_optimods import datasets
from gurobi_optimods.max_flow import max_flow
from gurobi_optimods.min_cut import min_cut


edge_data, _ = datasets.simple_graph_pandas()
print(edge_data[["capacity"]])

obj, flow = max_flow(edge_data, 0, 5, verbose=False) # Find max-flow between nodes 0 and 5
print(obj)

res = min_cut(edge_data, 0, 5, verbose=False)
print(res)

