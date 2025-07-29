import sys
        import os
        import subprocess
        from pathlib import Path
        from PyQt6.QtWidgets import QApplication
        from .cheesymamas import CheesyMamas

        def maybe_create_launcher():
            home = Path.home()
            apps_dir = home / ".local/share/applications"
            icons_dir = home / ".local/share/icons"
            apps_dir.mkdir(parents=True, exist_ok=True)
            icons_dir.mkdir(parents=True, exist_ok=True)

            desktop_file = apps_dir / "cheesymamas.desktop"
            icon_source = Path(__file__).parent / "assets" / "CheesyMamas.png"
            icon_target = icons_dir / "CheesyMamas.png"

            if not icon_target.exists():
                try:
                    icon_target.write_bytes(icon_source.read_bytes())
                except Exception as e:
                    print(f"[icon copy failed]: {e}")

            if not desktop_file.exists():
                desktop_file.write_text(f"""[Desktop Entry]
        Name=Cheesy Mamas
        Comment=Simple file editor with built-in Git snapshots
        Exec=python3 -m cheesymamas %f
        Icon=CheesyMamas
        Terminal=false
        Type=Application
        Categories=Development;Utility;TextEditor;
        MimeType=text/plain;text/x-python;text/x-csrc;text/x-shellscript;text/x-tex;
        StartupNotify=true
        """)
                os.chmod(desktop_file, 0o755)

                try:
                    subprocess.run([
                        "update-desktop-database",
                        str(apps_dir)
                    ], stderr=subprocess.DEVNULL)
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