-- Retail sales schema (DuckDB / ANSI SQL). Dates are real DATE values, not strings.
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name  VARCHAR NOT NULL,
    last_name   VARCHAR NOT NULL,
    address     VARCHAR
);

CREATE TABLE items (
    item_id    INTEGER PRIMARY KEY,
    item_name  VARCHAR NOT NULL,
    price      DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    department VARCHAR NOT NULL
);

-- One row per order line: an order can contain several items.
CREATE TABLE sales (
    sale_date   DATE NOT NULL,
    order_id    INTEGER NOT NULL,
    item_id     INTEGER NOT NULL REFERENCES items (item_id),
    customer_id INTEGER NOT NULL REFERENCES customers (customer_id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    revenue     DECIMAL(10, 2) NOT NULL CHECK (revenue >= 0),
    PRIMARY KEY (order_id, item_id)
);
