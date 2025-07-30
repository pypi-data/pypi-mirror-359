import subprocess

def test_cli_runs_and_prints_logo():
    result = subprocess.run(
        ["python3", "cli/main.py", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    assert result.returncode == 0
    assert "Goblin CLI" in result.stdout
    assert "analyze" in result.stdout