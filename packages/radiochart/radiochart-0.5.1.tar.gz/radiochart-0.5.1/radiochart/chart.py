from graphviz import Digraph
from datetime import datetime
import colorsys
import hashlib


def build_chart(data, output_path, colorize=True, timestamp=False):
    graph = Digraph(format=output_path.suffix.lstrip("."), strict=True)
    graph.attr("node", shape="box", style="filled", color="black", fontname="Arial", fontsize="10")

    squad_colors = {}

    def get_color(squad_name):
        if squad_name in squad_colors:
            return squad_colors[squad_name]

        # Generate a pastel color based on a hash of the squad name
        hash_val = int(hashlib.md5(squad_name.encode()).hexdigest(), 16)
        hue = (hash_val % 360) / 360.0
        rgb = colorsys.hsv_to_rgb(hue, 0.5, 0.95)
        hex_color = "#%02x%02x%02x" % tuple(int(c * 255) for c in rgb)
        squad_colors[squad_name] = hex_color
        return hex_color

    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def get_font_color(bg_hex_color):
        r, g, b = hex_to_rgb(bg_hex_color)
        # Calculate relative luminance per ITU-R BT.709 formula
        luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
        return 'white' if luminance < 0.5 else 'black'

    def walk(node_data, parent=None, parent_squad=None):
        for name, children in node_data.items():
            current_squad = parent_squad
            if "Squad" in name:
                current_squad = name

            if colorize:
                color_key = name if "Squad" in name else current_squad or name
                fill = get_color(color_key)
                fontcolor = get_font_color(fill)
                graph.node(name, fillcolor=fill, fontcolor=fontcolor)
            else:
                graph.node(name)

            if parent:
                graph.edge(parent, name)

            walk(children, parent=name, parent_squad=current_squad)

    walk(data)

    if timestamp:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        graph.attr(label=f"Generated {now}", fontsize="8", fontcolor="gray", labelloc="bottom")

    graph.render(output_path.with_suffix(""), cleanup=True)