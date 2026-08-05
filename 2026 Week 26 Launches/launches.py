import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('MM2026 W26 Launches.csv', encoding='utf-8-sig')

df['Launch Date'] = pd.to_datetime(df['Launch Date'], errors='coerce')
df = df[(df['Launch Date'].dt.year >= 2016) & (df['Launch Date'].dt.year <= 2026)].copy()

def nation(c):
    if c == 'United States':
        return 'United States'
    if c == 'China':
        return 'China'
    if c == 'Russia/Soviet Union':
        return 'Russia'
    return 'Rest of World'

df['nation'] = df['Country'].apply(nation)
df['quarter'] = df['Launch Date'].dt.to_period('Q').dt.to_timestamp()

counts = df.groupby(['quarter', 'nation']).size().unstack(fill_value=0)

cat_order = ['United States', 'China', 'Russia', 'Rest of World']
counts = counts.reindex(columns=cat_order, fill_value=0)

shares = counts.div(counts.sum(axis=1), axis=0) * 100
shares = shares.rolling(window=3, min_periods=1, center=True).mean()
shares = shares.div(shares.sum(axis=1), axis=0) * 100

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
COLORS = {
    'United States': '#1B3A5C',
    'China': '#C0392B',
    'Russia': '#B8973D',
    'Rest of World': '#D5D5D5',
}
FONT = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.stackplot(
    shares.index, [shares[c] for c in cat_order],
    colors=[COLORS[c] for c in cat_order],
    labels=cat_order,
    edgecolor=BG, linewidth=0.4
)

ax.set_xlim(shares.index.min(), shares.index.max())
ax.set_ylim(0, 100)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'], fontsize=10, fontfamily=FONT, color=MUTED)

ax.grid(True, axis='y', color=GRID, linewidth=0.7, alpha=0.8, zorder=0)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#CCCCCC')
ax.tick_params(left=False, bottom=True, labelsize=10, colors=MUTED)

import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.tick_params(axis='x', labelsize=10.5, colors=TEXT)

label_x = shares.index.max()
for c in cat_order:
    y = shares.loc[shares.index.max(), c]
    cum = sum(shares.loc[shares.index.max(), cat_order[:cat_order.index(c)]])
    ax.text(label_x, cum + y / 2, f'  {c}', va='center', ha='left',
             fontsize=10.5, fontfamily=FONT, fontweight='bold', color=TEXT)

fig.text(0.06, 0.95, 'THE MODERN SPACE RACE ISN\'T A ZERO-SUM GAME', fontsize=24, fontfamily=FONT,
          fontweight='bold', color=TEXT, ha='left')
fig.text(0.06, 0.915, 'CHINA EXPANDED ITS REACH. SO HAS THE UNITED STATES', fontsize=12,
          fontfamily=FONT, fontweight='bold', color='black', ha='left')
fig.text(0.06, 0.885, 'SHARE OF GLOBAL ORBITAL LAUNCHES BY NATION, 2016\u20132026', fontsize=12,
          fontfamily=FONT, fontweight='bold', color='#1B3A5C', ha='left')
fig.text(0.03, 0.015, 'Source: Space Launch Data Explorer | Global Launch Trends  |  Rowan Olson \u00b7 #MakeoverMonday', fontsize=8.5,
          fontfamily=FONT, color=MUTED, ha='left')

plt.tight_layout(rect=[0.04, 0.03, 0.86, 0.88])
plt.savefig('launches.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()