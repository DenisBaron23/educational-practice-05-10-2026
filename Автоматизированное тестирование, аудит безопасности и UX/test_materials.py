import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Реализация ядра бизнес-логики"))

from materials import calculate_material_amount


class MaterialsTest(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        conn = sqlite3.connect(self.db_path)
        conn.executescript(
            "CREATE TABLE product_types (product_type_id INTEGER PRIMARY KEY, coefficient DECIMAL);"
            "CREATE TABLE material_types (material_type_id INTEGER PRIMARY KEY, defect_percent DECIMAL);"
            "INSERT INTO product_types VALUES (1, 1.5);"
            "INSERT INTO material_types VALUES (1, 10);"
            "INSERT INTO material_types VALUES (2, 0);"
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        os.remove(self.db_path)

    def calc(self, product_id, material_id, quantity, p1, p2):
        return calculate_material_amount(product_id, material_id, quantity, p1, p2, self.db_path)

    def test_basic_calculation(self):
        # 10 * 2 * 3 * 1.5 * 1.1 = 99
        self.assertEqual(self.calc(1, 1, 10, 2, 3), 99)

    def test_rounding_strictly_up(self):
        # 1.5 -> 2
        self.assertEqual(self.calc(1, 2, 1, 1, 1), 2)

    def test_unknown_product_type(self):
        self.assertEqual(self.calc(999, 1, 10, 2, 3), -1)

    def test_unknown_material_type(self):
        self.assertEqual(self.calc(1, 999, 10, 2, 3), -1)

    def test_negative_quantity(self):
        self.assertEqual(self.calc(1, 1, -5, 2, 3), -1)

    def test_negative_parameter(self):
        self.assertEqual(self.calc(1, 1, 10, -2, 3), -1)

    def test_non_numeric_input(self):
        self.assertEqual(self.calc(1, 1, "abc", 2, 3), -1)


if __name__ == "__main__":
    unittest.main()
