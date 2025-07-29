import argparse
import json
from graphviz import Digraph
import os
import itertools

# Predefined colors for squads
SQUAD_COLORS = [
    "lightblue",
    "lightgreen",
    "lightyellow",
    "lightpink",
    "lightcyan",
    "lightsalmon",
    "lightgray"
]

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def is_squad(name):
    return "Squad" in name

def build_graph(tree, graph=None, parent=None, squad_color=None, color_cycle=None):
    if graph is None:
        graph = Digraph(format='png')
        # Only set default shape and font globally — no fillcolor here!
        graph.attr('node', shape='box', fontname='Arial')

    if color_cycle is None:
        color_cycle = itertools.cycle(SQUAD_COLORS)

    for node, children in tree.items():
        # Assign color for squads and their children
        if is_squad(node):
            squad_color = next(color_cycle)

        fillcolor = squad_color if squad_color else "white"
        # Set fillcolor and style per node (style='filled' enables fillcolor)
        graph.node(node, style='filled', fillcolor=fillcolor)

        if parent:
            graph.edge(parent, node)

        # Pass the squad color down to children if applicable
        build_graph(children, graph, node, squad_color, color_cycle)

    return graph

def main():
    parser = argparse.ArgumentParser(description="Generate a hierarchical radio chart from a JSON file")
    parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    parser.add_argument('--output', '-o', default='radio_chart.png', help='Output image file name')
    args = parser.parse_args()

    data = load_json(args.input)
    graph = build_graph(data)

    output_path = os.path.splitext(args.output)[0]
    graph.render(output_path, cleanup=True)
    print(f"✅ Chart saved as {output_path}.png")

if __name__ == "__main__":
    main()
