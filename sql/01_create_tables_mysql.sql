-- Saudi Tourism and Hospitality Analytics Project
-- Database: MySQL 8.x
-- Load the processed CSV files into these tables using MySQL Workbench Table Data Import Wizard.

CREATE DATABASE IF NOT EXISTS saudi_tourism_analytics;
USE saudi_tourism_analytics;

DROP TABLE IF EXISTS fact_tourism_monthly;
DROP TABLE IF EXISTS dim_segment;
DROP TABLE IF EXISTS dim_region;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INT,
    quarter VARCHAR(2),
    month_number INT,
    month_name VARCHAR(10)
);

CREATE TABLE dim_region (
    region_id INT PRIMARY KEY,
    region VARCHAR(100),
    zone VARCHAR(100),
    main_city VARCHAR(100)
);

CREATE TABLE dim_segment (
    segment_id INT PRIMARY KEY,
    visitor_type VARCHAR(50),
    travel_purpose VARCHAR(100),
    accommodation_type VARCHAR(100)
);

CREATE TABLE fact_tourism_monthly (
    date DATE,
    region_id INT,
    segment_id INT,
    visitors INT,
    tourist_nights INT,
    spend_sar BIGINT,
    rooms_available INT,
    rooms_sold INT,
    occupancy_rate DECIMAL(10,4),
    average_daily_rate_sar DECIMAL(10,2),
    room_revenue_sar BIGINT,
    cancellation_rate DECIMAL(10,4),
    satisfaction_score DECIMAL(10,2),
    FOREIGN KEY (date) REFERENCES dim_date(date),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id),
    FOREIGN KEY (segment_id) REFERENCES dim_segment(segment_id)
);

CREATE INDEX idx_fact_date ON fact_tourism_monthly(date);
CREATE INDEX idx_fact_region ON fact_tourism_monthly(region_id);
CREATE INDEX idx_fact_segment ON fact_tourism_monthly(segment_id);