DROP TABLE IF EXISTS sales_history;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS partners;
DROP TABLE IF EXISTS product_types;
DROP TABLE IF EXISTS material_types;

CREATE TABLE product_types (
    product_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    coefficient DECIMAL(10, 4) NOT NULL CHECK (coefficient > 0)
);

CREATE TABLE material_types (
    material_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_name TEXT NOT NULL UNIQUE,
    defect_percent DECIMAL(5, 2) NOT NULL CHECK (defect_percent >= 0)
);

CREATE TABLE partners (
    partner_id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_type TEXT NOT NULL,
    partner_name TEXT NOT NULL,
    director_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    inn TEXT NOT NULL UNIQUE,
    rating INTEGER NOT NULL DEFAULT 0 CHECK (rating >= 0),
    address TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    article TEXT UNIQUE,
    min_price DECIMAL(10, 2) NOT NULL CHECK (min_price >= 0),
    product_type_id INTEGER,
    FOREIGN KEY (product_type_id) REFERENCES product_types (product_type_id)
);

CREATE TABLE sales_history (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (partner_id) REFERENCES partners (partner_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE INDEX idx_sales_partner ON sales_history (partner_id);

INSERT INTO product_types (type_name, coefficient) VALUES
    ('Тип 1', 1.5),
    ('Тип 2', 2.0);

INSERT INTO material_types (material_name, defect_percent) VALUES
    ('Материал 1', 10),
    ('Материал 2', 5);
