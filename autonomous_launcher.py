#!/usr/bin/env python3
"""
Autonomous Launcher Wrapper for UX-MIRROR

This script creates a per-session results directory, starts the Phase 2
`ux_mirror_autonomous/run_tests.py` runner, and streams/captures its output so
that all artefacts, discoveries, and unit outputs are grouped together in a
single, timestamped location.  It also exposes a simple hook mechanism that
other tooling (e.g. an LLM agent) can subscribe to by importing
`register_hook()`.

Usage (PowerShell/CMD):

    python autonomous_launcher.py --suite basic

The launcher will automatically detect the project root and ensure the
underlying runner is executed from that location.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import subprocess as _sp
import sys
import threading
from pathlib import Path
from typing import Callable, List

# -------------------------------------------------------------
# Constants & helpers
# -------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
AUTONOMOUS_DIR = PROJECT_ROOT / "ux_mirror_autonomous"
RUNNER = AUTONOMOUS_DIR / "run_tests.py"
RESULTS_BASE = PROJECT_ROOT / "ux_results"
HOOKS: List[Callable[[str], None]] = []  # Simple line-level hooks

# Force UTF-8 console on Windows to avoid emoji encode errors
if os.name == "nt":
    try:
        os.system("chcp 65001 >nul")  # switch code page silently
    except Exception:
        pass

def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def register_hook(cb: Callable[[str], None]) -> None:
    """Register a callback that receives each output line from the runner."""
    HOOKS.append(cb)


# -------------------------------------------------------------
# Core launching logic
# -------------------------------------------------------------


def main(argv: List[str] | None = None) -> None:  # noqa: C901 (keep single fn)
    parser = argparse.ArgumentParser(description="UX-MIRROR autonomous launcher")
    parser.add_argument(
        "--suite",
        default="basic",
        choices=["basic", "full", "performance", "game_logic", "stress"],
        help="Test suite to run (passed through to run_tests.py)",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        help="Specific categories to include (optional)",
    )
    parser.add_argument(
        "--priority",
        type=int,
        choices=[1, 2, 3],
        help="Maximum priority level to run (optional)",
    )
    parser.add_argument(
        "--sentinel",
        action="store_true",
        help="Emit a sentinel line at the very end so external agents can react",
    )
    parser.add_argument(
        "--game-exe",
        type=str,
        help="Path to game executable (overrides default detection)",
    )
    args = parser.parse_args(argv)

    # Verify runner exists
    if not RUNNER.exists():
        print(f"❌ Autonomous runner not found: {RUNNER}")
        sys.exit(1)

    # Create session directory
    session_ts = _timestamp()
    session_dir = RESULTS_BASE / session_ts
    logs_dir = session_dir / "logs"
    session_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Environment variables for downstream tools
    env = os.environ.copy()
    env["UX_SESSION_DIR"] = str(session_dir)
    # Ensure package imports resolve and Unicode prints work
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = env.get("PYTHONIOENCODING", "utf-8")

    if args.game_exe:
        env["UX_GAME_EXE"] = args.game_exe

    # Build runner command
    cmd = [
        sys.executable,
        str(RUNNER),
        "--suite",
        args.suite,
    ]
    if args.categories:
        cmd += ["--categories", *args.categories]
    if args.priority is not None:
        cmd += ["--priority", str(args.priority)]

    log_path = logs_dir / "runner_output.log"
    print("🚀 Starting autonomous testing session")
    print(f"📂 Session directory: {session_dir}\n")

    with open(log_path, "w", encoding="utf-8") as log_file:
        proc = _sp.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=_sp.PIPE,
            stderr=_sp.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",  # avoid crashes on unexpected bytes
            bufsize=1,
        )

        def _stream_output() -> None:
            assert proc.stdout is not None  # for type checker
            for line in proc.stdout:
                sys.stdout.write(line)
                log_file.write(line)
                for cb in HOOKS:
                    try:
                        cb(line)
                    except Exception:  # noqa: BLE001 (safety – hooks must not crash main)
                        pass

        t = threading.Thread(target=_stream_output, daemon=True)
        t.start()
        proc.wait()
        t.join()

    exit_code = proc.returncode if proc.returncode is not None else -1
    print("\n⏹️  Runner finished with code", exit_code)
    print("📑  Log saved to", log_path)

    if exit_code != 0:
        sys.exit(exit_code)

    if args.sentinel:
        # Emit easily-detectable sentinel line for external tools.
        print("<<<SENTINEL>>> well how did it go")


if __name__ == "__main__":
    main() 