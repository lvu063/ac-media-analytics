# AC Media Analytics
### Campaign Performance Analysis & Fuel Price Impact Modelling
*A portfolio project demonstrating end-to-end data analytics skills applied to Air Canada's retail media business*

---

## Overview

This project simulates the work of a **Specialist, Media Analytics** at Air Canada — from raw data ingestion and cleaning, through SQL-based querying and statistical modelling, to stakeholder-facing interactive reporting.

It is structured as a real analyst workflow across two interconnected analyses:

1. **Campaign Performance Dashboard** — measuring advertiser performance, placement effectiveness, and audience segment behaviour across AC Media's in-flight and airport channels
2. **Jet Fuel Price Volatility Analysis** — modelling the statistical relationship between fuel price shocks and key operational metrics (load factor, route cancellations, revenue)

---

## Live Dashboard

**[View interactive dashboard →](https://ac-media-analytics.lovable.app)**

Built with React. Includes summary KPIs, weekly spend trend, CTR by placement, ROAS by passenger segment, and sortable advertiser table.

---

## Skills Demonstrated

| Skill | Where |
|---|---|
| Python | Data generation, cleaning, pipeline (`python/ac_media_data.py`) |
| SQL | Campaign queries via SQLite — ROAS, CTR, segmentation (`python/ac_media_data.py`) |
| R | OLS regression, correlation analysis, ggplot2 visualisation (`r/ac_fuel_analysis.R`) |
| PowerBI | Campaign performance report (`plots/powerbi_report.png`) |
| Statistics & Data Analysis | Three regression models with interpretation |
| Data Cleaning | 6 documented cleaning steps — duplicates, nulls, negatives, casing |
| Reporting & Presentation | Interactive dashboard + written key findings |
| Digital Marketing Analytics | CTR, CPC, ROAS, conversion rate, audience profiling |

---

## Project Structure

```
ac-media-analytics/
├── python/
│   └── ac_media_data.py        # Data generation, cleaning, SQL queries
├── r/
│   └── ac_fuel_analysis.R      # Regression analysis, visualisations
├── data/
│   ├── ac_media_raw.csv        # Raw dataset (with intentional errors)
│   ├── ac_media_clean.csv      # Cleaned dataset (493 rows)
│   ├── ac_fuel_analysis.csv    # Fuel price time series data
│   ├── top_advertisers_by_roas.csv
│   ├── ctr_by_placement.csv
│   ├── performance_by_passenger_segment.csv
│   └── weekly_spend_trend.csv
└── plots/
    ├── plot1_fuel_price.png    # Fuel price time series with shock annotation
    ├── plot2_regression.png    # OLS regression — fuel price vs load factor
    ├── plot3_revenue_impact.png # Revenue impact coloured by load factor
    └── powerbi_report.png      # Campaign performance PowerBI report
```

---

## Analysis 1 — Campaign Performance (Python + SQL)

### Data Cleaning Steps
Starting from 515 raw rows with intentional data quality issues:

1. Removed **15 duplicate rows**
2. Imputed **19 missing impression values** with placement-level median
3. Dropped **7 rows** with missing dates (required for time series)
4. Fixed **11 negative CPC values** (data entry errors)
5. Standardised **advertiser name casing** for consistent grouping
6. Derived calculated metrics: CTR, conversion rate, ROAS, week, month

Final clean dataset: **493 rows, 0 missing values**

### SQL Key Findings

**Top placement by CTR:** In-flight Entertainment (4.76% avg CTR)

**Highest ROAS advertiser:** Rogers (13.91x average return on ad spend)

**Best-performing segment:** International Travellers — highest ROAS at 13.86x, driven by longer dwell time and premium intent

**Actionable insight:** Frequent Flyers show the highest CTR (5.97%) but lowest ROAS — suggesting high engagement but lower conversion value. Recommend testing higher-value offers for this segment.

---

## Analysis 2 — Fuel Price Impact (R)

### Data
30 months of simulated operational data (Jan 2022 – Jun 2024), including a modelled supply shock period (Jul–Oct 2022) mirroring real-world disruptions.

### Regression Models

**Model 1 — Fuel Price → Load Factor (OLS)**
- Each $1 increase in jet fuel price → **−3.22 pp decline in load factor**
- R² = 0.204, p = 0.012 (statistically significant)

**Model 2 — Revenue Drivers (Multiple Regression)**
- Load factor and ticket yield together explain **42.9% of revenue variance**
- Load factor coefficient: 2.00 (p < 0.001) — strongest driver

**Model 3 — Route Cancellations (Quadratic)**
- Non-linear acceleration above ~$3.50/gallon
- R² = 0.866 — strong model fit

### Key Finding
The 2022 supply shock period averaged **$4.33/gallon** vs **$2.92/gallon** pre-shock — a 48% increase that drove measurable declines in load factor and accelerated route cancellations non-linearly.

---

## How to Run

### Python
```bash
pip install pandas numpy faker
python python/ac_media_data.py
```

### R
```r
install.packages(c("ggplot2", "dplyr", "broom", "scales", "lubridate"))
source("r/ac_fuel_analysis.R")
```

---

## Note on Data
All data in this project is synthetically generated for portfolio demonstration purposes. It does not represent actual Air Canada operational or financial data.

---

*Built by Hai-Huong Le Vu | [LinkedIn](https://www.linkedin.com/in/hai-huong-le-vu/)*
