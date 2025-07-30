import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

import toml
from rich.console import Console
from rich.panel import Panel

from goblin.analyzer import parse_java_file
from goblin.ascii_logo import GOBLIN_LOGO
from goblin.config import load_config
from goblin.shame_o_meter import shame_insult
from goblin.smell_types import SmellType

console = Console()

def analyze_folder(folder_path: str, json_output=False, ignored_smells=None, short_response=False):
    java_files = []
    results = []
    ignored_smells = ignored_smells or []
    ignored_set = set()
    analyzed = 0
    failed = 0

    for ignore in ignored_smells:
        try:
            normalized = ignore.replace("-", "_").upper()
            ignored_set.add(SmellType[normalized])
        except KeyError:
            console.print(f"[red]⚠️ Unknown smell type to ignore: {ignore}[/red]")
            SmellType.print_available_smell_types()
            sys.exit(1)

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
                file_path = os.path.join(root, file)
                try:
                    test_class = parse_java_file(file_path)
                    results.append({
                        "file": file_path,
                        "class": test_class.class_name,
                        "methods": [asdict(m) for m in test_class.methods]
                    })
                    analyzed += 1
                except Exception as e:
                    results.append({
                        "file": file_path,
                        "error": str(e)
                    })
                    failed += 1

    if not java_files:
        console.print("[red]No Java files found in the specified path.[/red]")
        sys.exit(1)
    else:
        console.print(
            f"[bold magenta]• Total files:[/] [cyan]{len(java_files)}[/] "
            f"• [green]✅ Loaded:[/] [bold green]{analyzed}[/] "
            f"• [red]❌ Failed:[/] [bold red]{failed}[/]"
        )

    if json_output:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            if "error" in r:
                print(f"\n📂❌ Failed to parse {r['file']} due to {r['error'] if r['error'] else 'Java syntax issues'}")
                continue
            
            console.print(f"📂 [bold cyan]Analyzing:[/] {r['file']}")
            clean = 0
            smelly = 0
            for method in r["methods"]:
                method["smells"] = [smell for smell in method["smells"] if smell not in ignored_set]
                if method["smells"]:
                    smelly += 1
                    if not short_response:
                        console.print(f"   🧪 [bold]{method['method_name']}[/]", style="yellow")
                        console.print("      👹 [bold red]Smells detected![/]")
                        for smell in method["smells"]:
                            print(f"         - {smell.value}")
                else:
                    clean += 1
                    console.print(f"   🧪 [green]{method['method_name']}[/] – [bold green]Clean![/]")
            console.print(Panel.fit(
                f"📊 Files Processed: {len(java_files)}\n✅ Analyzed: {analyzed}\n❌ Failed: {failed}\n🧪 Methods: {len(r['methods'])}\n😇 Clean: {clean}\n👹 Smelly: {smelly}",
                title="Goblin File Summary",
                border_style="blue")
            )
            console.print(f"\n[italic red]{shame_insult(smelly, len(r['methods']))}[/]")

def get_version():
    current_dir = Path(__file__).resolve()
    for parent in current_dir.parents:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            data = toml.load(pyproject)
            return data["project"]["version"]
    raise RuntimeError("Error during version retrieval")

def main():
    console.print(GOBLIN_LOGO, style="green")
    parser = argparse.ArgumentParser(
        prog="goblin",
        description="Goblin: A simple unit test runner for Python projects.",
        epilog="Examples:\n  goblin analyze ./examples\n  goblin --version\n  goblin --help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="store_true", help="Show Goblin CLI version")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze Java test files")
    analyze_parser.add_argument("path", nargs="?", help="Path to folder with .java files")
    analyze_parser.add_argument("--json", action="store_true", help="Output results as JSON")
    analyze_parser.add_argument("--ignore", nargs="+", help="List of smell types to ignore (e.g., no-assertions disabled)")
    analyze_parser.add_argument("--short", action="store_true", help="Short output format, only show file names and final report")

    args = parser.parse_args()

    if args.version:
        try:
            version = get_version()
            print(f"Goblin CLI version: {version}")
            sys.exit(0)
        except RuntimeError as e:
            print(e)
            sys.exit(1)
    elif args.command == "analyze":
        # Import config and load defaults if needed
        config = load_config()

        path = args.path if args.path else config.get("default_path")
        ignored = args.ignore if args.ignore else config.get("ignored_smells", [])
        json_output = args.json if args.json else config.get("json", False)
        short_response = args.short if args.short else config.get("short_response", False)

        if not path:
            console.print("[red]Error: No path specified and no default path found in config.[/red]")
            sys.exit(1)

        analyze_folder(path, json_output=json_output, ignored_smells=ignored, short_response=short_response)
        sys.exit(0)
    elif args.command is None:
        console.print("[red]Error: No subcommand provided. Use '--help' to see available commands.[/red]")
        parser.print_help()
        sys.exit(1)
    else:
        parser.print_help()
if __name__ == "__main__":
    main()