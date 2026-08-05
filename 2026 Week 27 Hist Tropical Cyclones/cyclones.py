import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy import stats

df = pd.read_csv('MM2026 W27 Hist Tropical Cyclones.csv', encoding='utf-8-sig')
df['USA_WIND (KTS)'] = pd.to_numeric(df['USA_WIND (KTS)'], errors='coerce')

storm = df.groupby('SID').agg(
    year=('SEASON (YEAR)', 'first'),
    name=('NAME', 'first'),
    basin=('BASIN', 'first'),
    max_wind=('USA_WIND (KTS)', 'max'),
).reset_index().dropna(subset=['max_wind'])

# 1987 cutoff: WP aircraft recon ended in 1987, and multiple reanalyses (Kruk/Knapp 2010,
# Song et al. 2010, Nakazawa & Hoshino 2009) document a step-function discontinuity in
# best-track intensity right at that boundary -- pre-1987 super typhoon winds are widely
# regarded as inflated relative to post-1987 satellite-Dvorak estimates. Using the full
# record would make the "ceiling" look like it's FALLING, purely from that methods change.
storm = storm[(storm['year'] >= 1987) & (storm['year'] <= 2025)].copy()

ann = storm.loc[storm.groupby('year')['max_wind'].idxmax()].set_index('year').sort_index()
top3 = storm.groupby('year')['max_wind'].apply(lambda s: s.nlargest(3).mean())

slope, intercept, r, p, se = stats.linregress(ann.index, ann['max_wind'])
z = lowess(ann['max_wind'], ann.index, frac=0.5, return_sorted=True)

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
STEM = '#F2C29A'
DOT = '#8B1E1E'
TREND_COLOR = '#1B3A5C'
TOP3_COLOR = '#2E7D6B'
FONT = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

baseline = 135
ax.vlines(ann.index, baseline, ann['max_wind'], color=STEM, linewidth=1.4, alpha=0.45, zorder=2)
ax.scatter(ann.index, ann['max_wind'], s=55, color=DOT, zorder=4, edgecolor='white', linewidth=0.6)

ax.plot(z[:, 0], z[:, 1], color=TREND_COLOR, linewidth=2.6, zorder=5, solid_capstyle='round')
ax.plot(top3.index, top3.values, color=TOP3_COLOR, linewidth=1.1, linestyle='--',
        zorder=3, alpha=0.45)

# annotate the record
rec_year = ann['max_wind'].idxmax()
rec_row = ann.loc[rec_year]
ax.annotate(f"{rec_row['name'].title()} ({rec_year}) — 185 kt, strongest in the record",
            xy=(rec_year, rec_row['max_wind']), xytext=(rec_year - 13, rec_row['max_wind'] + 4),
            fontsize=9.5, fontfamily=FONT, color=TEXT,
            arrowprops=dict(arrowstyle='-', color=MUTED, linewidth=0.8))


ax.set_xlim(1986, 2026)
ax.set_ylim(baseline, 190)
ax.set_yticks([140, 150, 160, 170, 180])
ax.set_yticklabels(['140 kt', '150', '160', '170', '180'], fontsize=10, fontfamily=FONT, color=MUTED)
ax.axhline(137, color=MUTED, linewidth=0.7, linestyle=':', zorder=1)
ax.text(2026.3, 137, ' Cat 5 threshold', fontsize=8.5, fontfamily=FONT, color=MUTED, va='center')

ax.grid(True, axis='y', color=GRID, linewidth=0.7, alpha=0.7, zorder=0)
for spine in ['top', 'right', 'left']:
    ax.spines[spine].set_visible(False)
ax.spines['bottom'].set_color('#CCCCCC')
ax.tick_params(left=False, bottom=True, labelsize=10.5, colors=TEXT)

ax.text(1987.3, 183, 'Strongest storm of the year', fontsize=10, fontfamily=FONT,
        fontweight='bold', color=DOT)
ax.text(1987.3, 178.5, '——  LOWESS trend', fontsize=10, fontfamily=FONT,
        fontweight='bold', color=TREND_COLOR)
ax.text(1987.3, 174, '- - -  Avg of top 3 storms (robustness check)', fontsize=10, fontfamily=FONT,
        fontweight='bold', color=TOP3_COLOR)

fig.text(0.06, 0.95, "THE TROPICAL CYCLONE WIND CEILING IS RISING", fontsize=26,
         fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.06, 0.915, f"THE STRONGEST STORM EACH YEAR HAS GAINED ~{slope*10:.0f} KT/DECADE SINCE 1987 (p={p:.3f})",
         fontsize=12, fontfamily=FONT, fontweight='bold', color='black', ha='left')
fig.text(0.06, 0.885, 'PEAK 1-MINUTE SUSTAINED WIND, STRONGEST STORM PER YEAR, GLOBAL, 1987–2025',
         fontsize=12, fontfamily=FONT, fontweight='bold', color=TREND_COLOR, ha='left')
fig.text(0.03, 0.025,
         'Source: IBTrACS via MakeoverMonday  |  Pre-1987 W. Pacific winds excluded: aircraft recon ended in 1987 and\n'
         'reanalyses (Knapp & Kruk 2010; Song et al. 2010) show a step-change intensity bias at that boundary, not a real decline  |  '
         'Rowan Olson · #MakeoverMonday',
         fontsize=8.3, fontfamily=FONT, color=MUTED, ha='left')

plt.tight_layout(rect=[0.04, 0.05, 0.93, 0.88])
plt.savefig('cyclones.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()