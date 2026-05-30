-- ============================================================
-- AC Media Analytics — SQL Query Library
-- Author: Hai-Huong Le Vu
-- Database: AC Media campaign performance (SQLite)
-- Purpose: Business intelligence queries for retail media network
-- ============================================================
-- Table: campaigns
-- Columns: campaign_id, date, advertiser, campaign_name, placement,
--          passenger_segment, route, impressions, clicks, spend_cad,
--          cpc, conversions, revenue_cad, ctr, conversion_rate,
--          roas, week, month
-- ============================================================


-- ============================================================
-- SECTION 1: CAMPAIGN PERFORMANCE OVERVIEW
-- ============================================================

-- Query 1: Overall campaign KPI summary
-- Purpose: Executive-level snapshot of total media performance
SELECT
    COUNT(DISTINCT campaign_id)        AS total_campaigns,
    COUNT(DISTINCT advertiser)         AS total_advertisers,
    ROUND(SUM(impressions), 0)         AS total_impressions,
    ROUND(SUM(clicks), 0)              AS total_clicks,
    ROUND(SUM(spend_cad), 2)           AS total_spend_cad,
    ROUND(SUM(revenue_cad), 2)         AS total_revenue_cad,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(cpc), 2)                 AS avg_cpc_cad,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(AVG(conversion_rate)*100, 2) AS avg_conversion_rate_pct
FROM campaigns;


-- Query 2: Top 5 advertisers by ROAS
-- Purpose: Identify highest-value clients for account prioritisation
SELECT
    advertiser,
    COUNT(DISTINCT campaign_id)        AS campaigns_run,
    ROUND(SUM(spend_cad), 2)           AS total_spend_cad,
    ROUND(SUM(revenue_cad), 2)         AS total_revenue_cad,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct
FROM campaigns
GROUP BY advertiser
ORDER BY avg_roas DESC
LIMIT 5;


-- Query 3: Campaign performance ranked within each advertiser
-- Purpose: Identify best and worst performing campaigns per client
-- Used for: Post-campaign reporting to vendors
SELECT
    advertiser,
    campaign_name,
    ROUND(SUM(spend_cad), 2)           AS total_spend_cad,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    RANK() OVER (
        PARTITION BY advertiser
        ORDER BY AVG(roas) DESC
    )                                  AS roas_rank_within_advertiser
FROM campaigns
GROUP BY advertiser, campaign_name
ORDER BY advertiser, roas_rank_within_advertiser;


-- ============================================================
-- SECTION 2: PLACEMENT & CHANNEL ANALYSIS
-- ============================================================

-- Query 4: Performance by ad placement
-- Purpose: Determine which AC Media channels drive the best results
-- Insight: Guides inventory pricing and placement recommendations
SELECT
    placement,
    SUM(impressions)                   AS total_impressions,
    SUM(clicks)                        AS total_clicks,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(cpc), 2)                 AS avg_cpc_cad,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(SUM(spend_cad), 2)           AS total_spend_cad
FROM campaigns
GROUP BY placement
ORDER BY avg_ctr_pct DESC;


-- Query 5: Placement efficiency index
-- Purpose: Compare CTR vs cost to find best value placements
-- High CTR + Low CPC = most efficient placement
SELECT
    placement,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(cpc), 2)                 AS avg_cpc_cad,
    ROUND(AVG(ctr) * 100 / AVG(cpc), 4) AS efficiency_index,
    ROUND(AVG(roas), 2)                AS avg_roas
FROM campaigns
GROUP BY placement
ORDER BY efficiency_index DESC;


-- ============================================================
-- SECTION 3: AUDIENCE PROFILING & SEGMENTATION
-- ============================================================

-- Query 6: Performance by passenger segment
-- Purpose: Understand which audience segments drive highest value
-- Used for: Audience profiling reports delivered to AC Media clients
SELECT
    passenger_segment,
    COUNT(DISTINCT campaign_id)        AS campaigns,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(conversion_rate)*100, 2) AS avg_conversion_rate_pct,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(AVG(cpc), 2)                 AS avg_cpc_cad
FROM campaigns
GROUP BY passenger_segment
ORDER BY avg_roas DESC;


-- Query 7: High-value segment identification
-- Purpose: Flag segments where engagement is high but conversion is low
-- Insight: These segments need offer optimisation, not more impressions
SELECT
    passenger_segment,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(conversion_rate)*100, 2) AS avg_conversion_rate_pct,
    ROUND(AVG(roas), 2)                AS avg_roas,
    CASE
        WHEN AVG(ctr) > 0.05 AND AVG(conversion_rate) < 0.08
            THEN 'High engagement, low conversion — optimise offer'
        WHEN AVG(ctr) > 0.05 AND AVG(conversion_rate) >= 0.08
            THEN 'High engagement, high conversion — scale spend'
        WHEN AVG(ctr) <= 0.05 AND AVG(roas) > 12
            THEN 'Low CTR but high ROAS — high intent audience'
        ELSE 'Monitor — below average performance'
    END                                AS strategic_recommendation
FROM campaigns
GROUP BY passenger_segment
ORDER BY avg_roas DESC;


-- Query 8: Route-level performance
-- Purpose: Identify which flight routes carry the most valuable audiences
SELECT
    route,
    COUNT(DISTINCT campaign_id)        AS campaigns,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(SUM(impressions), 0)         AS total_impressions
FROM campaigns
GROUP BY route
ORDER BY avg_roas DESC
LIMIT 10;


-- ============================================================
-- SECTION 4: TIME SERIES & TREND ANALYSIS
-- ============================================================

-- Query 9: Weekly spend and performance trend
-- Purpose: Track campaign pacing and performance over time
-- Used for: Weekly stakeholder reporting
SELECT
    week,
    ROUND(SUM(spend_cad), 2)           AS weekly_spend_cad,
    SUM(impressions)                   AS weekly_impressions,
    SUM(clicks)                        AS weekly_clicks,
    SUM(conversions)                   AS weekly_conversions,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(roas), 2)                AS avg_roas
FROM campaigns
GROUP BY week
ORDER BY week;


-- Query 10: Month-over-month performance change
-- Purpose: Identify growth or decline trends across key metrics
WITH monthly AS (
    SELECT
        month,
        ROUND(SUM(spend_cad), 2)       AS monthly_spend,
        ROUND(AVG(roas), 2)            AS avg_roas,
        ROUND(AVG(ctr) * 100, 2)       AS avg_ctr_pct,
        SUM(conversions)               AS total_conversions
    FROM campaigns
    GROUP BY month
)
SELECT
    month,
    monthly_spend,
    avg_roas,
    avg_ctr_pct,
    total_conversions,
    ROUND(monthly_spend - LAG(monthly_spend) OVER (ORDER BY month), 2)
        AS spend_change_vs_prev_month,
    ROUND(avg_roas - LAG(avg_roas) OVER (ORDER BY month), 2)
        AS roas_change_vs_prev_month
FROM monthly
ORDER BY month;


-- ============================================================
-- SECTION 5: A/B TEST & CAMPAIGN COMPARISON
-- ============================================================

-- Query 11: Compare two campaign types head-to-head
-- Purpose: Support test/control analysis for campaign optimisation
SELECT
    campaign_name,
    COUNT(DISTINCT campaign_id)        AS campaigns,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    ROUND(AVG(conversion_rate)*100, 2) AS avg_conv_rate_pct,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(AVG(cpc), 2)                 AS avg_cpc_cad,
    ROUND(SUM(spend_cad), 2)           AS total_spend_cad
FROM campaigns
GROUP BY campaign_name
ORDER BY avg_roas DESC;


-- Query 12: Advertiser × Placement performance matrix
-- Purpose: Which advertisers perform best on which placements?
-- Used for: Custom placement recommendations per client
SELECT
    advertiser,
    placement,
    ROUND(AVG(roas), 2)                AS avg_roas,
    ROUND(AVG(ctr) * 100, 2)           AS avg_ctr_pct,
    COUNT(DISTINCT campaign_id)        AS campaigns
FROM campaigns
GROUP BY advertiser, placement
ORDER BY advertiser, avg_roas DESC;


-- ============================================================
-- SECTION 6: DATA QUALITY & AUDIT QUERIES
-- ============================================================

-- Query 13: Data completeness check
-- Purpose: Identify missing or anomalous values before reporting
SELECT
    COUNT(*)                           AS total_rows,
    SUM(CASE WHEN impressions IS NULL THEN 1 ELSE 0 END)   AS null_impressions,
    SUM(CASE WHEN cpc < 0 THEN 1 ELSE 0 END)               AS negative_cpc,
    SUM(CASE WHEN ctr > 1 THEN 1 ELSE 0 END)               AS impossible_ctr,
    SUM(CASE WHEN roas < 0 THEN 1 ELSE 0 END)              AS negative_roas,
    SUM(CASE WHEN spend_cad = 0 THEN 1 ELSE 0 END)         AS zero_spend_campaigns
FROM campaigns;


-- Query 14: Top 10% campaigns by ROAS (high performers)
-- Purpose: Identify benchmark campaigns for best practice analysis
SELECT
    campaign_id,
    advertiser,
    campaign_name,
    placement,
    passenger_segment,
    ROUND(roas, 2)                     AS roas,
    ROUND(ctr * 100, 2)                AS ctr_pct,
    ROUND(spend_cad, 2)                AS spend_cad
FROM campaigns
WHERE roas >= (
    SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY roas)
    FROM campaigns
)
ORDER BY roas DESC;


-- Query 15: Budget pacing alert
-- Purpose: Flag campaigns that are underspending vs expected weekly pace
-- Useful for proactive client communication
WITH weekly_avg AS (
    SELECT
        advertiser,
        ROUND(SUM(spend_cad) / COUNT(DISTINCT week), 2) AS avg_weekly_spend
    FROM campaigns
    GROUP BY advertiser
)
SELECT
    c.advertiser,
    c.week,
    ROUND(SUM(c.spend_cad), 2)         AS actual_weekly_spend,
    w.avg_weekly_spend                 AS expected_weekly_spend,
    CASE
        WHEN SUM(c.spend_cad) < w.avg_weekly_spend * 0.8
            THEN 'UNDERPACING — flag for client review'
        WHEN SUM(c.spend_cad) > w.avg_weekly_spend * 1.2
            THEN 'OVERPACING — check budget cap'
        ELSE 'On track'
    END                                AS pacing_status
FROM campaigns c
JOIN weekly_avg w ON c.advertiser = w.advertiser
GROUP BY c.advertiser, c.week, w.avg_weekly_spend
ORDER BY c.advertiser, c.week;
