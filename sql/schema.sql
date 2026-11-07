-- P3 star schema (SQLite; same shape loads into Power BI / PostgreSQL).
-- fact_sales is the single fact table; every dimension joins on *_id.
CREATE TABLE dim_product (
    product_id INTEGER PRIMARY KEY,
    product TEXT NOT NULL,
    category TEXT NOT NULL
);
CREATE TABLE dim_region (
    region_id INTEGER PRIMARY KEY,
    region TEXT NOT NULL
);
CREATE TABLE dim_channel (
    channel_id INTEGER PRIMARY KEY,
    channel TEXT NOT NULL
);
CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    month TEXT NOT NULL,        -- '2026-01' .. '2026-06'
    month_name TEXT NOT NULL,
    month_no INTEGER NOT NULL,  -- 1 .. 6
    month_date TEXT NOT NULL    -- '2026-01-01' .. first of month; DATEADD target for the DAX MoM measures
);
CREATE TABLE fact_sales (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,   -- ISO YYYY-MM-DD
    month TEXT NOT NULL,
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    channel_id INTEGER NOT NULL REFERENCES dim_channel(channel_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL CHECK (unit_price > 0),
    unit_cost INTEGER NOT NULL CHECK (unit_cost >= 0),
    sales_amount INTEGER NOT NULL,
    profit INTEGER NOT NULL
);
