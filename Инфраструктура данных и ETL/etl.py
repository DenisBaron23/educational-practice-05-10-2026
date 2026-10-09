import csv
import re
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "partner_system.db"
DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


def clean(value):
    # trim по краям и схлопывание повторных пробелов внутри строки
    return re.sub(r"\s+", " ", (value or "").strip())


def normalize_date(value):
    text = clean(value)
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def read_csv(name):
    path = BASE_DIR / "data" / name
    with open(path, encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def import_partners(conn):
    for row in read_csv("partners_raw.csv"):
        conn.execute(
            "INSERT INTO partners (partner_id, partner_type, partner_name, "
            "director_name, email, phone, inn, rating, address) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                int(clean(row["partner_id"])),
                clean(row["partner_type"]),
                clean(row["partner_name"]),
                clean(row["director_name"]),
                clean(row["email"]).lower(),
                clean(row["phone"]),
                clean(row["inn"]),
                int(clean(row["rating"]) or 0),
                clean(row["address"]),
            ),
        )


def import_products(conn):
    for row in read_csv("products_raw.csv"):
        conn.execute(
            "INSERT INTO products (product_id, product_name, article, min_price) "
            "VALUES (?, ?, ?, ?)",
            (
                int(clean(row["product_id"])),
                clean(row["product_name"]),
                clean(row["article"]),
                clean(row["min_price"]).replace(",", "."),
            ),
        )


def import_sales(conn):
    partner_ids = {r[0] for r in conn.execute("SELECT partner_id FROM partners")}
    product_ids = {r[0] for r in conn.execute("SELECT product_id FROM products")}
    skipped = 0
    for row in read_csv("sales_history_raw.csv"):
        partner_id = int(clean(row["partner_id"]))
        product_id = int(clean(row["product_id"]))
        sale_date = normalize_date(row["sale_date"])
        # строки с битым внешним ключом или непонятной датой отбрасываем
        if partner_id not in partner_ids or product_id not in product_ids or not sale_date:
            skipped += 1
            print("пропущена строка:", row)
            continue
        conn.execute(
            "INSERT INTO sales_history (partner_id, product_id, sale_date, quantity) "
            "VALUES (?, ?, ?, ?)",
            (partner_id, product_id, sale_date, int(clean(row["quantity"]))),
        )
    print("пропущено строк:", skipped)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))
    import_partners(conn)
    import_products(conn)
    import_sales(conn)
    conn.commit()
    conn.close()
    print("etl завершен")


if __name__ == "__main__":
    main()
