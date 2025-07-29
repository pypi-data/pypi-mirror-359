import sys
import json
import os
from InquirerPy import prompt
from rich.console import Console
from rich.spinner import Spinner
from .chart import build_chart

console = Console()

def main():
    # Require one positional argument (input JSON)
    if len(sys.argv) < 2:
        console.print("[red]Usage: radiochart <input_file.json>[/red]")
        sys.exit(1)

    input_path = sys.argv[1]

    if not os.path.isfile(input_path):
        console.print(f"[red]Error:[/red] File '{input_path}' not found.")
        sys.exit(1)

    # Interactive prompt for output file
    questions = [
        {
            "type": "input",
            "name": "output_path",
            "message": "Enter output image path:",
            "default": "chart.png"
        }
    ]
    answers = prompt(questions)
    output_path = answers["output_path"]

    # Spinner while generating
    with console.status("[bold green]Generating chart...[/bold green]", spinner="dots"):
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            build_chart(data, output_path)
            console.print(f"\n[bold green]✔ Chart saved to {output_path}[/bold green]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]✘ Failed to generate chart:[/bold red] {e}")
            sys.exit(1)