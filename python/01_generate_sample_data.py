"""
01_generate_sample_data.py
Creates a Saudi tourism and hospitality sample dataset for a one-day Power BI portfolio project.

Run:
python 01_generate_sample_data.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

dates = pd.date_range("2022-01-01", "2025-12-01", freq="MS")

regions = [
    ("Riyadh", "Central", "Riyadh"),
    ("Makkah", "Western", "Jeddah"),
    ("Madinah", "Western", "Madinah"),
    ("Eastern Province", "Eastern", "Dammam"),
    ("Asir", "Southern", "Abha"),
    ("Tabuk", "Northern", "Tabuk"),
]

visitor_types = ["Domestic", "Inbound"]
purposes = ["Leisure", "Business", "Religious", "Family Visit", "Events"]
accommodations = ["Hotel", "Serviced Apartment", "Resort", "Other Paid Accommodation"]

rows = []

for date in dates:
    month = date.month
    year = date.year

    season_mult = (
        1.0
        + 0.15 * np.sin((month - 1) / 12 * 2 * np.pi)
        + (0.25 if month in [3, 4, 12] else 0)
        + (0.18 if month in [6, 7, 8] else 0)
    )
    year_growth = 1 + (year - 2022) * 0.11

    for region, zone, city in regions:
        region_base = {
            "Riyadh": 160000,
            "Makkah": 260000,
            "Madinah": 145000,
            "Eastern Province": 120000,
            "Asir": 85000,
            "Tabuk": 70000,
        }[region]

        for visitor_type in visitor_types:
            visitor_type_multiplier = 1.0 if visitor_type == "Domestic" else 0.55
            inbound_boost = 1 + (year - 2022) * 0.08 if visitor_type == "Inbound" else 1

            for purpose in purposes:
                purpose_multiplier = {
                    "Leisure": 0.34,
                    "Business": 0.16,
                    "Religious": 0.30 if region in ["Makkah", "Madinah"] else 0.05,
                    "Family Visit": 0.18,
                    "Events": 0.12 if region in ["Riyadh", "Makkah", "Eastern Province"] else 0.06,
                }[purpose]

                if purpose == "Religious" and region not in ["Makkah", "Madinah"]:
                    purpose_multiplier *= 0.5

                for accommodation in accommodations:
                    accommodation_multiplier = {
                        "Hotel": 0.55,
                        "Serviced Apartment": 0.22,
                        "Resort": 0.12,
                        "Other Paid Accommodation": 0.11,
                    }[accommodation]

                    visitors = max(
                        50,
                        int(
                            region_base
                            * visitor_type_multiplier
                            * purpose_multiplier
                            * accommodation_multiplier
                            * season_mult
                            * year_growth
                            * inbound_boost
                            * np.random.normal(1, 0.08)
                            / 5
                        ),
                    )

                    avg_stay = {"Domestic": 2.1, "Inbound": 4.2}[visitor_type]
                    if purpose == "Religious":
                        avg_stay += 1.2

                    tourist_nights = int(visitors * max(1.2, avg_stay + np.random.normal(0, 0.2)))

                    spend_per_day = {"Domestic": 420, "Inbound": 760}[visitor_type]
                    if region in ["Riyadh", "Makkah"]:
                        spend_per_day *= 1.15

                    spend_sar = int(tourist_nights * spend_per_day * np.random.normal(1, 0.06))
                    rooms_available = int((visitors / 1.7) * 2.4 + np.random.normal(5000, 1000))
                    rooms_sold = min(rooms_available, int((tourist_nights / 2.0) * np.random.normal(0.55, 0.05)))
                    occupancy_rate = rooms_sold / rooms_available if rooms_available else 0

                    adr = {
                        "Hotel": 520,
                        "Serviced Apartment": 350,
                        "Resort": 720,
                        "Other Paid Accommodation": 240,
                    }[accommodation]

                    if region in ["Riyadh", "Makkah"]:
                        adr *= 1.18

                    adr = max(180, adr * np.random.normal(1, 0.08))
                    room_revenue = int(rooms_sold * adr)
                    cancellation_rate = max(0.01, min(0.22, np.random.normal(0.07, 0.025)))
                    satisfaction_score = max(2.8, min(4.9, np.random.normal(4.15, 0.25)))

                    if accommodation in ["Hotel", "Resort"]:
                        satisfaction_score = min(4.9, satisfaction_score + 0.12)

                    rows.append(
                        {
                            "date": date.date().isoformat(),
                            "year": year,
                            "quarter": f"Q{((month - 1) // 3) + 1}",
                            "month_number": month,
                            "month_name": date.strftime("%b"),
                            "region": region,
                            "zone": zone,
                            "main_city": city,
                            "visitor_type": visitor_type,
                            "travel_purpose": purpose,
                            "accommodation_type": accommodation,
                            "visitors": visitors,
                            "tourist_nights": tourist_nights,
                            "spend_sar": spend_sar,
                            "rooms_available": rooms_available,
                            "rooms_sold": rooms_sold,
                            "occupancy_rate": round(occupancy_rate, 4),
                            "average_daily_rate_sar": round(adr, 2),
                            "room_revenue_sar": room_revenue,
                            "cancellation_rate": round(cancellation_rate, 4),
                            "satisfaction_score": round(satisfaction_score, 2),
                        }
                    )

df = pd.DataFrame(rows)
output_path = RAW_DIR / "saudi_tourism_hospitality_sample.csv"
df.to_csv(output_path, index=False)

print(f"Created: {output_path}")
print(f"Rows: {len(df):,}")
