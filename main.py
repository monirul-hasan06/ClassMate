import sys
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from database.db_manager import DatabaseManager
from ui.main_window import MainWindow
from ui.resources import get_app_icon, get_code_font


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ClassMate")
    app.setOrganizationName("BUBT_CSE_DBMS")

    app.setFont(QFont("Segoe UI Variable Text", 10))
    app.setFont(get_code_font(), "QPlainTextEdit")

    # Set High-Resolution Vector/Multi-DPI Windows App Icon
    app.setWindowIcon(get_app_icon())

    db = DatabaseManager()
    window = MainWindow(db)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
