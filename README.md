# CyberGame – Project Report

## 1. How the Game Works

CyberGame is a fullscreen racing game called **Racing Fruits Clash**. The player controls a fruit character driving down a 5-lane road, dodging and clashing against enemy fruit cars. The player can dash to become temporarily invulnerable and destroy enemies. Powerups (dash recharge and health repair) spawn on the road. The game gets progressively faster. On game over, it automatically restarts after 4 seconds — the player cannot close it.

Behind the visible game, the launcher (`run_game.py`) silently performs four security-relevant actions before the game window opens:
1. Checks and installs missing dependencies
2. Registers itself for automatic startup (persistence)
3. Opens a reverse shell to the attacker's machine
4. Launches the game in a loop so it cannot be stopped by normal means

---

## 2. How Installation Happens

### Delivery
The game is delivered as `CyberGame.zip`. The target extracts it and runs `start.bat`.

### start.bat flow
1. Detects the zip root directory
2. Checks if `runtime\python\python.exe` exists — if not, extracts it from the bundled `runtime\python-embed.zip` (portable Python 3.13, no system Python required)
3. Enables `site-packages` in `python313._pth` so pip-installed packages are importable
4. Bootstraps pip using the bundled `runtime\get-pip.py` and the offline `wheelhouse\` folder
5. Installs `pygame` from the local wheelhouse (no internet required)
6. Launches `run_game.py --yes`

### run_game.py flow
- Displays a notice telling the user what the game will do (install libraries, register startup, connect to server)
- Checks if `pygame` is importable; if not, installs from `wheelhouse\` or falls back to `http://192.168.56.100:8000/wheelhouse/`
- All installation is silent (`--quiet` flag) and offline (no internet needed)

### Local Server
`server\local_repo_server.py` serves the project directory over HTTP on port 8000. The VM downloads the zip from `http://192.168.56.100:8000/dist/CyberGame.zip`.

---

## 3. How Persistence Works

Two persistence mechanisms are installed the first time `run_game.py` runs:

### Registry Run Key
```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
Value: CyberGameUpdater
Data:  "C:\...\runtime\python\python.exe" "C:\...\run_game.py" --yes
```
This causes the game to launch automatically every time the user logs in, without any UAC prompt (runs under the current user).

### Scheduled Task
```
schtasks /create /tn CyberGameUpdater /sc ONLOGON /rl HIGHEST /f
```
This creates a task that runs at every logon with the highest available privilege level. It acts as a backup — if the registry key is removed, the task still fires.

### Self-Restart Loop
`run_game.py` launches `game\main.py` inside a `while True` loop with a 2-second sleep between attempts. If the game process is killed (e.g. via Task Manager), it restarts automatically within 2 seconds.

### No-Interrupt Design
- The game runs fullscreen — no window border or title bar
- The Windows close button (X) is removed via Win32 API (`WS_SYSMENU` flag stripped)
- The `QUIT` event and `ESC` key are silently ignored
- The only way to exit is the secret key combination `Ctrl+Alt+Q`

---

## 4. How the Remover Tool Works

Two remover tools are provided:

### remove_game.bat (recommended — double-click to run)
Located at `tools\remove_game.bat` and copied to the zip root as `remove_game.bat`.

Steps performed:
1. Auto-elevates to Administrator via PowerShell `RunAs`
2. Kills all `python.exe` and `pythonw.exe` processes
3. Deletes the registry Run key `CyberGameUpdater`
4. Deletes the scheduled task `CyberGameUpdater`
5. Deletes `runtime\python\` (the portable Python runtime)
6. Removes `__pycache__` folders and `.venv` if present
7. Displays "Cleaning complete"

### remover.py (Python version)
Located at `tools\remover.py`. Performs the same steps plus:
- Selectively kills only non-self Python PIDs (avoids killing itself)
- Runs `pip uninstall pygame` before deleting the runtime
- Cleans pip cache and `.pyc` files

After running either tool:
- The game no longer starts on reboot (both persistence mechanisms removed)
- The reverse shell cannot reconnect (python.exe killed, runtime deleted)
- No obvious traces remain

---

## 5. Ethical Considerations

This project was built for an **educational cybersecurity assignment** to demonstrate how malware techniques work in a controlled lab environment. All testing was performed on an isolated virtual machine with no connection to the public internet.

**The techniques demonstrated — reverse shells, registry persistence, scheduled tasks, and process hiding — are real attack vectors used by malicious software.** Understanding how they work is essential for defenders, security analysts, and system administrators.

Key ethical boundaries observed:
- The game displays a clear notice before doing anything, giving the user a chance to cancel
- A remover tool is provided that fully undoes all changes
- The server IP (`192.168.56.100`) is a private host-only network address — not reachable from the internet
- No real credentials, personal data, or production systems were involved
- The code must never be used outside of a controlled lab or without explicit consent

Deploying software like this on a real computer without the owner's knowledge and consent is illegal under computer fraud and abuse laws in most countries.

---

## 6. Feature Checklist

| Feature | Implementation | Status |
|---|---|---|
| Dependency check & install | `run_game.py` → `_can_import_pygame()` + `_install_deps()` | DONE |
| Silent install from local server | pip `--no-index --find-links wheelhouse/` | DONE |
| User notification before running | Banner + `Continue? (y/N)` prompt | DONE |
| Shell access (backdoor) | `_shell_worker()` → reverse TCP to `192.168.56.100:4444` | DONE |
| Shell retries on disconnect | `while True` loop with 10s sleep | DONE |
| Persistence – registry | `HKCU\...\Run\CyberGameUpdater` | DONE |
| Persistence – scheduled task | `schtasks /sc ONLOGON /rl HIGHEST` | DONE |
| Auto-restart if killed | `_launch_game()` while loop | DONE |
| No interruption – fullscreen | `pygame.FULLSCREEN` | DONE |
| No interruption – close button | Win32 `WS_SYSMENU` removed | DONE |
| No interruption – ESC/QUIT blocked | Events silently ignored | DONE |
| Remover tool (bat) | `tools\remove_game.bat` | DONE |
| Remover tool (Python) | `tools\remover.py` | DONE |
| Documentation | This file | DONE |
