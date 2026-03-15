import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from views.main_window import MainWindow
from config import AppConfig

def load_stylesheet(app: QApplication, path: str) -> None:
    """Load QSS stylesheet from file."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {path}")

def main():
    # Support high DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(AppConfig.APP_NAME)
    
    # Load and apply theme
    load_stylesheet(app, AppConfig.DEFAULT_THEME_PATH)
    
    # Set application icon
    app.setWindowIcon(QIcon(AppConfig.APP_ICON_PATH))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
# python -m nuitka main.py --onefile --standalone --enable-plugin=pyqt5 --windows-console-mode=disable --lto=yes --include-data-dir=d:\VuaCode\HotmailChecker\resources=resources --windows-icon-from-ico=D:\VuaCode\HotmailChecker\resources\icons\app_icon.ico