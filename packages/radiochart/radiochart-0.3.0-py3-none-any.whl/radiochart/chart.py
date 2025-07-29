from graphviz import Digraph

SQUAD_COLORS = [
    "lightblue", "lightgreen", "lightyellow", "lightpink", "lightcyan", "lightsalmon", "lightgray"
]

def is_squad(name):
    return "Squad" in name

def generate_graph(data, parent=None, graph=None, color_map=None, color_idx=0):
    if graph is None:
        graph = Digraph(format="png")
        graph.attr("node", shape="box", style="filled", fontname="Arial")

    if color_map is None:
        color_map = {}

    for node, children in data.items():
        if is_squad(node) and node not in color_map:
            color_map[node] = SQUAD_COLORS[color_idx % len(SQUAD_COLORS)]
            color_idx += 1

        color = color_map.get(parent, color_map.get(node, "white"))
        graph.node(node, fillcolor=color)

        if parent:
            graph.edge(parent, node)

        generate_graph(children, node, graph, color_map, color_idx)

    return graph

def build_chart(data, output_path):
    graph = generate_graph(data)
    graph.render(output_path, cleanup=True)