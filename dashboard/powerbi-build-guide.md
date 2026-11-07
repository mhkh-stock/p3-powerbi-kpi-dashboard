# Power BI build guide — NoorMart KPI dashboard (~15 minutes)

Builds the finished `.pbix` from this repo's model in Power BI Desktop
(Windows, free). No step needs anything outside this repo.

## 1. Import (2 min)

Power BI Desktop → Get Data → Text/CSV → import all 5 files from
`data/processed/`: `fact_sales.csv`, `dim_product.csv`, `dim_region.csv`,
`dim_channel.csv`, `dim_date.csv`. In Power Query, set `sales_amount`,
`profit`, `unit_price`, `unit_cost`, `quantity` to Whole Number, and
`order_date` and `dim_date[month_date]` to Date. Load.

## 2. Relationships (2 min, Model view)

Single-direction, one-to-many, from each dimension to the fact:

- `dim_product[product_id]` → `fact_sales[product_id]`
- `dim_region[region_id]` → `fact_sales[region_id]`
- `dim_channel[channel_id]` → `fact_sales[channel_id]`
- `dim_date[month]` → `fact_sales[month]`

One fact table, four dimensions — that star shape is why every visual
agrees on the same totals.

## 3. Measures (3 min)

Modeling → New measure, paste each measure from `dax/measures.dax`:
Total Sales, Total Profit, Profit Margin %, Total Orders, Total Units,
Average Order Value. Format sales/profit as whole PKR, margin as %.

`dim_date` already ships a `month_date` column (first of each month,
set to Date in step 1), so paste Sales Previous Month and
Sales MoM Growth % as-is — no extra column needed.

## 4. Page layout (8 min, one page, top to bottom)

1. **KPI cards (top row):** Total Sales · Total Profit · Profit Margin %
   · Average Order Value — the four numbers a manager reads first.
2. **Line chart:** Total Sales by `dim_date[month_name]` (Jan → Jun
   order: sort by `dim_date[date_id]`). Shows the April dip and May recovery.
3. **Bar chart:** Total Sales by `dim_region[region]` — Punjab first.
4. **Donut chart:** Total Sales by `dim_product[category]` — Furniture first.
5. **Table:** `dim_product[product]`, Total Sales, Total Profit, Profit
   Margin % — sorted by Total Sales descending; Office Chair Ergo on top.
6. **Slicers (left or top):** `dim_region[region]`, `dim_product[category]`,
   `dim_channel[channel]` — every visual must respond to all three.

## 5. Check before you call it done

- KPI cards match the README: sales 11,804,808 · profit 5,360,644 ·
  margin 45.4% · AOV 9,837 (on this SAMPLE data).
- Filter to one region: every visual moves, and the KPI cards move too.
  If a visual does not move, its relationship is wrong — fix step 2.
- Save as `.pbix` and publish/share from Power BI Service on a real order.

## What the preview renders are

`dashboard/previews/*.png` are matplotlib renders of the same data,
made so this repo shows the charts without Power BI — regenerate them
any time with `python3 src/make_previews.py` (reads `data/model.db`). They are labelled
as renders in the README and are **not** presented as Power BI
screenshots. The real screenshots come from the `.pbix` built above.
