import subprocess
import sys


def test_cli_basic():
    cmd = [sys.executable, "-m", "dabeaz.cli", "--nodes", "3"]
    script = "set a 1\nget a\ndelete a\nget a\nquit\n"
    result = subprocess.run(
        cmd, input=script, text=True, capture_output=True, check=True
    )
    lines = [line for line in result.stdout.strip().splitlines()]
    assert lines == ["1"]
