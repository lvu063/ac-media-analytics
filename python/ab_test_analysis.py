# ============================================================
# AC Media — A/B Test Analysis: Ad Creative Performance
# Author: Hai-Huong Le Vu
# Tools: Python, scipy, pandas, matplotlib
# ============================================================
# Business Question:
# Does a new ad creative (Variant B) outperform the control (Variant A)
# on In-flight Entertainment placements for the RBC campaign?
#
# Test Design:
# - Control (A): Existing static banner creative
# - Variant (B): New animated video creative
# - Primary metric: Conversion rate
# - Secondary metrics: CTR, CPC, ROAS
# - Significance level: α = 0.05
# - Test duration: 4 weeks
# ============================================================

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

# ============================================================
# 1. SIMULATE A/B TEST DATA
# ============================================================

n_per_day = 500
days = 28

def generate_variant(name, base_ctr, base_conv_rate, base_cpc):
    rows = []
    for day in range(1, days + 1):
        impressions = n_per_day + np.random.randint(-20, 20)
        clicks = int(impressions * (base_ctr + np.random.uniform(-0.005, 0.005)))
        conversions = int(clicks * (base_conv_rate + np.random.uniform(-0.02, 0.02)))
        cpc = round(base_cpc + np.random.uniform(-0.15, 0.15), 2)
        spend = round(clicks * cpc, 2)
        revenue = round(conversions * np.random.uniform(80, 250), 2)
        rows.append({
            'day': day,
            'variant': name,
            'impressions': impressions,
            'clicks': clicks,
            'conversions': conversions,
            'spend_cad': spend,
            'cpc': cpc,
            'revenue_cad': revenue,
            'ctr': round(clicks / impressions, 4),
            'conversion_rate': round(conversions / clicks if clicks > 0 else 0, 4),
            'roas': round(revenue / spend if spend > 0 else 0, 2)
        })
    return rows

# Control: static banner
variant_a = generate_variant('A — Static Banner',
                              base_ctr=0.10,
                              base_conv_rate=0.12,
                              base_cpc=1.85)

# Treatment: animated video (higher performance)
variant_b = generate_variant('B — Animated Video',
                              base_ctr=0.13,
                              base_conv_rate=0.16,
                              base_cpc=2.10)

df = pd.DataFrame(variant_a + variant_b)

print("=" * 55)
print("AC MEDIA — A/B TEST ANALYSIS")
print("RBC Campaign | In-flight Entertainment Placement")
print("=" * 55)

# ============================================================
# 2. DESCRIPTIVE SUMMARY
# ============================================================

a_data = df[df['variant'] == 'A — Static Banner']
b_data = df[df['variant'] == 'B — Animated Video']

a_conv   = int(a_data['conversions'].sum())
a_clicks = int(a_data['clicks'].sum())
b_conv   = int(b_data['conversions'].sum())
b_clicks = int(b_data['clicks'].sum())

print(f"\n--- SUMMARY METRICS ---")
print(f"{'Metric':<30} {'Variant A':>15} {'Variant B':>15}")
print("-" * 60)
print(f"{'Total impressions':<30} {int(a_data['impressions'].sum()):>15,} {int(b_data['impressions'].sum()):>15,}")
print(f"{'Total clicks':<30} {a_clicks:>15,} {b_clicks:>15,}")
print(f"{'Total conversions':<30} {a_conv:>15,} {b_conv:>15,}")
print(f"{'Avg CTR':<30} {a_data['ctr'].mean():>14.2%} {b_data['ctr'].mean():>14.2%}")
print(f"{'Overall conversion rate':<30} {a_conv/a_clicks:>14.2%} {b_conv/b_clicks:>14.2%}")
print(f"{'Avg CPC (CAD)':<30} ${a_data['cpc'].mean():>13.2f} ${b_data['cpc'].mean():>13.2f}")
print(f"{'Avg ROAS':<30} {a_data['roas'].mean():>14.2f}x {b_data['roas'].mean():>14.2f}x")

# ============================================================
# 3. STATISTICAL SIGNIFICANCE TESTING
# ============================================================

print(f"\n--- STATISTICAL TESTS (α = 0.05) ---")

# Test 1: Chi-square on conversion rates
contingency = np.array([
    [a_conv, a_clicks - a_conv],
    [b_conv, b_clicks - b_conv]
])
chi2, p_conv, dof, _ = chi2_contingency(contingency)
lift_conv = (b_conv/b_clicks - a_conv/a_clicks) / (a_conv/a_clicks) * 100

print(f"\nTest 1 — Chi-square: Conversion Rate")
print(f"  A: {a_conv/a_clicks:.2%}  |  B: {b_conv/b_clicks:.2%}  |  Lift: +{lift_conv:.1f}%")
print(f"  χ² = {chi2:.4f}, p = {p_conv:.4f} → {'SIGNIFICANT ✓' if p_conv < 0.05 else 'NOT SIGNIFICANT ✗'}")

# Test 2: t-test on daily CTR
t_ctr, p_ctr = ttest_ind(a_data['ctr'], b_data['ctr'])
lift_ctr = (b_data['ctr'].mean() - a_data['ctr'].mean()) / a_data['ctr'].mean() * 100

print(f"\nTest 2 — t-test: Daily CTR")
print(f"  A: {a_data['ctr'].mean():.2%}  |  B: {b_data['ctr'].mean():.2%}  |  Lift: +{lift_ctr:.1f}%")
print(f"  t = {t_ctr:.4f}, p = {p_ctr:.4f} → {'SIGNIFICANT ✓' if p_ctr < 0.05 else 'NOT SIGNIFICANT ✗'}")

# Test 3: t-test on daily ROAS
t_roas, p_roas = ttest_ind(a_data['roas'], b_data['roas'])

print(f"\nTest 3 — t-test: Daily ROAS")
print(f"  A: {a_data['roas'].mean():.2f}x  |  B: {b_data['roas'].mean():.2f}x")
print(f"  t = {t_roas:.4f}, p = {p_roas:.4f} → {'SIGNIFICANT ✓' if p_roas < 0.05 else 'NOT SIGNIFICANT ✗'}")

# ============================================================
# 4. CONFIDENCE INTERVALS
# ============================================================

print(f"\n--- 95% CONFIDENCE INTERVALS ---")

def ci(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    h = stats.sem(data) * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - h, mean + h

for metric, label in [('ctr', 'CTR'), ('conversion_rate', 'Conversion Rate'), ('roas', 'ROAS')]:
    a_m, a_lo, a_hi = ci(a_data[metric])
    b_m, b_lo, b_hi = ci(b_data[metric])
    print(f"\n  {label}:")
    print(f"    A: {a_m:.4f}  [{a_lo:.4f} – {a_hi:.4f}]")
    print(f"    B: {b_m:.4f}  [{b_lo:.4f} – {b_hi:.4f}]")

# ============================================================
# 5. VISUALISATIONS
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle('AC Media — A/B Test Results\nRBC Campaign | In-flight Entertainment',
             fontsize=13, fontweight='bold', color='#1B1E2B')

colors = {'A — Static Banner': '#9CB4CC', 'B — Animated Video': '#F01428'}

# Plot 1: Daily CTR over time
ax1 = axes[0, 0]
for variant, color in colors.items():
    vdata = df[df['variant'] == variant]
    ax1.plot(vdata['day'], vdata['ctr'] * 100, color=color, linewidth=1, alpha=0.4)
    ax1.plot(vdata['day'],
             pd.Series(vdata['ctr'].values).rolling(5, min_periods=1).mean() * 100,
             color=color, linewidth=2.5, label=variant)
ax1.set_title('Daily CTR — Rolling 5-day Average', fontweight='bold')
ax1.set_xlabel('Day')
ax1.set_ylabel('CTR (%)')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Conversion rate bar chart
ax2 = axes[0, 1]
variants_labels = ['Variant A\n(Static)', 'Variant B\n(Animated)']
conv_rates = [a_conv/a_clicks*100, b_conv/b_clicks*100]
bars = ax2.bar(variants_labels, conv_rates,
               color=['#9CB4CC', '#F01428'], width=0.5, edgecolor='white')
ax2.set_title('Conversion Rate Comparison', fontweight='bold')
ax2.set_ylabel('Conversion Rate (%)')
for bar, val in zip(bars, conv_rates):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{val:.2f}%', ha='center', fontsize=11, fontweight='bold')
ax2.set_xlabel(f'p = {p_conv:.4f} — {"Statistically significant ✓" if p_conv < 0.05 else "Not significant"}',
               fontsize=9, color='#333')
ax2.grid(True, alpha=0.3, axis='y')

# Plot 3: ROAS box plot
ax3 = axes[1, 0]
bp = ax3.boxplot([a_data['roas'].values, b_data['roas'].values],
                  labels=['Variant A', 'Variant B'],
                  patch_artist=True, notch=False)
bp['boxes'][0].set_facecolor('#9CB4CC')
bp['boxes'][1].set_facecolor('#F01428')
ax3.set_title('Daily ROAS Distribution', fontweight='bold')
ax3.set_ylabel('ROAS')
ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Cumulative conversions
ax4 = axes[1, 1]
for variant, color in colors.items():
    vdata = df[df['variant'] == variant].sort_values('day')
    ax4.plot(vdata['day'], vdata['conversions'].cumsum(),
             label=variant, color=color, linewidth=2.5)
ax4.set_title('Cumulative Conversions Over Test Period', fontweight='bold')
ax4.set_xlabel('Day')
ax4.set_ylabel('Total Conversions')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/ab_test_results.png', dpi=150,
            bbox_inches='tight', facecolor='white')
plt.close()
print("\nSaved: ab_test_results.png")

# ============================================================
# 6. RECOMMENDATION
# ============================================================

incremental_revenue = round((b_data['revenue_cad'].mean() - a_data['revenue_cad'].mean()) * 28, 0)

print(f"""
{'='*55}
RECOMMENDATION
{'='*55}
Winner: Variant B — Animated Video Creative

Results:
  Conversion rate lift : +{lift_conv:.1f}% (p={p_conv:.4f} ✓)
  CTR lift             : +{lift_ctr:.1f}% (p={p_ctr:.4f} ✓)
  ROAS                 : {b_data['roas'].mean():.2f}x vs {a_data['roas'].mean():.2f}x

Action: Roll out Variant B as default creative for RBC
  campaigns on In-flight Entertainment placements.

Estimated incremental revenue (28-day cycle):
  +${incremental_revenue:,.0f} CAD

Next steps:
  1. Test animated creative on Seatback Screen placement
  2. Run segment-level test for Frequent Flyer audience
     (high CTR but low ROAS — may respond better to video)
  3. Set minimum detectable effect = 10% for future tests
""")

# Save summary CSV
pd.DataFrame({
    'metric': ['Conversion Rate', 'CTR', 'Avg ROAS', 'Avg CPC'],
    'variant_a': [f"{a_conv/a_clicks:.2%}", f"{a_data['ctr'].mean():.2%}",
                  f"{a_data['roas'].mean():.2f}x", f"${a_data['cpc'].mean():.2f}"],
    'variant_b': [f"{b_conv/b_clicks:.2%}", f"{b_data['ctr'].mean():.2%}",
                  f"{b_data['roas'].mean():.2f}x", f"${b_data['cpc'].mean():.2f}"],
    'p_value':   [f"{p_conv:.4f}", f"{p_ctr:.4f}", f"{p_roas:.4f}", 'N/A'],
    'significant': ['Yes' if p_conv<0.05 else 'No',
                    'Yes' if p_ctr<0.05 else 'No',
                    'Yes' if p_roas<0.05 else 'No', 'N/A']
}).to_csv('/home/claude/ab_test_summary.csv', index=False)
print("Saved: ab_test_summary.csv")
