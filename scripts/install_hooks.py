"""Install a git pre-commit hook that runs `pixi run -e dev check`."""

import stat
import subprocess
from pathlib import Path

HOOK = """#!/bin/sh
# Installed by `pixi run install-hooks`
exec pixi run -e dev check
"""


def main() -> None:
    hooks_dir = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    hook = Path(hooks_dir) / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(HOOK, newline="\n")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Installed pre-commit hook at {hook}")


if __name__ == "__main__":
    main()
