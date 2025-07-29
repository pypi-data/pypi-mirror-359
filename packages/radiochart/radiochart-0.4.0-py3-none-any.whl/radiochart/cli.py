import sys
import json
import os
from pathlib import Path

from rich import print
from rich.console import Console
from rich.spinner import Spinner
from InquirerPy import inquirer
from radiochart.chart import build_chart

console = Console()


def main():
    if len(sys.argv) < 2:
        print("[bold red]Error:[/bold red] You must specify a JSON input file.")
        print("Usage: [bold]radiochart net_structure.json[/bold]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"[bold red]Error:[/bold red] File '{input_path}' does not exist.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[bold red]Invalid JSON:[/bold red] {e}")
            sys.exit(1)

    # === Interactive Options ===
    file_stem = inquirer.text(
        message="Enter output file name (without extension):", default="chart"
    ).execute()

    file_ext = inquirer.select(
        message="Select output file format:",
        choices=["png", "jpg", "svg", "pdf"],
        default="png",
    ).execute()

    colorize = inquirer.confirm(
        message="Enable color-coded squads?", default=True
    ).execute()

    timestamp = inquirer.confirm(
        message="Include timestamp in chart?", default=False
    ).execute()

    # Fix double-extension if user includes ".ext"
    if file_stem.lower().endswith(f".{file_ext}"):
        output_filename = file_stem
    else:
        output_filename = f"{file_stem}.{file_ext}"

    output_path = Path(output_filename)

    # === Spinner and Build Chart ===
    with console.status("[bold green]Generating chart...[/bold green]", spinner="dots"):
        try:
            build_chart(data, output_path=output_path, colorize=colorize, timestamp=timestamp)
        except Exception as e:
            print(f"[bold red]Error generating chart:[/bold red] {e}")
            sys.exit(1)

    print(f"\n[bold green]Chart generated successfully![/bold green] 📡 → {output_path.resolve()}")