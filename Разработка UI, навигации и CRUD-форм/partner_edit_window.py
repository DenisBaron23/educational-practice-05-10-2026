import sqlite3
from pathlib import Path

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QIcon, QRegularExpressionValidator
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout,
)

from db import get_connection

RES_DIR = Path(__file__).parent / "resources"
PARTNER_TYPES = ["ООО", "ЗАО", "ПАО", "ОАО"]


def make_icon(name):
    path = RES_DIR / f"{name}.png"
    return QIcon(str(path)) if path.exists() else QIcon()


def show_error(parent, text, steps):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle("Ошибка")
    box.setText(text)
    box.setInformativeText("Что сделать:\n" + steps)
    box.exec_()


class PartnerEditWindow(QDialog):
    def __init__(self, partner_id=None, parent=None):
        super().__init__(parent)
        self.partner_id = partner_id
        self.changed = False
        self.setWindowTitle("Редактирование партнера" if partner_id else "Новый партнер")
        self.build_ui()
        if partner_id:
            self.load_partner()
        self.changed = False

    def build_ui(self):
        form = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(PARTNER_TYPES)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Альфа")
        self.rating_input = QLineEdit()
        self.rating_input.setPlaceholderText("Целое число от 0")
        self.rating_input.setValidator(QRegularExpressionValidator(QRegularExpression(r"\d{1,9}")))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Город, улица, дом")
        self.director_input = QLineEdit()
        self.director_input.setPlaceholderText("Фамилия Имя Отчество")
        self.phone_input = QLineEdit()
        self.phone_input.setInputMask("+7 (000) 000-00-00;_")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("name@example.com")
        self.inn_input = QLineEdit()
        self.inn_input.setPlaceholderText("10 или 12 цифр")
        self.inn_input.setValidator(QRegularExpressionValidator(QRegularExpression(r"\d{0,12}")))

        fields = (
            ("Тип", self.type_combo), ("Наименование", self.name_input),
            ("Рейтинг", self.rating_input), ("Адрес", self.address_input),
            ("Директор", self.director_input), ("Телефон", self.phone_input),
            ("Email", self.email_input), ("ИНН", self.inn_input),
        )
        for label, widget in fields:
            form.addRow(label, widget)
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.mark_changed)
        self.type_combo.currentIndexChanged.connect(self.mark_changed)

        save_button = QPushButton(make_icon("save"), " Сохранить")
        save_button.clicked.connect(self.save)
        back_button = QPushButton(make_icon("back"), " Назад")
        back_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addWidget(save_button)
        buttons.addWidget(back_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def mark_changed(self, *args):
        self.changed = True

    def reject(self):
        # reject вызывается и кнопкой «Назад», и крестиком, и esc
        if self.changed:
            answer = QMessageBox.warning(
                self, "Несохраненные данные",
                "Изменения не сохранены. Если выйти, они будут безвозвратно потеряны.\nВыйти без сохранения?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
        super().reject()

    def load_partner(self):
        try:
            conn = get_connection()
            try:
                row = conn.execute(
                    "SELECT partner_type, partner_name, rating, address, director_name, "
                    "phone, email, inn FROM partners WHERE partner_id = ?",
                    (self.partner_id,),
                ).fetchone()
            finally:
                conn.close()
        except sqlite3.Error as error:
            show_error(self, str(error), "1. Проверьте файл базы данных.\n2. Откройте окно заново.")
            return
        if row is None:
            return
        self.type_combo.setCurrentText(row[0])
        self.name_input.setText(row[1])
        self.rating_input.setText(str(row[2]))
        self.address_input.setText(row[3])
        self.director_input.setText(row[4])
        self.phone_input.setText(row[5])
        self.email_input.setText(row[6])
        self.inn_input.setText(row[7])

    def validate(self):
        if not self.name_input.text().strip():
            return "Не заполнено наименование."
        if not self.rating_input.text().strip():
            return "Рейтинг должен быть целым числом от 0."
        if len(self.inn_input.text()) not in (10, 12):
            return "ИНН должен содержать 10 или 12 цифр."
        email = self.email_input.text().strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            return "Email указан неверно, пример: name@example.com."
        if not self.phone_input.hasAcceptableInput():
            return "Телефон заполнен не полностью."
        return None

    def save(self):
        problem = self.validate()
        if problem:
            show_error(self, problem, "1. Исправьте поле.\n2. Нажмите «Сохранить» снова.")
            return
        values = (
            self.type_combo.currentText(),
            self.name_input.text().strip(),
            int(self.rating_input.text()),
            self.address_input.text().strip(),
            self.director_input.text().strip(),
            self.phone_input.text(),
            self.email_input.text().strip().lower(),
            self.inn_input.text(),
        )
        try:
            conn = get_connection()
            try:
                if self.partner_id:
                    conn.execute(
                        "UPDATE partners SET partner_type = ?, partner_name = ?, rating = ?, "
                        "address = ?, director_name = ?, phone = ?, email = ?, inn = ? "
                        "WHERE partner_id = ?",
                        values + (self.partner_id,),
                    )
                else:
                    conn.execute(
                        "INSERT INTO partners (partner_type, partner_name, rating, address, "
                        "director_name, phone, email, inn) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        values,
                    )
                conn.commit()
            finally:
                conn.close()
        except sqlite3.IntegrityError:
            show_error(
                self, "Партнер с таким ИНН или email уже существует.",
                "1. Проверьте ИНН и email.\n2. Найдите существующую запись на главной форме.",
            )
            return
        except sqlite3.Error as error:
            show_error(
                self, "Не удалось сохранить данные: " + str(error),
                "1. Проверьте доступность базы данных.\n2. Повторите сохранение.",
            )
            return
        self.changed = False
        self.accept()
