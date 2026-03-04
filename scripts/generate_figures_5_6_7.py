#!/usr/bin/env python3
"""
Generate publication-quality Figures 5, 6, 7 for SexDiffKG manuscript.
All figures use seaborn 'ticks' style, fontsize 12, tight_layout(), 300 dpi.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np
import json
import os
import pandas as pd
from collections import Counter

# Global settings
sns.set_style('ticks')
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 300,
})

OUTPUT_DIR = '/home/jshaik369/sexdiffkg/results/figures/'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# FIGURE 5: Psychotropic Grouped Bar Chart
# ============================================================
print("=" * 60)
print("Generating Figure 5: Psychotropic Drug Class Sex Differences")
print("=" * 60)

with open('/home/jshaik369/sexdiffkg/results/analysis/psychotropic_sex_diff.json') as f:
    psych_data = json.load(f)

# Define classes in display order (exclude All_Antidepressants as it's a superset)
class_keys = ['Antipsychotics', 'SSRIs', 'SNRIs', 'TCAs', 'Other_AD', 'Anxiolytics', 'Mood_Stabilizers']
class_labels = ['Antipsychotics', 'SSRIs', 'SNRIs', 'TCAs', 'Other AD', 'Anxiolytics', 'Mood\nStabilizers']

pct_female = []
pct_male = []
totals = []

for k in class_keys:
    d = psych_data[k]
    total = d['total']
    f_pct = d['pct_female']
    m_pct = 100.0 - f_pct
    pct_female.append(f_pct)
    pct_male.append(m_pct)
    totals.append(total)

x = np.arange(len(class_labels))
width = 0.35

fig5, ax5 = plt.subplots(figsize=(12, 6))

bars_f = ax5.bar(x - width/2, pct_female, width, label='% Female-higher signals',
                  color='#4878CF', edgecolor='white', linewidth=0.5, zorder=3)
bars_m = ax5.bar(x + width/2, pct_male, width, label='% Male-higher signals',
                  color='#EE854A', edgecolor='white', linewidth=0.5, zorder=3)

# Horizontal line at 50%
ax5.axhline(y=50, color='#555555', linestyle='--', linewidth=1, alpha=0.7, zorder=2)
ax5.text(len(class_labels) - 0.5, 50.8, '50%', color='#555555', fontsize=10, ha='right', va='bottom')

# Annotate total signal count above each group
for i, (total, yf, ym) in enumerate(zip(totals, pct_female, pct_male)):
    max_y = max(yf, ym)
    ax5.text(i, max_y + 2.0, f'n={total:,}', ha='center', va='bottom',
             fontsize=9.5, fontweight='bold', color='#333333')

ax5.set_xlabel('Psychotropic Drug Class', fontweight='bold')
ax5.set_ylabel('Proportion of Drug-AE Signals (%)', fontweight='bold')
ax5.set_title('Sex-Differential AE Profiles by Psychotropic Drug Class', fontweight='bold', pad=15)
ax5.set_xticks(x)
ax5.set_xticklabels(class_labels)
ax5.set_ylim(0, 82)
ax5.legend(loc='upper right', frameon=True, framealpha=0.9, edgecolor='#cccccc')
ax5.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax5.yaxis.set_minor_locator(ticker.MultipleLocator(5))
ax5.grid(axis='y', alpha=0.3, zorder=0)
sns.despine(ax=ax5)
fig5.tight_layout()

fig5.savefig(os.path.join(OUTPUT_DIR, 'fig5_psychotropic.png'), dpi=300, bbox_inches='tight')
fig5.savefig(os.path.join(OUTPUT_DIR, 'fig5_psychotropic.pdf'), dpi=300, bbox_inches='tight')
plt.close(fig5)
print("  Saved fig5_psychotropic.png and .pdf")

# ============================================================
# FIGURE 6: Temporal Trend Line Plot
# ============================================================
print()
print("=" * 60)
print("Generating Figure 6: Temporal Evolution of Sex-Differential Signals")
print("=" * 60)

with open('/home/jshaik369/sexdiffkg/results/analysis/temporal_trend_analysis.json') as f:
    temp_data = json.load(f)

# Extract era-level data from temporal_aggregate_trends
agg_trends = temp_data['temporal_aggregate_trends']
era_labels_raw = [t['era'] for t in agg_trends]
# Clean up era labels for display
era_display = []
era_years = []
for e in era_labels_raw:
    # e.g. 'Era1_2013-2015'
    parts = e.split('_', 1)
    years = parts[1] if len(parts) > 1 else e
    era_display.append(years)
    era_years.append(years)

pct_fb = [t['pct_female_biased'] for t in agg_trends]
n_pairs = [t['n_pairs'] for t in agg_trends]
median_log2 = [t['median_log2_ror_ratio'] for t in agg_trends]

# Extract quarterly F/M ratio
quarterly = temp_data['quarterly_reporting_trends']
q_labels = [q['quarter'] for q in quarterly]
q_fm_ratio = [q['fm_ratio'] for q in quarterly]
q_pct_female = [q['pct_female'] for q in quarterly]

fig6, ax6_left = plt.subplots(figsize=(10, 6))

# Primary axis: % female-biased per era
color_era = '#2C73D2'
line1 = ax6_left.plot(era_display, pct_fb, 's-', color=color_era, markersize=10,
                       linewidth=2.5, markeredgecolor='white', markeredgewidth=1.5,
                       label='% Female-biased signals (era)', zorder=5)

# Annotate each era point with value and n_pairs
for i, (pf, n) in enumerate(zip(pct_fb, n_pairs)):
    ax6_left.annotate(f'{pf:.1f}%\n({n//1000}k pairs)',
                       xy=(era_display[i], pf),
                       xytext=(0, 15), textcoords='offset points',
                       ha='center', fontsize=9, color=color_era, fontweight='bold')

# Horizontal reference line at 50%
ax6_left.axhline(y=50, color='#555555', linestyle='--', linewidth=1, alpha=0.7, zorder=2)
ax6_left.text(era_display[0], 50.3, 'Equal (50%)', color='#555555', fontsize=9, va='bottom')

ax6_left.set_xlabel('Time Period', fontweight='bold')
ax6_left.set_ylabel('% Female-Biased Drug-AE Pairs', fontweight='bold', color=color_era)
ax6_left.tick_params(axis='y', labelcolor=color_era)
ax6_left.set_ylim(44, 56)
ax6_left.yaxis.set_major_locator(ticker.MultipleLocator(2))

# COVID era annotation (Era4: 2020-2022)
covid_idx = era_display.index('2020-2022')
ax6_left.annotate('COVID-19\npandemic era',
                   xy=(era_display[covid_idx], pct_fb[covid_idx]),
                   xytext=(-60, -40), textcoords='offset points',
                   fontsize=10, color='#D32F2F', fontweight='bold',
                   arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5),
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFEBEE', edgecolor='#D32F2F', alpha=0.9))

# Secondary y-axis: quarterly F/M ratio
ax6_right = ax6_left.twinx()
color_q = '#FF6D00'

# Map quarters to approximate x positions for overlay
# Create numeric positions for quarterly data
q_numeric = np.linspace(0, len(era_display) - 1, len(q_labels))
ax6_right.plot(q_numeric, q_fm_ratio, '-', color=color_q, alpha=0.5, linewidth=1.2, zorder=3)
# Smooth with rolling average
if len(q_fm_ratio) > 4:
    window = 4
    smoothed = pd.Series(q_fm_ratio).rolling(window, center=True).mean()
    ax6_right.plot(q_numeric, smoothed, '-', color=color_q, linewidth=2.2, alpha=0.85,
                    label='F/M reporting ratio (quarterly, smoothed)', zorder=4)

ax6_right.set_ylabel('Female/Male Reporting Ratio', fontweight='bold', color=color_q)
ax6_right.tick_params(axis='y', labelcolor=color_q)
ax6_right.set_ylim(1.3, 1.8)

# Use era_display positions on x-axis but map quarterly to those
ax6_left.set_xticks(range(len(era_display)))
ax6_left.set_xticklabels(era_display)

ax6_left.set_title('Temporal Evolution of Sex-Differential Drug Safety Signals (2013\u20132025)',
                     fontweight='bold', pad=15)

# Combined legend
lines_left = line1
lines_right = [Line2D([0], [0], color=color_q, linewidth=2.2, alpha=0.85)]
labels_left = ['% Female-biased signals (per era)']
labels_right = ['F/M reporting ratio (quarterly, smoothed)']
ax6_left.legend(lines_left + lines_right, labels_left + labels_right,
                 loc='lower left', frameon=True, framealpha=0.9, edgecolor='#cccccc')

ax6_left.grid(axis='y', alpha=0.3, zorder=0)
sns.despine(ax=ax6_left, right=False)
sns.despine(ax=ax6_right, left=True)
fig6.tight_layout()

fig6.savefig(os.path.join(OUTPUT_DIR, 'fig6_temporal.png'), dpi=300, bbox_inches='tight')
fig6.savefig(os.path.join(OUTPUT_DIR, 'fig6_temporal.pdf'), dpi=300, bbox_inches='tight')
plt.close(fig6)
print("  Saved fig6_temporal.png and .pdf")

# ============================================================
# FIGURE 7: Network Degree Distribution
# ============================================================
print()
print("=" * 60)
print("Generating Figure 7: SexDiffKG Degree Distribution")
print("=" * 60)

# Load edges
print("  Loading edges.tsv...")
edges_df = pd.read_csv('/home/jshaik369/sexdiffkg/data/kg_v4/edges.tsv', sep='\t')
print(f"  Loaded {len(edges_df):,} edges")

# Load nodes for category info
print("  Loading nodes.tsv...")
nodes_df = pd.read_csv('/home/jshaik369/sexdiffkg/data/kg_v4/nodes.tsv', sep='\t')
print(f"  Loaded {len(nodes_df):,} nodes")

# Compute degree for each node (both subject and object count)
degree_counter = Counter()
degree_counter.update(edges_df['subject'])
degree_counter.update(edges_df['object'])

# Create node-category mapping
node_cat = dict(zip(nodes_df['id'], nodes_df['category']))

# Build degree DataFrame
degree_data = []
for node_id, deg in degree_counter.items():
    cat = node_cat.get(node_id, 'Unknown')
    degree_data.append({'node': node_id, 'degree': deg, 'category': cat})

deg_df = pd.DataFrame(degree_data)
print(f"  Computed degrees for {len(deg_df):,} unique nodes")
print(f"  Degree range: {deg_df['degree'].min()} - {deg_df['degree'].max()}")
print(f"  Mean degree: {deg_df['degree'].mean():.1f}, Median: {deg_df['degree'].median():.0f}")

# Category color mapping
cat_colors = {
    'Drug': '#E53935',
    'AdverseEvent': '#1E88E5',
    'Gene': '#43A047',
    'Protein': '#8E24AA',
    'Pathway': '#FB8C00',
    'Tissue': '#00ACC1',
    'Unknown': '#757575'
}

# Order categories by count for consistent legend
cat_order = ['Drug', 'AdverseEvent', 'Gene', 'Protein', 'Pathway', 'Tissue']

fig7, ax7_main = plt.subplots(figsize=(10, 8))

# Compute complementary CDF (CCDF) per category
for cat in cat_order:
    subset = deg_df[deg_df['category'] == cat]['degree'].values
    if len(subset) == 0:
        continue
    sorted_deg = np.sort(subset)
    ccdf = 1.0 - np.arange(1, len(sorted_deg) + 1) / len(sorted_deg)
    # Avoid log(0) — remove last point where ccdf=0
    mask = ccdf > 0
    ax7_main.loglog(sorted_deg[mask], ccdf[mask], '.', color=cat_colors[cat],
                     alpha=0.4, markersize=3, rasterized=True)

# Overall CCDF (bold line)
all_degrees = deg_df['degree'].values
sorted_all = np.sort(all_degrees)
ccdf_all = 1.0 - np.arange(1, len(sorted_all) + 1) / len(sorted_all)
mask_all = ccdf_all > 0
ax7_main.loglog(sorted_all[mask_all], ccdf_all[mask_all], '-', color='#333333',
                 linewidth=1.5, alpha=0.7, label='All nodes', zorder=5)

# Power-law fit (linear regression in log-log space)
# Use middle portion to avoid edge effects
log_deg = np.log10(sorted_all[mask_all].astype(float))
log_ccdf = np.log10(ccdf_all[mask_all])
# Fit on the range where degree > 5 and ccdf > 0.001
fit_mask = (sorted_all[mask_all] >= 5) & (ccdf_all[mask_all] >= 0.001)
if fit_mask.sum() > 10:
    coeffs = np.polyfit(log_deg[fit_mask], log_ccdf[fit_mask], 1)
    alpha = -coeffs[0]
    fit_x = np.logspace(np.log10(5), np.log10(sorted_all.max()), 100)
    fit_y = 10 ** (coeffs[0] * np.log10(fit_x) + coeffs[1])
    ax7_main.loglog(fit_x, fit_y, '--', color='#D32F2F', linewidth=2, alpha=0.8,
                     label=f'Power-law fit (\u03b1 = {alpha:.2f})', zorder=6)

# Legend for categories
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor=cat_colors[cat],
                           markersize=8, label=cat) for cat in cat_order]
legend_elements.append(Line2D([0], [0], color='#333333', linewidth=1.5, alpha=0.7, label='All nodes (CCDF)'))
legend_elements.append(Line2D([0], [0], color='#D32F2F', linewidth=2, linestyle='--', alpha=0.8,
                                label=f'Power-law fit (\u03b1 = {alpha:.2f})'))

ax7_main.legend(handles=legend_elements, loc='lower left', frameon=True,
                 framealpha=0.95, edgecolor='#cccccc', fontsize=10)

ax7_main.set_xlabel('Node Degree (k)', fontweight='bold')
ax7_main.set_ylabel('P(K \u2265 k)  [Complementary CDF]', fontweight='bold')
ax7_main.set_title('SexDiffKG Degree Distribution', fontweight='bold', pad=15)
ax7_main.grid(True, alpha=0.2, which='both')
sns.despine(ax=ax7_main)

# Inset: bar chart of mean degree by node type
ax_inset = fig7.add_axes([0.58, 0.55, 0.35, 0.32])  # [left, bottom, width, height]

mean_degrees = []
for cat in cat_order:
    subset = deg_df[deg_df['category'] == cat]['degree']
    mean_degrees.append(subset.mean() if len(subset) > 0 else 0)

bars_inset = ax_inset.barh(range(len(cat_order)), mean_degrees,
                            color=[cat_colors[c] for c in cat_order],
                            edgecolor='white', linewidth=0.5)

# Annotate bars
for i, (md, cat) in enumerate(zip(mean_degrees, cat_order)):
    ax_inset.text(md + 0.5, i, f'{md:.1f}', va='center', fontsize=8.5, fontweight='bold')

ax_inset.set_yticks(range(len(cat_order)))
ax_inset.set_yticklabels(cat_order, fontsize=9)
ax_inset.set_xlabel('Mean Degree', fontsize=10, fontweight='bold')
ax_inset.set_title('Mean Degree by Node Type', fontsize=10, fontweight='bold')
ax_inset.invert_yaxis()
# Add some padding on the right for labels
max_md = max(mean_degrees)
ax_inset.set_xlim(0, max_md * 1.25)
ax_inset.grid(axis='x', alpha=0.3)
sns.despine(ax=ax_inset)

fig7.tight_layout()

fig7.savefig(os.path.join(OUTPUT_DIR, 'fig7_network.png'), dpi=300, bbox_inches='tight')
fig7.savefig(os.path.join(OUTPUT_DIR, 'fig7_network.pdf'), dpi=300, bbox_inches='tight')
plt.close(fig7)
print("  Saved fig7_network.png and .pdf")

# ============================================================
# Summary
# ============================================================
print()
print("=" * 60)
print("ALL FIGURES GENERATED SUCCESSFULLY")
print("=" * 60)
print()

for fname in ['fig5_psychotropic.png', 'fig5_psychotropic.pdf',
              'fig6_temporal.png', 'fig6_temporal.pdf',
              'fig7_network.png', 'fig7_network.pdf']:
    fpath = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(fpath):
        size_kb = os.path.getsize(fpath) / 1024
        if size_kb > 1024:
            print(f"  {fname}: {size_kb/1024:.1f} MB")
        else:
            print(f"  {fname}: {size_kb:.0f} KB")
    else:
        print(f"  {fname}: NOT FOUND")
