import sys
    import os
    import subprocess
    from pathlib import Path
    from PyQt6.QtWidgets import QApplication
    from .cheesymamas import CheesyMamas

    def maybe_create_launcher():
        home = Path.home()
        desktop_dir = home / ".local/share/applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = desktop_dir / "cheesymamas.desktop"
        icon_path = Path(__file__).parent / "assets" / "CheesyMamas.png"
        exec_path = f"{sys.executable} -m cheesymamas"

        if not desktop_file.exists():
            desktop_file.write_text(f"""[Desktop Entry]
    Name=Cheesy Mamas
    Comment=A local-first code editor with cheesy git power
    Exec={exec_path}
    Icon={icon_path}
    Terminal=false
    Type=Application
    Categories=Development;TextEditor;
    StartupNotify=true
    """)
            os.chmod(desktop_file, 0o755)

            # Try to update desktop database if available
            try:
                subprocess.run([
                    "update-desktop-database",
                    str(desktop_dir)
                ], stderr=subprocess.DEVNULL)
            except Exception:
                pass  # Non-fatal

    def main():
        maybe_create_launcher()
        app = QApplication(sys.argv)
        window = CheesyMamas()
        window.start_file_relay_watch()
        window.show()
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()