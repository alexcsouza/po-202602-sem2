import gurobipy as gp
from gurobipy import GRB

# Example inputs
elements = [0, 1, 2, 3, 4]
weights = {0: 10, 1: 20, 2: 15, 3: 25, 4: 30}
subsets = {
    "S1": [0, 1, 2],
    "S2": [1, 3],
    "S3": [2, 3, 4],
    "S4": [0, 4],
}
max_select = 2

# Map each element to the subsets that cover it
covering_subsets = {
    i: [j for j, elems in subsets.items() if i in elems] for i in elements
}

model = gp.Model("max_coverage")

x = model.addVars(subsets.keys(), vtype=GRB.BINARY, name="x")
y = model.addVars(elements, vtype=GRB.BINARY, name="y")

model.setObjective(
    gp.quicksum(weights[i] * y[i] for i in elements), GRB.MAXIMIZE
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
