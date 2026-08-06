from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W31 America Trade Balances.csv')

assert df['Country'].notna().all()
assert df[['Goods and services ($B)', 'Goods ($B)', 'Services ($B)']].notna().all().all()

df = df.rename(columns={'Goods and services ($B)': 'Total', 'Goods ($B)': 'Goods', 'Services ($B)': 'Services'})
df = df.sort_values('Total').reset_index(drop=True)
df['y'] = np.arange(len(df))

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
GOODS, SERVICES, TOTAL = '#24466B', '#D96C2F', '#111111'
FONT = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(12, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for _, row in df.iterrows():
    ax.plot([0, row['Goods']], [row['y'], row['y']], color=GOODS, linewidth=8, solid_capstyle='round', zorder=2)
    ax.plot([row['Goods'], row['Total']], [row['y'], row['y']], color=SERVICES, linewidth=8, solid_capstyle='round', zorder=3)
    ax.scatter(row['Total'], row['y'], s=78, color=BG, edgecolor=TOTAL, linewidth=1.8, zorder=4)

for _, row in df.iterrows():
    ax.annotate(f"{row['Total']:+.1f}", xy=(row['Total'], row['y']), xytext=(0, 5), textcoords='offset points', fontsize=9, fontfamily=FONT, fontweight='bold', color=TEXT, ha='center', va='bottom')

ax.axvline(0, color='#B8B8B8', linewidth=1.0, zorder=1)
ax.set_xlim(-200, 55)
ax.set_ylim(-0.8, len(df) - 0.2)
ax.set_yticks(df['y'])
ax.set_yticklabels(df['Country'], fontsize=10.5, fontfamily=FONT, color=MUTED)
ax.set_xticks([-200, -150, -100, -50, 0, 50])
ax.set_xticklabels(['−$200B', '−$150B', '−$100B', '−$50B', '$0', '+$50B'], fontsize=10, fontfamily=FONT, color=MUTED)
ax.grid(True, axis='x', color=GRID, linewidth=0.7, alpha=0.8, zorder=0)

for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_visible(False)

ax.tick_params(left=False, bottom=False, colors=MUTED)
ax.text(0.02, -0.075, '←  U.S. DEFICIT', transform=ax.transAxes, fontsize=11.5, fontfamily=FONT, fontweight='bold', color=MUTED, ha='left')
ax.text(0.98, -0.075, 'U.S. SURPLUS  →', transform=ax.transAxes, fontsize=11.5, fontfamily=FONT, fontweight='bold', color=MUTED, ha='right')

fig.text(0.075, 0.955, 'THE TRADE BALANCE HIDES TWO DIFFERENT STORIES', fontsize=24, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.075, 0.914, 'THE FINAL TOTAL CAN MASK LARGE, OFFSETTING GOODS AND SERVICES BALANCES.', fontsize=12, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.075, 0.878, 'U.S. GOODS AND SERVICES TRADE BALANCES WITH 15 PARTNERS, BILLIONS OF DOLLARS', fontsize=12, fontfamily=FONT, fontweight='bold', color=GOODS, ha='left')

fig.text(0.075, 0.842, '━  GOODS BALANCE', fontsize=10.5, fontfamily=FONT, fontweight='bold', color=GOODS, ha='left')
fig.text(0.265, 0.842, '━  SERVICES CONTRIBUTION', fontsize=10.5, fontfamily=FONT, fontweight='bold', color=SERVICES, ha='left')
fig.text(0.525, 0.842, '○  FINAL BALANCE', fontsize=10.5, fontfamily=FONT, fontweight='bold', color=TOTAL, ha='left')

fig.text(0.04, 0.025, 'Source: MakeoverMonday 2026, Week 31 — America Trade Balances  |  Final balance shown at each endpoint  |  Rowan Olson · #MakeoverMonday', fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

fig.subplots_adjust(left=0.19, right=0.95, top=0.79, bottom=0.13)
plt.savefig(HERE / 'tradebalances.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()