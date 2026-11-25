"""Gera todos os gráficos em resultados/graficos/.

    python src/graficos/gerar_todos.py              # todos
    python src/graficos/gerar_todos.py --sem-g4     # pula a escalabilidade (é a mais demorada)
    python src/graficos/gerar_todos.py g1 g5        # só os indicados
"""

import importlib
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

GRAFICOS = {
    "g1": "g1_cobertura_vs_orcamento",
    "g2": "g2_cobertura_por_disciplina",
    "g3": "g3_limite_de_saltos",
    "g4": "g4_escalabilidade",
    "g5": "g5_ganho_por_aresta",
    "g6": "g6_rede_solucao",
}


def main(argv):
    pedidos = [a for a in argv if a in GRAFICOS] or list(GRAFICOS)
    if "--sem-g4" in argv and "g4" in pedidos:
        pedidos.remove("g4")
    falhas = []
    for chave in pedidos:
        print(f"\n=== {chave}: {GRAFICOS[chave]} ===")
        try:
            importlib.import_module(GRAFICOS[chave]).main()
        except Exception:
            traceback.print_exc()
            falhas.append(chave)
    if falhas:
        print(f"\nfalharam: {', '.join(falhas)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
