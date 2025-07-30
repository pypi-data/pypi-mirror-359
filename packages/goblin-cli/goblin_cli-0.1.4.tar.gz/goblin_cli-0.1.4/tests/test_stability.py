import os
import subprocess

import pytest


def run_command(args):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cli_path = os.path.join(project_root, "src", "goblin", "cli.py")

    result = subprocess.run(
        ["python3", cli_path] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=project_root,
        env={**os.environ, "PYTHONPATH": project_root}
    )

    print(f"\nCommand: {' '.join(args)}")
    print(f"Return Code: {result.returncode}")
    print("STDERR:\n", result.stderr)

    assert result.returncode == 0, f"Failed with stderr:\n{result.stderr}"

@pytest.mark.parametrize("args", [
    ["--version"],
    ["--help"],
    ["analyze", "examples"],
    ["analyze", "examples", "--short"],
    ["analyze", "examples", "--json"],
    ["analyze", "examples", "--ignore", "DISABLED_ANNOTATION"],
])
def test_all_variants(args):
    run_command(args)