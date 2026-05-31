"""
02_clean_and_model.py
Cleans the raw file and creates Power BI-ready fact and dimension CSV files.

Run:
python 02_clean_and_model.py
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw" / "saudi_tourism_hospitality_sample.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW_FILE)

# Basic data quality checks
required_columns = [
    "date", "year", "quarter", "month_number", "month_name", "region", "zone",
    "main_city", "visitor_type", "travel_purpose", "accommodation_type",
    "visitors", "tourist_nights", "spend_sar", "rooms_available", "rooms_sold",
    "occupancy_rate", "average_daily_rate_sar", "room_revenue_sar",
    "cancellation_rate", "satisfaction_score"
]

missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

df["date"] = pd.to_datetime(df["date"]).dt.date
df = df.drop_duplicates()

numeric_columns = [
    "visitors", "tourist_nights", "spend_sar", "rooms_available", "rooms_sold",
    "occupancy_rate", "average_daily_rate_sar", "room_revenue_sar",
    "cancellation_rate", "satisfaction_score"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df[numeric_columns] = df[numeric_columns].fillna(0)

# Remove impossible values
df = df[df["visitors"] >= 0]
df = df[df["rooms_available"] >= 0]
df = df[df["rooms_sold"] >= 0]
df.loc[df["rooms_sold"] > df["rooms_available"], "rooms_sold"] = df["rooms_available"]

# Recalculate ratios from base columns
df["occupancy_rate"] = df["rooms_sold"] / df["rooms_available"].replace(0, pd.NA)
df["occupancy_rate"] = df["occupancy_rate"].fillna(0).round(4)

# Build dimensions
dim_date = (
    df[["date", "year", "quarter", "month_number", "month_name"]]
    .drop_duplicates()
    .sort_values("date")
)

dim_region = (
    df[["region", "zone", "main_city"]]
    .drop_duplicates()
    .sort_values("region")
    .reset_index(drop=True)
)
dim_region.insert(0, "region_id", range(1, len(dim_region) + 1))

dim_segment = (
    df[["visitor_type", "travel_purpose", "accommodation_type"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
dim_segment.insert(0, "segment_id", range(1, len(dim_segment) + 1))

fact = (
    df.merge(dim_region, on=["region", "zone", "main_city"])
    .merge(dim_segment, on=["visitor_type", "travel_purpose", "accommodation_type"])
)

fact = fact[
    [
        "date", "region_id", "segment_id", "visitors", "tourist_nights",
        "spend_sar", "rooms_available", "rooms_sold", "occupancy_rate",
        "average_daily_rate_sar", "room_revenue_sar", "cancellation_rate",
        "satisfaction_score"
    ]
]

dim_date.to_csv(PROCESSED_DIR / "dim_date.csv", index=False)
dim_region.to_csv(PROCESSED_DIR / "dim_region.csv", index=False)
dim_segment.to_csv(PROCESSED_DIR / "dim_segment.csv", index=False)
fact.to_csv(PROCESSED_DIR / "fact_tourism_monthly.csv", index=False)

print("Created Power BI model files:")
print(PROCESSED_DIR / "dim_date.csv")
print(PROCESSED_DIR / "dim_region.csv")
print(PROCESSED_DIR / "dim_segment.csv")
print(PROCESSED_DIR / "fact_tourism_monthly.csv")
print(f"Fact rows: {len(fact):,}")
