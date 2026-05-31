USE saudi_tourism_analytics;

-- 1. Executive KPIs
SELECT
    SUM(f.visitors) AS total_visitors,
    SUM(f.tourist_nights) AS total_tourist_nights,
    SUM(f.spend_sar) AS total_spend_sar,
    ROUND(SUM(f.spend_sar) / NULLIF(SUM(f.visitors), 0), 2) AS avg_spend_per_visitor_sar,
    ROUND(SUM(f.rooms_sold) / NULLIF(SUM(f.rooms_available), 0), 4) AS occupancy_rate
FROM fact_tourism_monthly f;

-- 2. Monthly tourism demand trend
SELECT
    d.year,
    d.month_number,
    d.month_name,
    SUM(f.visitors) AS visitors,
    SUM(f.spend_sar) AS spend_sar,
    ROUND(SUM(f.rooms_sold) / NULLIF(SUM(f.rooms_available), 0), 4) AS occupancy_rate
FROM fact_tourism_monthly f
JOIN dim_date d ON f.date = d.date
GROUP BY d.year, d.month_number, d.month_name
ORDER BY d.year, d.month_number;

-- 3. Region ranking by visitors and spend
SELECT
    r.region,
    r.zone,
    SUM(f.visitors) AS visitors,
    SUM(f.spend_sar) AS spend_sar,
    ROUND(SUM(f.spend_sar) / NULLIF(SUM(f.visitors), 0), 2) AS avg_spend_per_visitor_sar
FROM fact_tourism_monthly f
JOIN dim_region r ON f.region_id = r.region_id
GROUP BY r.region, r.zone
ORDER BY visitors DESC;

-- 4. Domestic vs inbound split
SELECT
    s.visitor_type,
    SUM(f.visitors) AS visitors,
    ROUND(100 * SUM(f.visitors) / SUM(SUM(f.visitors)) OVER (), 2) AS visitor_share_pct,
    SUM(f.spend_sar) AS spend_sar,
    ROUND(100 * SUM(f.spend_sar) / SUM(SUM(f.spend_sar)) OVER (), 2) AS spend_share_pct
FROM fact_tourism_monthly f
JOIN dim_segment s ON f.segment_id = s.segment_id
GROUP BY s.visitor_type
ORDER BY visitors DESC;

-- 5. Purpose demand by region
SELECT
    r.region,
    s.travel_purpose,
    SUM(f.visitors) AS visitors,
    SUM(f.spend_sar) AS spend_sar
FROM fact_tourism_monthly f
JOIN dim_region r ON f.region_id = r.region_id
JOIN dim_segment s ON f.segment_id = s.segment_id
GROUP BY r.region, s.travel_purpose
ORDER BY r.region, visitors DESC;

-- 6. Hospitality efficiency by accommodation type
SELECT
    s.accommodation_type,
    SUM(f.rooms_available) AS rooms_available,
    SUM(f.rooms_sold) AS rooms_sold,
    ROUND(SUM(f.rooms_sold) / NULLIF(SUM(f.rooms_available), 0), 4) AS occupancy_rate,
    ROUND(SUM(f.room_revenue_sar) / NULLIF(SUM(f.rooms_sold), 0), 2) AS adr_sar,
    ROUND(SUM(f.room_revenue_sar) / NULLIF(SUM(f.rooms_available), 0), 2) AS revpar_sar
FROM fact_tourism_monthly f
JOIN dim_segment s ON f.segment_id = s.segment_id
GROUP BY s.accommodation_type
ORDER BY revpar_sar DESC;

-- 7. Underperforming region-months
SELECT
    d.year,
    d.month_name,
    r.region,
    SUM(f.visitors) AS visitors,
    ROUND(SUM(f.rooms_sold) / NULLIF(SUM(f.rooms_available), 0), 4) AS occupancy_rate,
    ROUND(AVG(f.satisfaction_score), 2) AS avg_satisfaction
FROM fact_tourism_monthly f
JOIN dim_date d ON f.date = d.date
JOIN dim_region r ON f.region_id = r.region_id
GROUP BY d.year, d.month_number, d.month_name, r.region
HAVING occupancy_rate < 0.55
ORDER BY d.year, d.month_number, occupancy_rate ASC;

-- 8. Year over year visitor growth by region
WITH yearly_region AS (
    SELECT
        d.year,
        r.region,
        SUM(f.visitors) AS visitors
    FROM fact_tourism_monthly f
    JOIN dim_date d ON f.date = d.date
    JOIN dim_region r ON f.region_id = r.region_id
    GROUP BY d.year, r.region
)
SELECT
    year,
    region,
    visitors,
    LAG(visitors) OVER (PARTITION BY region ORDER BY year) AS previous_year_visitors,
    ROUND(
        100 * (visitors - LAG(visitors) OVER (PARTITION BY region ORDER BY year))
        / NULLIF(LAG(visitors) OVER (PARTITION BY region ORDER BY year), 0),
        2
    ) AS yoy_growth_pct
FROM yearly_region
ORDER BY region, year;