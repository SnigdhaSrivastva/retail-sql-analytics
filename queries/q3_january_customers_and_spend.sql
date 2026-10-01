-- Customers who purchased in January 2023 and their average total spend.
-- Fix: a half-open date range includes all of 31 January if sale_date ever becomes a timestamp.
SELECT COUNT(*)                     AS customers,
       ROUND(AVG(total_spent), 2)   AS avg_spend_per_customer
FROM (
    SELECT customer_id, SUM(revenue) AS total_spent
    FROM sales
    WHERE sale_date >= DATE '2023-01-01' AND sale_date < DATE '2023-02-01'
    GROUP BY customer_id
) AS per_customer;
