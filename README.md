# retail-sql-analytics

[![CI](https://github.com/SnigdhaSrivastva/retail-sql-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/SnigdhaSrivastva/retail-sql-analytics/actions/workflows/ci.yml)
![DuckDB](https://img.shields.io/badge/DuckDB-SQL-FFF000?logo=duckdb&logoColor=black)

Six business questions over a retail sales schema, answered in SQL and **verified by tests**. Each query runs against a small dataset whose correct answers were worked out by hand.

> This started as a Data Science Bootcamp SQL assignment at NYU (kept unchanged in [`original/`](original/bootcamp_queries.sql)). Writing tests for it exposed **five bugs**, and each query here documents what was wrong and why the fix is correct.

## Schema

`customers (customer_id, first_name, last_name, address)` · `items (item_id, item_name, price, department)` · `sales (sale_date, order_id, item_id, customer_id, quantity, revenue)`, with one row per order **line** ([`schema.sql`](schema.sql)).

## Queries and what the tests caught

| # | Question | Bug in the original | Fix |
|---|---|---|---|
| [1](queries/q1_orders_on_date.sql) | Orders on 18 Mar 2023 | Dates stored as `'18/03/2023'` strings, inconsistent with the other queries | Real `DATE` type, `COUNT(DISTINCT order_id)` |
| [2](queries/q2_orders_by_customer_on_date.sql) | …placed by John Doe | `LEFT JOIN … ON` with the filters inside the `ON` keeps every sales row, so it **counted every order in the table** (proven by a test) | Inner join, filters in `WHERE` |
| [3](queries/q3_january_customers_and_spend.sql) | January customers and average spend | Inclusive `BETWEEN … '2023-01-31'` silently loses the last day if the column ever holds timestamps | Half-open range `>= Jan 1 AND < Feb 1` |
| [4](queries/q4_departments_under_600_in_2022.sql) | Departments under $600 in 2022 | `HAVING total_revenue` used an alias that was never defined (it doesn't run), and the inner join **dropped departments with no sales**, which are the lowest earners of all | Start from `items`, `LEFT JOIN` 2022 sales with the date filter in `ON`, and `COALESCE` to $0 |
| [5](queries/q5_order_revenue_range.sql) | Highest and lowest revenue per order | `MAX/MIN` over order **lines**, not orders | Sum lines per order first |
| [6](queries/q6_items_in_top_order.sql) | Items in the most lucrative order | `ORDER BY … LIMIT 1` picks one order **arbitrarily** when two are tied | `RANK()` window function returns every tied order |

## Run it

```bash
pip install duckdb pytest
pytest -v
```

The test dataset ([`tests/test_queries.py`](tests/test_queries.py)) is deliberately built around each failure mode: multi-line orders, a "John" who isn't "Doe", a department with no 2022 sales, a 2021 sale on the year boundary, and two orders tied for top revenue.

## Tech

SQL (DuckDB dialect, ANSI-compatible) · window functions · pytest · GitHub Actions
