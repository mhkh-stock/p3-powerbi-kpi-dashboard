# Data dictionary — P3 NoorMart (SAMPLE data)

## Raw file: `data/raw/sales_SAMPLE.csv` (1,200 rows, untouched generator output)

| Column | Type | Meaning |
|---|---|---|
| order_id | text | `NM-00001` … unique per order (one row = one order here) |
| order_date | date | ISO `YYYY-MM-DD`, Jan–Jun 2026 |
| product | text | Product name (20 products) |
| category | text | 5 categories: Electronics, Home & Living, Fashion, Health & Fitness, Furniture |
| region | text | 5 regions: Punjab, Sindh, Khyber Pakhtunkhwa, Balochistan, Islamabad |
| channel | text | In-Store, Online, WhatsApp Order |
| quantity | int | Units in the order (1–3) |
| unit_price | int (PKR) | Selling price per unit |
| unit_cost | int (PKR) | Cost per unit (seeded ratio of price; profit = qty × (price − cost)) |
| sales_amount | int (PKR) | quantity × unit_price — always recomputed, never typed |
| profit | int (PKR) | quantity × (unit_price − unit_cost) |

## Star schema: `data/processed/*.csv` + `data/model.db`

- `fact_sales`: one row per order; keys `product_id`, `region_id`,
  `channel_id` join to the dimensions; `month` is `YYYY-MM` text.
- `dim_product`: `product_id`, `product`, `category` (20 rows).
- `dim_region`: `region_id`, `region` (5 rows).
- `dim_channel`: `channel_id`, `channel` (3 rows).
- `dim_date`: `date_id`, `month` (`2026-01` … `2026-06`), `month_name`.

All money is PKR. All data is fictional SAMPLE data (seed 7) — see README.
