import argparse
import json
from graphviz import Digraph
import os

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def build_graph(tree, graph=None, parent=None):
    if graph is None:
        graph = Digraph(format='png')
        graph.attr('node', shape='box', style='filled', fillcolor='lightgrey', fontname='Arial')

    for node, children in tree.items():
        graph.node(node)
        if parent:
            graph.edge(parent, node)
        build_graph(children, graph, node)

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
