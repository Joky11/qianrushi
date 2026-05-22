#!/usr/bin/env python3
import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def find_tool(name):
    java_home = os.environ.get("JAVA_HOME")
    exe_name = name + (".exe" if os.name == "nt" else "")

    if java_home:
        candidate = Path(java_home) / "bin" / exe_name
        if candidate.exists() and is_usable(candidate):
            return str(candidate)

    # Homebrew OpenJDK is often not linked into PATH on macOS.
    for base in (
        "/opt/homebrew/opt/openjdk/bin",
        "/opt/homebrew/opt/openjdk@21/bin",
        "/usr/local/opt/openjdk/bin",
        "/usr/local/opt/openjdk@21/bin",
    ):
        candidate = Path(base) / name
        if candidate.exists() and is_usable(candidate):
            return str(candidate)

    found = shutil.which(name)
    if found and is_usable(Path(found)):
        return found

    return name


def is_usable(path):
    try:
        completed = subprocess.run(
            [str(path), "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=5,
            check=False,
        )
        return completed.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


class TeeLogger:
    def __init__(self, path):
        self.file = open(path, "w", encoding="utf-8") if path else None

    def write(self, text=""):
        print(text)
        if self.file:
            self.file.write(text + "\n")
            self.file.flush()

    def close(self):
        if self.file:
            self.file.close()


def command_output(command, cwd):
    completed = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Run the Java deadlock demo repeatedly.")
    parser.add_argument("--runs", type=int, default=100, help="number of runs")
    parser.add_argument("--timeout", type=float, default=3.0, help="timeout seconds per run")
    parser.add_argument("--workdir", type=Path, default=script_dir, help="directory containing Java files")
    parser.add_argument("--log", type=Path, default=script_dir / "run_python.log", help="log file path")
    args = parser.parse_args()

    workdir = args.workdir.resolve()
    logger = TeeLogger(args.log)
    java = find_tool("java")
    javac = find_tool("javac")

    try:
        logger.write("=== Deadlock cross-platform test ===")
        logger.write(f"Platform: {platform.platform()}")
        logger.write(f"Machine : {platform.machine()}")
        logger.write(f"Python  : {platform.python_version()}")

        _, java_version = command_output([java, "-version"], workdir)
        logger.write(f"Java    : {java_version.splitlines()[0] if java_version else java}")
        logger.write(f"Runs    : {args.runs}")
        logger.write(f"Timeout : {args.timeout:g}s")
        logger.write("")

        compile_cmd = [javac, "Deadlock.java", "A.java", "B.java"]
        code, output = command_output(compile_cmd, workdir)
        if code != 0:
            logger.write("Compile failed:")
            logger.write(output)
            return 2

        normal = 0
        deadlock = 0
        errors = 0

        for index in range(1, args.runs + 1):
            try:
                completed = subprocess.run(
                    [java, "Deadlock"],
                    cwd=workdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=args.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                deadlock += 1
                partial = (exc.stdout or "").strip()
                logger.write(f"[{index}] DEADLOCK (timeout)")
                if partial:
                    logger.write(partial)
                continue

            output = completed.stdout.strip()
            if completed.returncode == 0:
                normal += 1
                logger.write(f"[{index}] OK")
                if output:
                    logger.write(output)
            else:
                errors += 1
                logger.write(f"[{index}] ERROR exit={completed.returncode}")
                if output:
                    logger.write(output)

        rate = deadlock * 100 / args.runs if args.runs else 0
        logger.write("")
        logger.write("=== Summary ===")
        logger.write(f"Total     : {args.runs}")
        logger.write(f"Normal    : {normal}")
        logger.write(f"Deadlock  : {deadlock}")
        logger.write(f"Errors    : {errors}")
        logger.write(f"Rate      : {rate:.1f}%")

        return 2 if errors else 0
    finally:
        logger.close()


if __name__ == "__main__":
    sys.exit(main())
