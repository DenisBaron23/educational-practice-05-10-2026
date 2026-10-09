import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter

RES_DIR = Path(__file__).parent / "resources"


def draw_image(size, letter, background):
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(background))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.setPen(QColor("white"))
    font = QFont("Arial")
    font.setBold(True)
    font.setPixelSize(int(size * 0.5))
    painter.setFont(font)
    painter.drawText(image.rect(), Qt.AlignCenter, letter)
    painter.end()
    return image


def draw_symbol(name, color):
    symbols = {"add": "+", "edit": "E", "history": "≡", "save": "✔", "back": "←"}
    size = 64
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QColor(color))
    font = QFont("Arial")
    font.setBold(True)
    font.setPixelSize(52)
    painter.setFont(font)
    painter.drawText(image.rect(), Qt.AlignCenter, symbols[name])
    painter.end()
    return image


def main():
    # QImage и QPainter требуют экземпляра приложения
    app = QGuiApplication(sys.argv)
    RES_DIR.mkdir(exist_ok=True)
    draw_image(256, "П", "#2a6fb0").save(str(RES_DIR / "logo.png"))
    draw_image(256, "П", "#1e4f82").save(str(RES_DIR / "icon.ico"))
    for name, color in (
        ("add", "#2e8b57"), ("edit", "#2a6fb0"), ("history", "#6a4c93"),
        ("save", "#2e8b57"), ("back", "#555555"),
    ):
        draw_symbol(name, color).save(str(RES_DIR / f"{name}.png"))
    print("ресурсы созданы в", RES_DIR)
    del app


if __name__ == "__main__":
    main()

