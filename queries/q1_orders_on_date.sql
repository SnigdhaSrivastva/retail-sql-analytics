-- Total orders completed on 18 March 2023.
-- An order has one row per item, so count DISTINCT orders.
SELECT COUNT(DISTINCT order_id) AS orders
FROM sales
WHERE sale_date = DATE '2023-03-18';
