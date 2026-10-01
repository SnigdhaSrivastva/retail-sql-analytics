-- Orders completed on 18 March 2023 by John Doe.
-- Fix: the original used LEFT JOIN with the filters inside ON, which keeps every
-- sales row and counts all orders. The filters belong in WHERE, with an inner join.
SELECT COUNT(DISTINCT s.order_id) AS orders
FROM sales s
JOIN customers c ON c.customer_id = s.customer_id
WHERE s.sale_date = DATE '2023-03-18'
  AND c.first_name = 'John'
  AND c.last_name = 'Doe';
