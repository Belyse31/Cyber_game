"""
CyberGame Remover
=================
Completely removes everything the game installed:
  1. Kills any running game / python processes
  2. Removes persistence (registry Run key + scheduled task)
  3. Deletes all game files and folders
  4. Uninstalls pygame from the portable Python
  5. Cleans up temp files and traces
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_TASK_NAME = "CyberGameUpdater"
_REG_KEY   = r"Software\Microsoft\Windows\CurrentVersion\Run"
_REG_VAL   = "CyberGameUpdater"

# Folders/files to fully delete
_TARGETS = [
    ROOT / "runtime" / "python",   # portable Python we extracted
    ROOT / "runtime" / "get-pip.py",
    ROOT / "runtime" / "python-embed.zip",
    ROOT / ".venv",                 # in case old venv exists
]


def _ok(msg):  print(f"  [OK]  {msg}")
def _skip(msg): print(f"  [--]  {msg}")
def _err(msg):  print(f"  [!!]  {msg}")


# ── 1. Kill running processes ─────────────────────────────────────────────────
def kill_processes():
    print("\n[1/5] Killing game processes...")
    killed = False
    try:
        # Get all python.exe PIDs except our own
        result = subprocess.run(
            ["tasklist", "/fi", "imagename eq python.exe", "/fo", "csv", "/nh"],
            capture_output=True, text=True
        )
        our_pid = os.getpid()
        for line in result.stdout.strip().splitlines():
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                try:
                    pid = int(parts[1])
                    if pid != our_pid:
                        subprocess.run(["taskkill", "/f", "/pid", str(pid)],
                                       capture_output=True)
                        _ok(f"killed python.exe (PID {pid})")
                        killed = True
                except ValueError:
                    pass
        # Also kill pythonw.exe
        subprocess.run(["taskkill", "/f", "/im", "pythonw.exe"],
                       capture_output=True)
    except Exception as e:
        _err(f"process kill failed: {e}")
    if not killed:
        _skip("no other python processes found")
    time.sleep(1)  # give processes time to die before deleting files


# ── 2. Remove persistence ─────────────────────────────────────────────────────
def remove_persistence():
    print("\n[2/5] Removing persistence mechanisms...")

    # Registry Run key
    if os.name == "nt":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0,
                                 winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, _REG_VAL)
            winreg.CloseKey(key)
            _ok("registry Run key removed")
        except FileNotFoundError:
            _skip("registry key not present")
        except Exception as e:
            _err(f"registry: {e}")

        # Scheduled task
        try:
            r = subprocess.run(
                ["schtasks", "/delete", "/tn", _TASK_NAME, "/f"],
                capture_output=True, text=True
            )
            if r.returncode == 0:
                _ok("scheduled task removed")
            else:
                _skip("scheduled task not present")
        except Exception as e:
            _err(f"schtasks: {e}")

        # Startup folder shortcut (just in case)
        startup = Path(os.environ.get("APPDATA", "")) / \
                  "Microsoft/Windows/Start Menu/Programs/Startup/CyberGame.lnk"
        if startup.exists():
            startup.unlink()
            _ok("startup folder shortcut removed")
        else:
            _skip("no startup folder shortcut")


# ── 3. Delete game files ──────────────────────────────────────────────────────
def delete_files():
    print("\n[3/5] Deleting game files and folders...")
    for target in _TARGETS:
        if not target.exists():
            _skip(f"not found: {target.name}")
            continue
        try:
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink()
            _ok(f"deleted: {target.relative_to(ROOT)}")
        except Exception as e:
            _err(f"could not delete {target.name}: {e}")


# ── 4. Uninstall pygame (pip uninstall from portable python) ──────────────────
def uninstall_packages():
    print("\n[4/5] Uninstalling game packages...")
    pyexe = ROOT / "runtime" / "python" / "python.exe"
    if not pyexe.exists():
        _skip("portable Python already removed — skipping pip uninstall")
        return
    try:
        r = subprocess.run(
            [str(pyexe), "-m", "pip", "uninstall", "pygame", "-y"],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            _ok("pygame uninstalled")
        else:
            _skip("pygame was not installed or already removed")
    except Exception as e:
        _err(f"pip uninstall failed: {e}")


# ── 5. Clean traces (temp files, pip cache) ───────────────────────────────────
def clean_traces():
    print("\n[5/5] Cleaning traces...")

    # pip cache inside portable python
    pip_cache = ROOT / "runtime" / "python" / "pip_cache"
    if pip_cache.exists():
        shutil.rmtree(pip_cache, ignore_errors=True)
        _ok("pip cache cleared")

    # __pycache__ folders inside game dir
    for cache in ROOT.rglob("__pycache__"):
        try:
            shutil.rmtree(cache, ignore_errors=True)
            _ok(f"removed __pycache__: {cache.relative_to(ROOT)}")
        except Exception:
            pass

    # .pyc files
    for pyc in ROOT.rglob("*.pyc"):
        try:
            pyc.unlink()
        except Exception:
            pass

    _ok("trace cleanup done")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  CyberGame Remover")
    print("=" * 50)
    print()
    print("This will completely remove CyberGame from this")
    print("computer, including:")
    print("  - All running game processes")
    print("  - Registry startup entry")
    print("  - Scheduled task (CyberGameUpdater)")
    print("  - Portable Python runtime")
    print("  - Installed packages (pygame)")
    print("  - Temporary files and traces")
    print()
    ans = input("Proceed with full removal? (y/N): ").strip().lower()
    if ans != "y":
        print("\nCancelled. Nothing was removed.")
        input("\nPress Enter to exit...")
        return

    kill_processes()
    remove_persistence()
    uninstall_packages()   # must run before delete_files removes python
    delete_files()
    clean_traces()

    print()
    print("=" * 50)
    print("  Cleaning complete.")
    print("  CyberGame has been fully removed.")
    print("=" * 50)
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    except Exception as e:
        import traceback
        print("\n[FATAL ERROR]")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
