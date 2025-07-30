import os
import subprocess


def test_cli_runs_and_prints_logo():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cli_path = os.path.join(project_root, "src", "goblin", "cli.py")

    result = subprocess.run(
        ["python3", cli_path, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=project_root,  # Run from project root so relative paths work
        env={**os.environ, "PYTHONPATH": project_root}
    )

    assert result.returncode == 0, f"Failed with stderr:\n{result.stderr}"
    assert "Goblin CLI" in result.stdout
    assert "analyze" in result.stdout