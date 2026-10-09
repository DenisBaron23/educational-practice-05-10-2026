from db import get_connection


def get_discount_percent(total_quantity):
    if total_quantity < 10000:
        return 0
    if total_quantity < 50000:
        return 5
    if total_quantity < 300000:
        return 10
    return 15


def get_partner_discount(partner_id, db_path=None):
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM sales_history WHERE partner_id = ?",
            (partner_id,),
        ).fetchone()
    finally:
        conn.close()
    return get_discount_percent(row[0])
