from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent


def run_step(script_name):
    script_path = PROJECT_ROOT / "src" / script_name

    print(f"\nRunning: {sys.executable} {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        text=True,
    )

    if result.returncode != 0:
        raise SystemExit(f"Step failed: {script_name}")


def main():
    run_step("signaling_analyzer.py")
    print("\nDone. Check the reports/ folder.")


if __name__ == "__main__":
    main()