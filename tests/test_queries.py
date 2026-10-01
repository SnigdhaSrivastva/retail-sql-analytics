"""Every query runs against a small hand-built dataset whose correct answers were worked out by hand.

The dataset deliberately contains the cases the original assignment queries got wrong:
multi-line orders, a customer named John but not Doe, a department with no 2022 sales,
and two orders tied for the highest revenue.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]

SEED = """
INSERT INTO customers VALUES
  (1, 'John', 'Doe',   '1 Main St'),
  (2, 'John', 'Smith', '2 Main St'),
  (3, 'Jane', 'Roe',   '3 Main St'),
  (4, 'Ava',  'Lee',   '4 Main St');

INSERT INTO items VALUES
  (10, 'Laptop',    900.00, 'Electronics'),
  (11, 'Mouse',      25.00, 'Electronics'),
  (20, 'Mug',        12.00, 'Kitchen'),
  (21, 'Kettle',     40.00, 'Kitchen'),
  (30, 'Notebook',    5.00, 'Stationery'),
  (40, 'Tent',      300.00, 'Outdoors');      -- Outdoors never sells in 2022

INSERT INTO sales VALUES
  -- 18 March 2023: three orders, two of them by John Doe, one by John Smith
  ('2023-03-18', 100, 10, 1, 1, 900.00),
  ('2023-03-18', 100, 11, 1, 2,  50.00),      -- order 100 has two lines: 950 total
  ('2023-03-18', 101, 20, 1, 1,  12.00),
  ('2023-03-18', 102, 21, 2, 1,  40.00),
  -- January 2023: customers 1, 3, 3 again
  ('2023-01-05', 200, 30, 1, 4,  20.00),
  ('2023-01-31', 201, 21, 3, 2,  80.00),
  ('2023-01-20', 202, 20, 3, 1,  12.00),
  ('2023-02-01', 203, 30, 4, 1,   5.00),      -- February: excluded from Q3
  -- 2022 sales
  ('2022-06-01', 300, 10, 4, 1, 900.00),
  ('2022-06-01', 300, 11, 4, 2,  50.00),      -- order 300 ties order 100 at 950
  ('2022-07-04', 301, 20, 3, 5,  60.00),
  ('2022-08-10', 302, 30, 2, 10, 50.00),
  ('2021-12-31', 303, 21, 2, 20, 800.00);     -- 2021: must not count toward 2022
"""


@pytest.fixture(scope="module")
def db() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute((ROOT / "schema.sql").read_text(encoding="utf-8"))
    con.execute(SEED)
    return con


def run(db: duckdb.DuckDBPyConnection, name: str) -> list[tuple]:
    return db.execute((ROOT / "queries" / name).read_text(encoding="utf-8")).fetchall()


def test_q1_counts_distinct_orders_not_lines(db) -> None:
    assert run(db, "q1_orders_on_date.sql") == [(3,)]  # 4 lines, 3 orders


def test_q2_only_john_doe(db) -> None:
    assert run(db, "q2_orders_by_customer_on_date.sql") == [(2,)]  # orders 100, 101; not John Smith


def test_q3_january_customers_and_average_spend(db) -> None:
    # customer 1 spent 20, customer 3 spent 80 + 12 = 92 -> average 56
    assert run(db, "q3_january_customers_and_spend.sql") == [(2, Decimal("56.00"))]


def test_q4_includes_departments_with_no_2022_sales(db) -> None:
    rows = run(db, "q4_departments_under_600_in_2022.sql")
    # Outdoors: $0 (no 2022 sales), Kitchen: $60, Stationery: $50; Electronics made $950
    assert rows == [("Outdoors", Decimal("0.00")), ("Stationery", Decimal("50.00")), ("Kitchen", Decimal("60.00"))]


def test_q5_ranges_over_whole_orders(db) -> None:
    # Largest order is 950 (two lines), not the 900 single line; smallest is order 203 at 5
    assert run(db, "q5_order_revenue_range.sql") == [(Decimal("950.00"), Decimal("5.00"))]


def test_q6_returns_every_order_tied_for_top(db) -> None:
    rows = run(db, "q6_items_in_top_order.sql")
    assert {r[0] for r in rows} == {100, 300}
    assert len(rows) == 4


def test_original_q2_bug_is_real(db) -> None:
    """The original LEFT JOIN with filters in ON counts every order in the table."""
    original = """
        SELECT COUNT(DISTINCT s.order_id) FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.customer_id
        AND s.sale_date = DATE '2023-03-18' AND c.first_name = 'John' AND c.last_name = 'Doe'
    """
    total_orders = db.execute("SELECT COUNT(DISTINCT order_id) FROM sales").fetchone()[0]
    assert db.execute(original).fetchone()[0] == total_orders != 2
