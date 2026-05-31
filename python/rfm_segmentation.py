# ============================================================
# AC Media — Advertiser RFM Segmentation
# Author: Hai-Huong Le Vu
# Tools: Python, pandas, matplotlib
# ============================================================
# Business Question:
# How can AC Media segment its advertisers by engagement behaviour
# to prioritise account management and personalise outreach?
#
# RFM Framework:
# - Recency (R):   How recently did the advertiser run a campaign?
# - Frequency (F): How many campaigns have they run?
# - Monetary (M):  How much have they spent in total?
#
# Why RFM for AC Media?
# Retail media networks need to understand which advertisers are
# high-value, at-risk, or dormant — the same logic used in CRM
# and digital marketing to optimise customer lifecycle management.
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ============================================================
# 1. LOAD & PREPARE DATA
# ============================================================

df = pd.read_csv('/home/claude/ac_media_clean.csv')
df['date'] = pd.to_datetime(df['date'])

reference_date = df['date'].max() + timedelta(days=1)
print(f"Reference date (today): {reference_date.date()}")
print(f"Dataset: {len(df)} campaigns, {df['advertiser'].nunique()} advertisers\n")

# ============================================================
# 2. CALCULATE RFM METRICS PER ADVERTISER
# ============================================================

rfm = df.groupby('advertiser').agg(
    last_campaign_date=('date', 'max'),
    frequency=('campaign_id', 'count'),
    monetary=('spend_cad', 'sum'),
    avg_roas=('roas', 'mean'),
    avg_ctr=('ctr', 'mean'),
    total_conversions=('conversions', 'sum'),
    total_revenue=('revenue_cad', 'sum')
).reset_index()

rfm['recency'] = (reference_date - rfm['last_campaign_date']).dt.days
rfm['monetary'] = rfm['monetary'].round(2)
rfm['avg_roas'] = rfm['avg_roas'].round(2)
rfm['avg_ctr'] = rfm['avg_ctr'].round(4)

print("--- RAW RFM METRICS ---")
print(rfm[['advertiser','recency','frequency','monetary',
           'avg_roas','total_conversions']].to_string(index=False))

# ============================================================
# 3. RFM SCORING (1-4 scale)
# Using rank-based cut for robustness with small datasets
# Recency: lower days = higher score
# Frequency & Monetary: higher = higher score
# ============================================================

def score_col(series, ascending=True):
    ranks = series.rank(method='first')
    scores = pd.cut(ranks, bins=4, labels=[1, 2, 3, 4]).astype(int)
    if not ascending:
        scores = 5 - scores
    return scores

rfm['R_score'] = score_col(rfm['recency'], ascending=False)
rfm['F_score'] = score_col(rfm['frequency'], ascending=True)
rfm['M_score'] = score_col(rfm['monetary'], ascending=True)
rfm['RFM_score'] = rfm['R_score'] + rfm['F_score'] + rfm['M_score']

# ============================================================
# 4. SEGMENT CLASSIFICATION
# ============================================================

def classify_segment(row):
    r, f, m = row['R_score'], row['F_score'], row['M_score']
    total = row['RFM_score']
    if r >= 3 and f >= 3 and m >= 3:
        return 'Champions'
    elif r >= 3 and total >= 8:
        return 'Loyal Advertisers'
    elif r >= 3 and f <= 2:
        return 'Promising — New'
    elif r == 2 and total >= 6:
        return 'At Risk — High Value'
    elif r == 1 and total >= 6:
        return 'Churned — High Value'
    elif r <= 2 and total <= 4:
        return 'Dormant'
    else:
        return 'Needs Attention'

rfm['segment'] = rfm.apply(classify_segment, axis=1)

print("\n--- RFM SCORES & SEGMENTS ---")
print(rfm[['advertiser','R_score','F_score','M_score',
           'RFM_score','segment']].to_string(index=False))

# ============================================================
# 5. SEGMENT SUMMARY
# ============================================================

segment_summary = rfm.groupby('segment').agg(
    advertisers=('advertiser', 'count'),
    avg_recency_days=('recency', 'mean'),
    avg_frequency=('frequency', 'mean'),
    avg_spend_cad=('monetary', 'mean'),
    avg_roas=('avg_roas', 'mean'),
    total_revenue=('total_revenue', 'sum')
).round(2).reset_index().sort_values('avg_spend_cad', ascending=False)

print("\n--- SEGMENT SUMMARY ---")
print(segment_summary.to_string(index=False))

# ============================================================
# 6. CRM ACTION PLAN
# ============================================================

recommendations = {
    'Champions':           'Priority accounts — offer premium placements, early access to new inventory, dedicated account manager',
    'Loyal Advertisers':   'Upsell — propose multi-placement packages, annual commitments, increased spend targets',
    'Promising — New':     'Nurture with case studies and performance reports — convert to repeat advertiser within 30 days',
    'At Risk — High Value':'Re-engagement — reach out with performance recap and exclusive offer before churn',
    'Churned — High Value':'Win-back — personalised proposal highlighting missed impressions and competitor activity',
    'Needs Attention':     'Low-touch nurture — automated performance reports, self-serve dashboard access',
    'Dormant':             'Evaluate ROI of re-engagement vs acquisition cost — sunset if no response in 60 days'
}

print("\n--- CRM ACTION PLAN BY SEGMENT ---")
for segment, action in recommendations.items():
    advertisers_in_seg = rfm[rfm['segment'] == segment]['advertiser'].tolist()
    if advertisers_in_seg:
        print(f"\n{segment} ({len(advertisers_in_seg)} advertiser{'s' if len(advertisers_in_seg)>1 else ''}):")
        print(f"  Advertisers : {', '.join(advertisers_in_seg)}")
        print(f"  Action      : {action}")

# ============================================================
# 7. VISUALISATIONS
# ============================================================

segment_colors = {
    'Champions':           '#1B1E2B',
    'Loyal Advertisers':   '#F01428',
    'Promising — New':     '#4A90D9',
    'At Risk — High Value':'#E8A020',
    'Churned — High Value':'#9B59B6',
    'Needs Attention':     '#95A5A6',
    'Dormant':             '#D5D8DC'
}

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle('AC Media — Advertiser RFM Segmentation\nCRM & Audience Profiling Analysis',
             fontsize=13, fontweight='bold', color='#1B1E2B')

# Plot 1: RFM scatter — Recency vs Monetary, sized by Frequency
ax1 = axes[0, 0]
for _, row in rfm.iterrows():
    color = segment_colors.get(row['segment'], '#95A5A6')
    ax1.scatter(row['recency'], row['monetary'],
                s=row['frequency'] * 18,
                color=color, alpha=0.85,
                edgecolors='white', linewidth=0.8)
    ax1.annotate(row['advertiser'].split()[0],
                 (row['recency'], row['monetary']),
                 fontsize=8, ha='center', va='bottom',
                 xytext=(0, 7), textcoords='offset points')
ax1.set_xlabel('Recency (days since last campaign) — lower is better →')
ax1.set_ylabel('Total Spend (CAD)')
ax1.set_title('RFM Map — Recency vs Spend\n(bubble size = campaign frequency)',
              fontweight='bold')
ax1.invert_xaxis()
ax1.grid(True, alpha=0.3)

# Plot 2: Segment distribution
ax2 = axes[0, 1]
seg_counts = rfm['segment'].value_counts()
colors_list = [segment_colors.get(s, '#95A5A6') for s in seg_counts.index]
bars = ax2.barh(seg_counts.index, seg_counts.values,
                color=colors_list, edgecolor='white')
for bar, val in zip(bars, seg_counts.values):
    ax2.text(bar.get_width() + 0.03,
             bar.get_y() + bar.get_height()/2,
             str(val), va='center', fontsize=9)
ax2.set_xlabel('Number of Advertisers')
ax2.set_title('Advertiser Distribution by Segment', fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# Plot 3: Avg spend by segment
ax3 = axes[1, 0]
seg_spend = rfm.groupby('segment')['monetary'].mean().sort_values()
colors_spend = [segment_colors.get(s, '#95A5A6') for s in seg_spend.index]
bars3 = ax3.barh(seg_spend.index, seg_spend.values,
                  color=colors_spend, edgecolor='white')
for bar, val in zip(bars3, seg_spend.values):
    ax3.text(bar.get_width() + 100,
             bar.get_y() + bar.get_height()/2,
             f'${val:,.0f}', va='center', fontsize=8)
ax3.set_xlabel('Average Total Spend (CAD)')
ax3.set_title('Average Spend by Segment', fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# Plot 4: RFM score heatmap
ax4 = axes[1, 1]
rfm_sorted = rfm.sort_values('RFM_score', ascending=False)
heatmap_data = rfm_sorted[['R_score','F_score','M_score']].values
im = ax4.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=1, vmax=4)
ax4.set_xticks(range(3))
ax4.set_xticklabels(['R Score', 'F Score', 'M Score'], fontsize=9)
ax4.set_yticks(range(len(rfm_sorted)))
ax4.set_yticklabels(
    [f"{r['advertiser']} ({r['segment']})" for _, r in rfm_sorted.iterrows()],
    fontsize=7)
ax4.set_title('RFM Score Heatmap by Advertiser', fontweight='bold')
plt.colorbar(im, ax=ax4, label='Score (1=Low, 4=High)')
for i in range(len(rfm_sorted)):
    for j in range(3):
        ax4.text(j, i, str(heatmap_data[i, j]),
                 ha='center', va='center',
                 fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('/home/claude/rfm_segmentation.png', dpi=150,
            bbox_inches='tight', facecolor='white')
plt.close()
print("\nSaved: rfm_segmentation.png")

# ============================================================
# 8. EXPORT
# ============================================================

rfm[['advertiser','segment','RFM_score','recency','frequency',
     'monetary','avg_roas','total_conversions','total_revenue']]\
    .sort_values('RFM_score', ascending=False)\
    .to_csv('/home/claude/rfm_segments.csv', index=False)

print("Saved: rfm_segments.csv")
print(f"\nTotal advertisers segmented : {len(rfm)}")
print(f"Segments identified         : {rfm['segment'].nunique()}")
print(f"Total revenue               : ${rfm['total_revenue'].sum():,.2f} CAD")
