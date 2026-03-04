#!/usr/bin/env python3
"""
Generate 4 publication-quality figures for SexDiffKG.
Saves each as PNG (300 dpi) and PDF.
"""
import json
import os
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Global style ──────────────────────────────────────────────────────────
sns.set_style('ticks')
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 13,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

OUT = '/home/jshaik369/sexdiffkg/results/figures'
os.makedirs(OUT, exist_ok=True)

# Colour palette
FEMALE_BLUE = '#3274A1'
MALE_ORANGE = '#E1812C'
BALANCED_GRAY = '#888888'
PARITY_RED = '#CC3333'

# ══════════════════════════════════════════════════════════════════════════
# Figure 1: Cardiac Reversal Bar Chart
# ══════════════════════════════════════════════════════════════════════════
print('Generating Figure 1: Cardiac Reversal Bar Chart …')

with open('/home/jshaik369/sexdiffkg/results/analysis/cardiac_reversal_analysis.json') as f:
    cardiac = json.load(f)

pab = cardiac['per_ae_breakdown']
rows = []
for ae, stats in pab.items():
    total = stats['total']
    fh = stats['female_higher']
    pct_f = 100.0 * fh / total if total > 0 else 50.0
    rows.append({'ae': ae.title(), 'pct_female': pct_f, 'total': total,
                 'female_higher': fh, 'male_higher': stats['male_higher']})

df1 = pd.DataFrame(rows).sort_values('pct_female', ascending=True)

fig1, ax1 = plt.subplots(figsize=(10, 8))
colours = [FEMALE_BLUE if p > 50 else MALE_ORANGE for p in df1['pct_female']]
bars = ax1.barh(df1['ae'], df1['pct_female'], color=colours, edgecolor='white', linewidth=0.5)

# Parity line
ax1.axvline(50, color=PARITY_RED, linewidth=1.5, linestyle='--', zorder=3, label='Parity (50 %)')

# Annotations: count on each bar
for bar, (_, row) in zip(bars, df1.iterrows()):
    width = bar.get_width()
    label = f"n = {row['total']}"
    x_pos = width + 0.8 if width < 85 else width - 6
    ha = 'left' if width < 85 else 'right'
    color = 'black' if width < 85 else 'white'
    ax1.text(x_pos, bar.get_y() + bar.get_height() / 2, label,
             va='center', ha=ha, fontsize=9, color=color, fontweight='medium')

ax1.set_xlabel('% Signals Female-Higher')
ax1.set_title('Sex-Differential Cardiac Adverse Events', fontweight='bold', pad=12)
ax1.set_xlim(0, 100)
ax1.legend(loc='lower right', frameon=True, framealpha=0.9)
sns.despine(left=True)
ax1.tick_params(axis='y', length=0)
fig1.tight_layout()

fig1.savefig(os.path.join(OUT, 'fig1_cardiac_reversal.png'))
fig1.savefig(os.path.join(OUT, 'fig1_cardiac_reversal.pdf'))
plt.close(fig1)
print('  ✓ fig1_cardiac_reversal saved')


# ══════════════════════════════════════════════════════════════════════════
# Figure 2: Opioid Heatmap
# ══════════════════════════════════════════════════════════════════════════
print('Generating Figure 2: Opioid Heatmap …')

with open('/home/jshaik369/sexdiffkg/results/analysis/opioid_sex_diff_analysis.json') as f:
    opioid = json.load(f)

pd_data = opioid['per_drug']
rows2 = []
for drug, stats in pd_data.items():
    rows2.append({
        'Drug': drug.title(),
        'Total Signals': stats['total'],
        '% Female-Higher': stats['pct_female'],
        'Mean log(ROR ratio)': stats['mean_log_ratio'],
    })

df2 = pd.DataFrame(rows2).sort_values('% Female-Higher', ascending=False)
df2 = df2.set_index('Drug')

# Normalize columns independently for heatmap display
df2_plot = df2.copy()

fig2, ax2 = plt.subplots(figsize=(8, 10))

# We need separate colour scales — use annotated heatmap approach
# Standardize each column for colour mapping, but annotate with real values
from matplotlib.colors import TwoSlopeNorm

# Build a matrix where each column is separately normalized
vals = df2_plot.values.astype(float)
# For display, we manually create the heatmap cell-by-cell
# Simpler: use 3 adjacent heatmaps

# Actually, let's use seaborn heatmap with z-scored values for colour,
# and annotate with raw values.
z = vals.copy()
for j in range(z.shape[1]):
    col = z[:, j]
    mu, sigma = col.mean(), col.std()
    if sigma > 0:
        z[:, j] = (col - mu) / sigma
    else:
        z[:, j] = 0

# For %Female, use diverging centred at 50
# Custom approach: plot raw %Female for the colour of col 1 with TwoSlopeNorm
# For simplicity, use z-scores with RdBu_r — female-high is blue, male-high is red.

# Create annotation strings
annot = np.empty_like(vals, dtype=object)
for i in range(vals.shape[0]):
    annot[i, 0] = f"{int(vals[i, 0])}"
    annot[i, 1] = f"{vals[i, 1]:.1f}%"
    annot[i, 2] = f"{vals[i, 2]:.2f}"

# Use %Female column for colouring entire heatmap (thematic)
# Actually use z-scores for balanced colour mapping
norm = TwoSlopeNorm(vmin=-2.5, vcenter=0, vmax=2.5)

hm = sns.heatmap(z, annot=annot, fmt='', cmap='RdBu_r', norm=norm,
                  xticklabels=df2_plot.columns, yticklabels=df2_plot.index,
                  linewidths=0.8, linecolor='white', cbar_kws={'label': 'Z-score'},
                  ax=ax2)
ax2.set_title('Opioid Sex-Differential Safety Profiles', fontweight='bold', pad=12)
ax2.set_ylabel('')
ax2.set_xlabel('')
plt.setp(ax2.get_xticklabels(), rotation=20, ha='right')
fig2.tight_layout()

fig2.savefig(os.path.join(OUT, 'fig2_opioid_heatmap.png'))
fig2.savefig(os.path.join(OUT, 'fig2_opioid_heatmap.pdf'))
plt.close(fig2)
print('  ✓ fig2_opioid_heatmap saved')


# ══════════════════════════════════════════════════════════════════════════
# Figure 3: ATC Level 1 Forest Plot
# ══════════════════════════════════════════════════════════════════════════
print('Generating Figure 3: ATC Level 1 Forest Plot …')

with open('/home/jshaik369/sexdiffkg/results/analysis/atc_soc_analysis.json') as f:
    atc_data = json.load(f)

atc_l1 = atc_data['atc_level1']
rows3 = []
for code, stats in atc_l1.items():
    rows3.append({
        'code': code,
        'name': stats['name'],
        'total': stats['total'],
        'pct_female': stats['pct_female'],
        'n_drugs': stats['n_drugs'],
        'mean_logR': stats['mean_logR'],
    })

df3 = pd.DataFrame(rows3).sort_values('pct_female', ascending=True)

# Assign colours
def forest_color(pct):
    if pct > 55:
        return FEMALE_BLUE
    elif pct < 45:
        return MALE_ORANGE
    else:
        return BALANCED_GRAY

df3['color'] = df3['pct_female'].apply(forest_color)

# Label = "Code – Name"
df3['label'] = df3.apply(lambda r: f"{r['code']} – {r['name']}", axis=1)

# Size scaling: proportional to sqrt(total) for area perception
size_scale = 15
df3['dot_size'] = np.sqrt(df3['total']) * size_scale

fig3, ax3 = plt.subplots(figsize=(10, 6))

for _, row in df3.iterrows():
    ax3.scatter(row['pct_female'], row['label'], s=row['dot_size'],
                color=row['color'], edgecolors='white', linewidths=0.5, zorder=3)
    # Horizontal error-like line from 50 to the point
    ax3.plot([50, row['pct_female']], [row['label'], row['label']],
             color=row['color'], linewidth=1.2, alpha=0.6, zorder=2)

ax3.axvline(50, color=PARITY_RED, linewidth=1.5, linestyle='--', zorder=1, label='Parity (50 %)')

# Annotations: n_drugs and total signals
for _, row in df3.iterrows():
    offset = 0.8 if row['pct_female'] >= 50 else -0.8
    ha = 'left' if row['pct_female'] >= 50 else 'right'
    ax3.annotate(f"{row['pct_female']:.1f}%  ({row['n_drugs']} drugs)",
                 xy=(row['pct_female'], row['label']),
                 xytext=(row['pct_female'] + offset * 3, row['label']),
                 fontsize=8.5, color=row['color'], fontweight='medium',
                 va='center', ha=ha)

ax3.set_xlabel('% Signals Female-Higher')
ax3.set_title('Sex Bias by Drug Therapeutic Class (ATC Level 1)', fontweight='bold', pad=12)
ax3.set_xlim(30, 72)
ax3.legend(loc='upper left', frameon=True, framealpha=0.9)
sns.despine(left=True)
ax3.tick_params(axis='y', length=0)
ax3.grid(axis='x', alpha=0.3, linewidth=0.5)
fig3.tight_layout()

fig3.savefig(os.path.join(OUT, 'fig3_atc_forest.png'))
fig3.savefig(os.path.join(OUT, 'fig3_atc_forest.pdf'))
plt.close(fig3)
print('  ✓ fig3_atc_forest saved')


# ══════════════════════════════════════════════════════════════════════════
# Figure 4: Global Volcano Plot
# ══════════════════════════════════════════════════════════════════════════
print('Generating Figure 4: Global Volcano Plot …')

df4 = pd.read_parquet('/home/jshaik369/sexdiffkg/results/signals_v4/sex_differential_v4.parquet')

df4['report_volume'] = np.log10(df4['n_female'] + df4['n_male'])
df4['abs_lr'] = df4['log_ratio'].abs()

fig4, ax4 = plt.subplots(figsize=(12, 8))

# Scatter — female_higher vs male_higher
mask_f = df4['direction'] == 'female_higher'
mask_m = df4['direction'] == 'male_higher'

ax4.scatter(df4.loc[mask_f, 'log_ratio'], df4.loc[mask_f, 'report_volume'],
            c=FEMALE_BLUE, alpha=0.08, s=8, linewidths=0, rasterized=True,
            label=f'Female-higher (n={mask_f.sum():,})')
ax4.scatter(df4.loc[mask_m, 'log_ratio'], df4.loc[mask_m, 'report_volume'],
            c=MALE_ORANGE, alpha=0.08, s=8, linewidths=0, rasterized=True,
            label=f'Male-higher (n={mask_m.sum():,})')

# Highlight top 10 signals by absolute log_ratio (with sufficient volume)
top10 = df4.nlargest(10, 'abs_lr')
for _, row in top10.iterrows():
    colour = FEMALE_BLUE if row['direction'] == 'female_higher' else MALE_ORANGE
    ax4.scatter(row['log_ratio'], row['report_volume'],
                c=colour, s=50, edgecolors='black', linewidths=0.8, zorder=5)
    label_text = f"{row['drug_name'].title()}\n{row['adverse_event'].title()}"
    # Shorten long labels
    if len(label_text) > 45:
        parts = label_text.split('\n')
        parts[1] = parts[1][:25] + '…'
        label_text = '\n'.join(parts)
    ax4.annotate(label_text,
                 xy=(row['log_ratio'], row['report_volume']),
                 xytext=(8, 6), textcoords='offset points',
                 fontsize=7, color=colour, fontweight='bold',
                 arrowprops=dict(arrowstyle='-', color=colour, lw=0.5),
                 zorder=6)

# Reference lines
ax4.axvline(0, color='gray', linewidth=0.8, linestyle='-', alpha=0.4)

ax4.set_xlabel('log(ROR$_{female}$ / ROR$_{male}$)  —  Effect Size')
ax4.set_ylabel('log$_{10}$(Total Reports)')
ax4.set_title(f'Sex-Differential Drug Safety Signal Landscape ({len(df4):,} signals)',
              fontweight='bold', pad=12)

# Custom legend with opaque markers
legend = ax4.legend(loc='upper left', frameon=True, framealpha=0.95,
                     markerscale=3, scatterpoints=1)
for lh in legend.legend_handles:
    lh.set_alpha(1.0)

sns.despine()
ax4.grid(alpha=0.2, linewidth=0.5)
fig4.tight_layout()

fig4.savefig(os.path.join(OUT, 'fig4_volcano.png'))
fig4.savefig(os.path.join(OUT, 'fig4_volcano.pdf'))
plt.close(fig4)
print('  ✓ fig4_volcano saved')


# ══════════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('All figures saved to:', OUT)
print('=' * 60)
for fname in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, fname)
    if os.path.isfile(fpath) and fname.startswith('fig'):
        size_kb = os.path.getsize(fpath) / 1024
        if size_kb > 1024:
            print(f'  {fname:40s}  {size_kb/1024:.1f} MB')
        else:
            print(f'  {fname:40s}  {size_kb:.0f} KB')
print('=' * 60)
