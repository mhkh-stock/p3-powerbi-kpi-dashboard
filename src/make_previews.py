"""P3 — regenerate the dashboard preview renders from data/model.db.

The previews in dashboard/previews/ are matplotlib renders of the same
SAMPLE data (labelled as renders, NOT Power BI screenshots). Re-run any
time after rebuilding the model: same data -> same charts.

Usage: python3 src/make_previews.py   (run from the project folder)
Requires: matplotlib (see requirements.txt). Stdlib sqlite3 otherwise.
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "previews"
OUT.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(ROOT / "data" / "model.db")

# Monthly trend (Jan -> Jun, in month order).
months, sales = zip(*con.execute(
    "SELECT d.month_name, SUM(f.sales_amount) FROM fact_sales f "
    "JOIN dim_date d ON d.month = f.month "
    "GROUP BY f.month ORDER BY f.month"))
# Sales by category, descending.
cats, cat_sales = zip(*con.execute(
    "SELECT p.category, SUM(f.sales_amount) FROM fact_sales f "
    "JOIN dim_product p ON p.product_id = f.product_id "
    "GROUP BY p.category ORDER BY SUM(f.sales_amount) DESC"))
# Sales by region, descending.
regs, reg_sales = zip(*con.execute(
    "SELECT r.region, SUM(f.sales_amount) FROM fact_sales f "
    "JOIN dim_region r ON r.region_id = f.region_id "
    "GROUP BY r.region ORDER BY SUM(f.sales_amount) DESC"))
con.close()

M = 1_000_000  # axis in PKR millions, so no "1e6" offset label overlaps

fig, ax = plt.subplots(figsize=(11.7, 5.85))
ax.plot(months, [s / M for s in sales], marker="o")
for x, s in zip(months, sales):
    ax.annotate(f"{s / M:.2f}M", (x, s / M), textcoords="offset points",
                xytext=(0, 8), ha="center")
ax.set_title("NoorMart monthly sales, Jan–Jun 2026 (PKR) — preview render")
ax.set_ylabel("PKR millions")
ax.set_ylim(min(sales) / M - 0.15, max(sales) / M + 0.15)
fig.tight_layout()
fig.savefig(OUT / "monthly-trend.png", dpi=100)
plt.close(fig)

fig, ax = plt.subplots(figsize=(11.7, 5.85))
ax.bar(cats, [s / M for s in cat_sales])
ax.set_title("Sales by category (PKR millions) — preview render")
ax.set_ylabel("PKR millions")
fig.tight_layout()
fig.savefig(OUT / "sales-by-category.png", dpi=100)
plt.close(fig)

fig, ax = plt.subplots(figsize=(11.7, 5.85))
ax.barh(list(reversed(regs)), [s / M for s in reversed(reg_sales)])
ax.set_title("Sales by region (PKR millions) — preview render")
ax.set_xlabel("PKR millions")
fig.tight_layout()
fig.savefig(OUT / "sales-by-region.png", dpi=100)
plt.close(fig)

print("Wrote:", sorted(p.name for p in OUT.glob("*.png")))
