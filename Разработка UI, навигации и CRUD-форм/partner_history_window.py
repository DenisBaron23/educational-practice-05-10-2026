import sqlite3
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QLabel, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from db import get_connection

RES_DIR = Path(__file__).parent / "resources"


class PartnerHistoryWindow(QDialog):
    def __init__(self, partner_id, parent=None):
        super().__init__(parent)
        self.partner_id = partner_id
        self.setWindowTitle("История продаж партнера")
        self.resize(600, 400)

        self.title = QLabel()
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Товар", "Дата", "Количество"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        back_button = QPushButton(QIcon(str(RES_DIR / "back.png")), " Назад")
        back_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(self.table)
        layout.addWidget(back_button)
        self.load_history()

    def load_history(self):
        try:
            conn = get_connection()
            try:
                name_row = conn.execute(
                    "SELECT partner_name FROM partners WHERE partner_id = ?",
                    (self.partner_id,),
                ).fetchone()
                rows = conn.execute(
                    "SELECT pr.product_name, s.sale_date, s.quantity "
                    "FROM sales_history s JOIN products pr ON pr.product_id = s.product_id "
                    "WHERE s.partner_id = ? ORDER BY s.sale_date DESC",
                    (self.partner_id,),
                ).fetchall()
            finally:
                conn.close()
        except sqlite3.Error as error:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Critical)
            box.setWindowTitle("Ошибка")
            box.setText("Не удалось загрузить историю: " + str(error))
            box.setInformativeText("Что сделать:\n1. Проверьте файл базы данных.\n2. Закройте и откройте окно заново.")
            box.exec_()
            return
        self.title.setText("Партнер: " + (name_row[0] if name_row else "не найден"))
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))
