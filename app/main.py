import sys

from PySide6.QtWidgets import QApplication, QLabel


def main():
    app = QApplication(sys.argv)

    label = QLabel("Lunar Landing Site Navigator")
    label.resize(500, 300)
    label.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()