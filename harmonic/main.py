from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowType = ...) -> None:
        super().__init__(parent, flags)

        self.setWindowTitle("Harmonic")


if __name__ == "main":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()