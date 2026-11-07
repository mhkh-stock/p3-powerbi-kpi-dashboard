"""P3 — Power BI KPI Dashboard: build the star-schema model (SAMPLE data).

Generates a seeded fictional retail dataset (NoorMart, Jan-Jun 2026),
loads it into SQLite as a star schema, exports Power BI-ready CSVs,
and prints the KPI numbers the README quotes. Re-run any time:
same seed -> same numbers.

Usage: python3 src/build_model.py   (run from the project folder)
Requires: pandas (see requirements.txt). Stdlib only otherwise.
"""
import random
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 7
random.seed(SEED)

PRODUCTS = [  # (product, category, price_low, price_high, cost_ratio)
    ("Wireless Earbuds", "Electronics", 2500, 6500, 0.62),
    ("Power Bank 20000mAh", "Electronics", 2800, 5500, 0.60),
    ("Bluetooth Speaker", "Electronics", 3500, 9000, 0.58),
    ("LED Desk Lamp", "Electronics", 1800, 4200, 0.55),
    ("Cotton Bedsheet Set", "Home & Living", 3200, 7500, 0.52),
    ("Ceramic Dinner Set", "Home & Living", 8500, 18000, 0.50),
    ("Non-stick Cookware Set", "Home & Living", 6500, 14000, 0.54),
    ("Wall Clock Classic", "Home & Living", 1500, 3800, 0.48),
    ("Running Shoes", "Fashion", 4500, 12000, 0.57),
    ("Leather Wallet", "Fashion", 1800, 4500, 0.45),
    ("Cotton Kurta", "Fashion", 2800, 6500, 0.50),
    ("Sunglasses UV400", "Fashion", 1500, 4200, 0.42),
    ("Whey Protein 1kg", "Health & Fitness", 6500, 12000, 0.60),
    ("Yoga Mat Pro", "Health & Fitness", 1800, 4200, 0.50),
    ("Dumbbell Set 20kg", "Health & Fitness", 5500, 11000, 0.58),
    ("Resistance Bands Kit", "Health & Fitness", 1200, 2800, 0.45),
    ("Office Chair Ergo", "Furniture", 14000, 28000, 0.58),
    ("Study Table Wooden", "Furniture", 9500, 19000, 0.55),
    ("Bookshelf 5-Tier", "Furniture", 7500, 15000, 0.52),
    ("Floor Lamp Modern", "Furniture", 4200, 9500, 0.50),
]
REGIONS = ["Punjab", "Sindh", "Khyber Pakhtunkhwa", "Balochistan", "Islamabad"]
CHANNELS = ["In-Store", "Online", "WhatsApp Order"]
REGION_W = [0.34, 0.26, 0.18, 0.07, 0.15]
CHANNEL_W = [0.52, 0.33, 0.15]


def gen_transactions(n=1200):
    rows = []
    for i in range(1, n + 1):
        month = random.randint(1, 6)
        day = random.randint(1, 28)
        prod, cat, lo, hi, cost_ratio = random.choice(PRODUCTS)
        price = random.randint(lo, hi)
        qty = random.choices([1, 2, 3], weights=[0.72, 0.21, 0.07])[0]
        rows.append({
            "order_id": f"NM-{i:05d}",
            "order_date": f"2026-{month:02d}-{day:02d}",
            "product": prod, "category": cat,
            "region": random.choices(REGIONS, weights=REGION_W)[0],
            "channel": random.choices(CHANNELS, weights=CHANNEL_W)[0],
            "quantity": qty, "unit_price": price,
            "unit_cost": round(price * cost_ratio),
            "sales_amount": qty * price,
            "profit": qty * (price - round(price * cost_ratio)),
        })
    return pd.DataFrame(rows)


def main():
    (ROOT / "data" / "raw").mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "dashboard" / "previews").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)

    df = gen_transactions()
    df.to_csv(ROOT / "data" / "raw" / "sales_SAMPLE.csv", index=False)

    dim_product = (df[["product", "category"]].drop_duplicates()
                   .sort_values("product").reset_index(drop=True))
    dim_product.insert(0, "product_id", range(1, len(dim_product) + 1))
    dim_region = pd.DataFrame({"region_id": range(1, len(REGIONS) + 1),
                               "region": REGIONS})
    dim_channel = pd.DataFrame({"channel_id": range(1, len(CHANNELS) + 1),
                                "channel": CHANNELS})
    dim_date = pd.DataFrame({
        "date_id": range(1, 7),
        "month": [f"2026-{m:02d}" for m in range(1, 7)],
        "month_name": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "month_no": range(1, 7),
        "month_date": [f"2026-{m:02d}-01" for m in range(1, 7)],
    })
    pmap = dict(zip(dim_product["product"], dim_product.product_id))
    rmap = dict(zip(dim_region["region"], dim_region.region_id))
    cmap = dict(zip(dim_channel["channel"], dim_channel.channel_id))
    fact = pd.DataFrame({
        "order_id": df["order_id"], "order_date": df["order_date"],
        "month": df["order_date"].str[:7],
        "product_id": df["product"].map(pmap),
        "region_id": df["region"].map(rmap),
        "channel_id": df["channel"].map(cmap),
        "quantity": df["quantity"], "unit_price": df["unit_price"],
        "unit_cost": df["unit_cost"], "sales_amount": df["sales_amount"],
        "profit": df["profit"],
    })
    for name, table in [("dim_product", dim_product), ("dim_region", dim_region),
                        ("dim_channel", dim_channel), ("dim_date", dim_date),
                        ("fact_sales", fact)]:
        table.to_csv(ROOT / "data" / "processed" / f"{name}.csv", index=False)

    db = ROOT / "data" / "model.db"
    if db.exists():
        db.unlink()
    con = sqlite3.connect(db)
    schema = (ROOT / "sql" / "schema.sql").read_text()
    con.executescript(schema)
    dim_product.to_sql("dim_product", con, if_exists="append", index=False)
    dim_region.to_sql("dim_region", con, if_exists="append", index=False)
    dim_channel.to_sql("dim_channel", con, if_exists="append", index=False)
    dim_date.to_sql("dim_date", con, if_exists="append", index=False)
    fact.to_sql("fact_sales", con, if_exists="append", index=False)
    con.commit()

    kpis = {
        "total_sales": int(fact.sales_amount.sum()),
        "total_profit": int(fact.profit.sum()),
        "orders": int(fact.order_id.nunique()),
        "units": int(fact.quantity.sum()),
        "aov": round(fact.sales_amount.sum() / fact.order_id.nunique()),
        "margin_pct": round(100 * fact.profit.sum() / fact.sales_amount.sum(), 1),
    }
    print("KPIs:", kpis)
    print("fact rows:", len(fact), "| products:", len(dim_product))
    print("DB:", db)
    con.close()


if __name__ == "__main__":
    main()
