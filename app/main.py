import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow
import time

if __name__ == "__main__":
    print(f"[APP] App launched at {time.time()}")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())