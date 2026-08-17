from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W33 Sports Betting.csv')

METRIC = 'Redirected investing funds to sports betting at least once in the past year'
ORDER = ['Boomers','Gen X','Millennials','Gen Z']

data = df[(df['Metric'] == METRIC) & (df['Is Overall'] == 'No')].set_index('Generation').reindex(ORDER).reset_index()

assert data['Percent'].notna().all()
assert list(data['Generation']) == ORDER

data['x'] = np.arange(len(data))

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
BLUE, ORANGE = '#24466B', '#D96C2F'
FONT = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for i, row in data.iterrows():
    x0, x1 = row['x'] - 0.34, row['x'] + 0.34
    ax.plot([x0, x1], [row['Percent'], row['Percent']], color=BLUE, linewidth=9, solid_capstyle='round', zorder=3)
    ax.scatter(row['x'], row['Percent'], s=145, color=ORANGE, edgecolor='white', linewidth=1.2, zorder=4)
    if i < len(data) - 1:
        next_row = data.iloc[i + 1]
        ax.plot([x1, x1], [row['Percent'], next_row['Percent']], color=GRID, linewidth=1.4, zorder=1)
        ax.plot([x1, next_row['x'] - 0.34], [next_row['Percent'], next_row['Percent']], color=GRID, linewidth=1.4, zorder=1)

for _, row in data.iterrows():
    ax.annotate(f"{row['Percent']}%", xy=(row['x'], row['Percent']), xytext=(0, 13), textcoords='offset points', fontsize=17, fontfamily=FONT, fontweight='bold', color=TEXT, 
    ha='center', va='bottom')

ax.set_xlim(-0.55, 3.55)
ax.set_ylim(0, 60)
ax.set_xticks(data['x'])
ax.set_xticklabels([f"{r['Generation']}\n{r['Birth Years']}" for _, r in data.iterrows()], fontsize=11, fontfamily=FONT, fontweight='bold', color=TEXT)
ax.set_yticks([0,10,20,30,40,50,60])
ax.set_yticklabels(['0%','10%','20%','30%','40%','50%','60%'], fontsize=9.5, fontfamily=FONT, color=MUTED)
ax.grid(True, axis='y', color=GRID, linewidth=0.7, alpha=0.8, zorder=0)

for spine in ['top','right','left','bottom']:
    ax.spines[spine].set_visible(False)

ax.tick_params(left=False, bottom=False, colors=MUTED)

fig.text(0.065, 0.955, 'BETTING WITH INVESTMENT MONEY IS A GEN Z TACTIC', fontsize=23, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.065, 0.914, 'GEN Z IS 13× AS LIKELY AS BOOMERS TO HAVE MOVED INVESTING FUNDS TO SPORTS BETTING', fontsize=12.2, fontfamily=FONT, fontweight='bold', color=TEXT, 
    ha='left')
fig.text(0.065, 0.878, 'SHARE WHO REDIRECTED INVESTING FUNDS TO SPORTS BETTING IN THE PAST YEAR', fontsize=12, fontfamily=FONT, fontweight='bold', color=BLUE, ha='left')
fig.text(0.04, 0.025, 'Source: Betterment 2026 Retail Investor Survey via MakeoverMonday  |  n=250 per generation  |  Rowan Olson · #MakeoverMonday', fontsize=8.5, 
    fontfamily=FONT, color=MUTED, ha='left')

fig.subplots_adjust(left=0.09, right=0.96, top=0.82, bottom=0.14)
plt.savefig(HERE / 'sportsbetting.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()