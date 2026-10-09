import math
from decimal import Decimal, InvalidOperation

from db import get_connection


def to_decimal(value):
    # через str, чтобы не тащить двоичную погрешность float
    return Decimal(str(value))


def calculate_material_amount(
    product_type_id,
    material_type_id,
    quantity,
    param1,
    param2,
    db_path=None,
):
    try:
        quantity = to_decimal(quantity)
        param1 = to_decimal(param1)
        param2 = to_decimal(param2)
        if quantity < 0 or param1 < 0 or param2 < 0:
            return -1

        conn = get_connection(db_path)
        try:
            product_row = conn.execute(
                "SELECT coefficient FROM product_types WHERE product_type_id = ?",
                (product_type_id,),
            ).fetchone()
            material_row = conn.execute(
                "SELECT defect_percent FROM material_types WHERE material_type_id = ?",
                (material_type_id,),
            ).fetchone()
        finally:
            conn.close()

        if product_row is None or material_row is None:
            return -1

        coefficient = to_decimal(product_row[0])
        defect_percent = to_decimal(material_row[0])
        raw_amount = (
            quantity
            * param1
            * param2
            * coefficient
            * (1 + defect_percent / 100)
        )
        # ceil от Decimal точен: 99.0 останется 99, а не станет 100
        return int(math.ceil(raw_amount))
    except (InvalidOperation, ValueError, TypeError):
        return -1
    except Exception:
        return -1
