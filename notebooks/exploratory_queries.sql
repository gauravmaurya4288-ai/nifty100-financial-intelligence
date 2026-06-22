SELECT COUNT(*) FROM companies;

SELECT company_id,
       MAX(market_cap_crore)
FROM market_cap
GROUP BY company_id
ORDER BY 2 DESC
LIMIT 10;

SELECT company_id,
       AVG(roe)
FROM analysis
GROUP BY company_id
ORDER BY 2 DESC
LIMIT 10;

SELECT company_id,
       AVG(close_price)
FROM stock_prices
GROUP BY company_id;

SELECT broad_sector,
       COUNT(*)
FROM sectors
GROUP BY broad_sector;