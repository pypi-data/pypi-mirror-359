def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    from .cheesymamas import CheesyMamas
    window = CheesyMamas()
    window.start_file_relay_watch()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()