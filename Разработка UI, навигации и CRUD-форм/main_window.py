import sqlite3
from pathlib import Path

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from db import get_connection
from discounts import get_partner_discount
from partner_edit_window import PartnerEditWindow
from partner_history_window import PartnerHistoryWindow

RES_DIR = Path(__file__).parent / "resources"
HEADERS = ["ID", "Тип", "Наименование", "Директор", "Телефон", "Рейтинг", "Скидка"]


def make_icon(name):
    # если файла нет, вернется пустая иконка и приложение не упадет
    path = RES_DIR / f"{name}.png"
    return QIcon(str(path)) if path.exists() else QIcon()


def show_error(parent, title, text, steps):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText(text)
    box.setInformativeText("Что сделать:\n" + steps)
    box.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Партнеры компании")
        self.setWindowIcon(QIcon(str(RES_DIR / "icon.ico")))
        self.resize(1000, 600)
        self.build_ui()
        self.load_partners()

    def build_ui(self):
        root = QWidget()
        layout = QVBoxLayout(root)

        header = QHBoxLayout()
        logo = QLabel()
        logo_path = RES_DIR / "logo.png"
        if logo_path.exists():
            logo.setPixmap(QPixmap(str(logo_path)).scaledToHeight(60, Qt.SmoothTransformation))
        else:
            logo.setText("[логотип]")
        title = QLabel("Партнеры компании")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2a6fb0;")
        header.addWidget(logo)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по наименованию, директору или email")
        self.search_input.textChanged.connect(self.load_partners)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        buttons = QHBoxLayout()
        for text, icon_name, handler in (
            ("Добавить", "add", self.add_partner),
            ("Редактировать", "edit", self.edit_partner),
            ("История продаж", "history", self.open_history),
        ):
            button = QPushButton(make_icon(icon_name), " " + text)
            button.setIconSize(QSize(20, 20))
            button.clicked.connect(handler)
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.setCentralWidget(root)

    def load_partners(self):
        pattern = "%" + self.search_input.text().strip() + "%"
        try:
            conn = get_connection()
            try:
                rows = conn.execute(
                    "SELECT partner_id, partner_type, partner_name, director_name, "
                    "phone, rating FROM partners "
                    "WHERE partner_name LIKE ? OR director_name LIKE ? OR email LIKE ? "
                    "ORDER BY partner_name",
                    (pattern, pattern, pattern),
                ).fetchall()
                self.table.setRowCount(len(rows))
                for r, row in enumerate(rows):
                    discount = get_partner_discount(row[0])
                    values = list(row) + [f"{discount}%"]
                    for c, value in enumerate(values):
                        self.table.setItem(r, c, QTableWidgetItem(str(value)))
            finally:
                conn.close()
        except sqlite3.Error as error:
            show_error(
                self, "База данных недоступна", str(error),
                "1. Проверьте, что файл partner_system.db существует.\n"
                "2. Запустите etl.py из папки «Инфраструктура данных и ETL».\n"
                "3. Перезапустите приложение.",
            )

    def selected_partner_id(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Партнер не выбран", "Выделите строку в таблице.")
            return None
        return int(self.table.item(row, 0).text())

    def add_partner(self):
        dialog = PartnerEditWindow(parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_partners()

    def edit_partner(self):
        partner_id = self.selected_partner_id()
        if partner_id is None:
            return
        dialog = PartnerEditWindow(partner_id=partner_id, parent=self)
        if dialog.exec_() == dialog.Accepted:
            self.load_partners()

    def open_history(self):
        partner_id = self.selected_partner_id()
        if partner_id is None:
            return
        PartnerHistoryWindow(partner_id=partner_id, parent=self).exec_()
