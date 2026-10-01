-- Departments that generated less than $600 in 2022.
-- Fixes: HAVING referenced an alias that was never defined; and an inner join silently
-- dropped departments with *no* 2022 sales, which are the lowest earners of all.
-- Start from items, LEFT JOIN 2022 sales, and treat no sales as $0.
SELECT i.department,
       COALESCE(SUM(s.revenue), 0) AS revenue_2022
FROM items i
LEFT JOIN sales s
       ON s.item_id = i.item_id
      AND s.sale_date >= DATE '2022-01-01' AND s.sale_date < DATE '2023-01-01'
GROUP BY i.department
HAVING COALESCE(SUM(s.revenue), 0) < 600
ORDER BY revenue_2022, i.department;
