import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from .cheesymamas import CheesyMamas

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

def maybe_create_launcher():
    home = Path.home()
    apps_dir = home / ".local/share/applications"
    icons_dir = home / ".local/share/icons"
    apps_dir.mkdir(parents=True, exist_ok=True)
    icons_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = apps_dir / "cheesymamas.desktop"
    icon_target = icons_dir / "CheesyMamas.png"
    if not icon_target.exists():
        try:
            icon_data = files("cheesymamas.assets").joinpath("CheesyMamas.png").read_bytes()
            icon_target.write_bytes(icon_data)
        except Exception:
            dev_icon = Path(__file__).parent.parent / "assets" / "CheesyMamas.png"
            if dev_icon.exists():
                icon_target.write_bytes(dev_icon.read_bytes())
            else:
                print("🧀 [Warning] Could not find CheesyMamas.png")
    if not desktop_file.exists():
        python_exec = sys.executable
        desktop_file.write_text(f"""[Desktop Entry]
Name=Cheesy Mamas
Comment=Simple file editor with built-in Git snapshots
Exec={python_exec} -m cheesymamas
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
    maybe_create_launcher()
    app = QApplication(sys.argv)
    window = CheesyMamas()
    window.start_file_relay_watch()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()