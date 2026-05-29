import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sqlite3

np.random.seed(42)
random.seed(42)

# --- 1. GENERATE RAW (DIRTY) DATA ---
# This simulates what a real raw export from an ad server might look like

n = 500

advertisers = ['RBC', 'Marriott Hotels', 'Hertz', 'Samsung', 'Rogers', 'Expedia', 'TD Bank', 'Hilton']
placements = ['In-flight Entertainment', 'Seatback Screen', 'WiFi Portal', 'Boarding Gate Display']
segments = ['Business Traveller', 'Leisure Traveller', 'International Traveller', 'Frequent Flyer']
routes = ['YYZ-LAX', 'YUL-CDG', 'YVR-NRT', 'YYZ-LHR', 'YYC-YYZ', 'YUL-JFK', 'YYZ-MEX']
campaigns = ['Brand Awareness Q1', 'Product Launch Q1', 'Retargeting Q2', 'Seasonal Promo Q2', 'Brand Awareness Q2']

start_date = datetime(2024, 1, 1)

rows = []
for i in range(n):
    advertiser = random.choice(advertisers)
    placement = random.choice(placements)
    segment = random.choice(segments)
    route = random.choice(routes)
    campaign = random.choice(campaigns)
    date = start_date + timedelta(days=random.randint(0, 180))

    # Simulate realistic performance by placement
    base_impressions = {
        'In-flight Entertainment': random.randint(8000, 25000),
        'Seatback Screen': random.randint(5000, 18000),
        'WiFi Portal': random.randint(2000, 8000),
        'Boarding Gate Display': random.randint(3000, 12000)
    }[placement]

    # CTR varies by segment
    ctr_base = {
        'Business Traveller': random.uniform(0.03, 0.07),
        'Leisure Traveller': random.uniform(0.02, 0.05),
        'International Traveller': random.uniform(0.025, 0.055),
        'Frequent Flyer': random.uniform(0.04, 0.08)
    }[segment]

    impressions = base_impressions
    clicks = int(impressions * ctr_base)
    cpc = round(random.uniform(0.80, 3.50), 2)
    spend = round(clicks * cpc, 2)
    conversions = int(clicks * random.uniform(0.05, 0.18))
    revenue = round(conversions * random.uniform(50, 400), 2)

    # Introduce dirty data: missing values, duplicates, formatting issues
    if random.random() < 0.05:
        impressions = None  # missing
    if random.random() < 0.03:
        cpc = -abs(cpc)  # negative CPC (error)
    if random.random() < 0.04:
        advertiser = advertiser.lower()  # inconsistent casing
    if random.random() < 0.02:
        date = None  # missing date

    rows.append({
        'campaign_id': f'AC{str(i+1000)}',
        'date': date,
        'advertiser': advertiser,
        'campaign_name': campaign,
        'placement': placement,
        'passenger_segment': segment,
        'route': route,
        'impressions': impressions,
        'clicks': clicks,
        'spend_cad': spend,
        'cpc': cpc,
        'conversions': conversions,
        'revenue_cad': revenue
    })

# Add intentional duplicates
rows += random.sample(rows, 15)

raw_df = pd.DataFrame(rows)
raw_df.to_csv('/home/claude/ac_media_raw.csv', index=False)
print(f"Raw dataset: {len(raw_df)} rows, {raw_df.isnull().sum().sum()} missing values, {raw_df.duplicated().sum()} duplicates")


# --- 2. DATA CLEANING (Python) ---

df = raw_df.copy()

print("\n--- CLEANING STEPS ---")

# Step 1: Remove duplicates
before = len(df)
df = df.drop_duplicates()
print(f"Step 1 — Removed {before - len(df)} duplicate rows")

# Step 2: Handle missing impressions (impute with placement median)
missing_imp = df['impressions'].isnull().sum()
df['impressions'] = df.groupby('placement')['impressions'].transform(
    lambda x: x.fillna(x.median())
)
print(f"Step 2 — Imputed {missing_imp} missing impression values with placement median")

# Step 3: Handle missing dates (drop — date is required for time series)
missing_dates = df['date'].isnull().sum()
df = df.dropna(subset=['date'])
print(f"Step 3 — Dropped {missing_dates} rows with missing dates")

# Step 4: Fix negative CPC values
negative_cpc = (df['cpc'] < 0).sum()
df['cpc'] = df['cpc'].abs()
print(f"Step 4 — Fixed {negative_cpc} negative CPC values")

# Step 5: Standardise advertiser casing
df['advertiser'] = df['advertiser'].str.title()
print(f"Step 5 — Standardised advertiser name casing")

# Step 6: Derive calculated metrics
df['ctr'] = (df['clicks'] / df['impressions']).round(4)
df['conversion_rate'] = (df['conversions'] / df['clicks'].replace(0, np.nan)).round(4)
df['roas'] = (df['revenue_cad'] / df['spend_cad'].replace(0, np.nan)).round(2)
df['date'] = pd.to_datetime(df['date'])
df['week'] = df['date'].dt.isocalendar().week
df['month'] = df['date'].dt.month
print(f"Step 6 — Derived CTR, conversion rate, ROAS, week, month columns")

print(f"\nClean dataset: {len(df)} rows, {df.isnull().sum().sum()} missing values remaining")

df.to_csv('/home/claude/ac_media_clean.csv', index=False)
print("Saved: ac_media_clean.csv")


# --- 3. LOAD INTO SQLite (SQL layer) ---

conn = sqlite3.connect('/home/claude/ac_media.db')
df.to_sql('campaigns', conn, if_exists='replace', index=False)

# Write meaningful SQL queries
queries = {
    "Top advertisers by ROAS": """
        SELECT advertiser,
               COUNT(*) as campaigns,
               ROUND(SUM(spend_cad), 2) as total_spend,
               ROUND(SUM(revenue_cad), 2) as total_revenue,
               ROUND(AVG(roas), 2) as avg_roas
        FROM campaigns
        GROUP BY advertiser
        ORDER BY avg_roas DESC
        LIMIT 5
    """,
    "CTR by placement": """
        SELECT placement,
               ROUND(AVG(ctr)*100, 2) as avg_ctr_pct,
               ROUND(AVG(cpc), 2) as avg_cpc_cad,
               SUM(impressions) as total_impressions,
               SUM(clicks) as total_clicks
        FROM campaigns
        GROUP BY placement
        ORDER BY avg_ctr_pct DESC
    """,
    "Performance by passenger segment": """
        SELECT passenger_segment,
               ROUND(AVG(ctr)*100, 2) as avg_ctr_pct,
               ROUND(AVG(conversion_rate)*100, 2) as avg_conv_rate_pct,
               ROUND(AVG(roas), 2) as avg_roas,
               COUNT(*) as total_campaigns
        FROM campaigns
        GROUP BY passenger_segment
        ORDER BY avg_roas DESC
    """,
    "Weekly spend trend": """
        SELECT week,
               ROUND(SUM(spend_cad), 2) as weekly_spend,
               SUM(impressions) as weekly_impressions,
               SUM(conversions) as weekly_conversions
        FROM campaigns
        GROUP BY week
        ORDER BY week
        LIMIT 10
    """
}

print("\n--- SQL QUERY RESULTS ---")
results = {}
for title, query in queries.items():
    result = pd.read_sql_query(query, conn)
    results[title] = result
    print(f"\n{title}:")
    print(result.to_string(index=False))

conn.close()

# Save query results for PowerBI
for title, df_result in results.items():
    filename = title.lower().replace(' ', '_').replace('/', '_')
    df_result.to_csv(f'/home/claude/{filename}.csv', index=False)

print("\n\nAll files saved. Ready for PowerBI import and Lovable dashboard.")
