-- Line items in the most lucrative order(s).
-- Fix: LIMIT 1 picked one order arbitrarily on a tie; RANK keeps every top order.
WITH order_totals AS (
    SELECT order_id, SUM(revenue) AS order_revenue,
           RANK() OVER (ORDER BY SUM(revenue) DESC) AS rnk
    FROM sales
    GROUP BY order_id
)
SELECT s.order_id, s.item_id, i.item_name, s.quantity, s.revenue
FROM sales s
JOIN items i ON i.item_id = s.item_id
JOIN order_totals t ON t.order_id = s.order_id AND t.rnk = 1
ORDER BY s.order_id, s.revenue DESC;
