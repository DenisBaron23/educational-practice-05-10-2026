import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Реализация ядра бизнес-логики"))

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # иконка приложения наследуется всеми диалогами
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "resources" / "icon.ico")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
