"""P3 data-quality checks as code. Run: python3 src/checks.py
Exits non-zero if any check fails. All checks must pass before delivery.
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "data" / "model.db")
fails = []


def check(name, sql, expect):
    got = con.execute(sql).fetchone()[0]
    ok = got == expect
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got}, expected {expect}")
    if not ok:
        fails.append(name)


check("fact rows = 1200", "SELECT COUNT(*) FROM fact_sales", 1200)
check("no duplicate order_id", "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM fact_sales", 0)
check("no null keys", "SELECT COUNT(*) FROM fact_sales WHERE product_id IS NULL OR region_id IS NULL OR channel_id IS NULL", 0)
check("no non-positive qty/price", "SELECT COUNT(*) FROM fact_sales WHERE quantity <= 0 OR unit_price <= 0", 0)
check("sales = qty x price everywhere",
      "SELECT COUNT(*) FROM fact_sales WHERE sales_amount != quantity * unit_price", 0)
check("profit = qty x (price - cost) everywhere",
      "SELECT COUNT(*) FROM fact_sales WHERE profit != quantity * (unit_price - unit_cost)", 0)
check("all fact products exist in dim_product",
      "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product d ON d.product_id = f.product_id WHERE d.product_id IS NULL", 0)
check("all fact regions exist in dim_region",
      "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_region d ON d.region_id = f.region_id WHERE d.region_id IS NULL", 0)
check("all fact channels exist in dim_channel",
      "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_channel d ON d.channel_id = f.channel_id WHERE d.channel_id IS NULL", 0)
check("all fact months exist in dim_date",
      "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_date d ON d.month = f.month WHERE d.month IS NULL", 0)
check("dim_date covers 6 months", "SELECT COUNT(*) FROM dim_date", 6)
check("all months in Jan-Jun 2026",
      "SELECT COUNT(*) FROM fact_sales WHERE month NOT BETWEEN '2026-01' AND '2026-06'", 0)
check("dimensions complete: 20 products", "SELECT COUNT(*) FROM dim_product", 20)
import csv
with open(ROOT / "data" / "raw" / "sales_SAMPLE.csv", newline="") as fh:
    csv_total = sum(int(r["sales_amount"]) for r in csv.DictReader(fh))
db_total = con.execute("SELECT SUM(sales_amount) FROM fact_sales").fetchone()[0]
ok = csv_total == db_total
print(f"{'PASS' if ok else 'FAIL'}  fact total = raw CSV total: {db_total} = {csv_total}")
if not ok:
    fails.append("fact total = raw CSV total")
print("ALL CHECKS PASSED" if not fails else f"{len(fails)} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
