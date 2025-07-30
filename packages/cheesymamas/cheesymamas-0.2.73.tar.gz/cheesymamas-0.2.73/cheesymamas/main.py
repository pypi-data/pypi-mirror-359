import sys
import os
import site
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from .cheesymamas import CheesyMamas

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

# 🩷 Ensure user site-packages are in sys.path when launched from GUI
if site.getusersitepackages() not in sys.path:
    sys.path.append(site.getusersitepackages())

def create_desktop_launcher():
    home = Path.home()
    apps_dir = home / ".local/share/applications"
    icons_dir = home / ".local/share/icons"
    apps_dir.mkdir(parents=True, exist_ok=True)
    icons_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = apps_dir / "cheesymamas.desktop"
    icon_target = icons_dir / "CheesyMamas.png"

    # Always copy icon
    try:
        icon_data = files("cheesymamas.assets").joinpath("CheesyMamas.png").read_bytes()
        icon_target.write_bytes(icon_data)
    except Exception:
        dev_icon = Path(__file__).parent.parent / "assets" / "CheesyMamas.png"
        if dev_icon.exists():
            icon_target.write_bytes(dev_icon.read_bytes())
        else:
            print("🧀 [Warning] Could not find CheesyMamas.png")

    # Always write launcher
    python_exec = sys.executable
    desktop_file.write_text(f"""[Desktop Entry]
Name=Cheesy Mamas
Comment=Simple file editor with built-in Git snapshots
Exec="{python_exec}" -m cheesymamas
Icon=CheesyMamas
Terminal=false
Type=Application
Categories=Development;Utility;TextEditor;
MimeType=text/plain;text/x-python;text/x-csrc;text/x-shellscript;text/x-tex;
StartupNotify=true
""")
    os.chmod(desktop_file, 0o755)

    try:
        subprocess.run(["update-desktop-database", str(apps_dir)], stderr=subprocess.DEVNULL)
        subprocess.run(["gtk-update-icon-cache", str(icons_dir)], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    create_desktop_launcher()
    app = QApplication(sys.argv)
    window = CheesyMamas()
    window.start_file_relay_watch()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print("🧀 Launching...")
    from PyQt6.QtCore import QTimer
    import traceback

    PENDING_PATH_FILE = os.path.expanduser("~/.local/share/CheesyMamas/pending_open.txt")
    os.makedirs(os.path.dirname(PENDING_PATH_FILE), exist_ok=True)

    lock_file = os.path.expanduser("~/.local/share/CheesyMamas/instance.lock")
    file_to_open = sys.argv[1] if len(sys.argv) > 1 else None
    already_running = os.path.exists(lock_file) and file_to_open and not file_to_open.endswith("cheesymamas.py")

    if file_to_open and already_running:
        try:
            with open(PENDING_PATH_FILE, "a") as f:
                f.write(file_to_open + "\n")
            print(f"📂 Relayed file to running instance: {file_to_open}")
            sys.exit(0)
        except Exception as e:
            print(f"[relay write failed]: {e}")
            sys.exit(1)

    app = QApplication(sys.argv)
    try:
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

        window = CheesyMamas()
        window.start_file_relay_watch()
        print("✅ Window built")
        window.show()
        if file_to_open:
            QTimer.singleShot(100, lambda: window.open_file_path(file_to_open))
        print("✅ Window shown")
        exit_code = app.exec()
    except Exception:
        log_path = Path.home() / ".cache" / "cheesymamas_crash.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as log:
            log.write("💥 Exception during GUI startup:\n")
            log.write(traceback.format_exc())
            log.write("\n\n")
        raise
    finally:
        if os.path.exists(lock_file):
            os.remove(lock_file)
        if "window" in locals() and hasattr(window, 'file_relay_timer'):
            window.file_relay_timer.stop()
            window.file_relay_timer.deleteLater()

    sys.exit(exit_code)