import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

df = pd.read_csv('MM2026 W23 Coachella.csv')
df = df[df['year'] >= 2022].reset_index(drop=True)

BG    = '#FFFFFF'
LINE  = '#2C5F8A'
DOT   = '#2C5F8A'
ANNOT = '#1a1a1a'
MUTED = '#666666'
RED   = '#C0392B'

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

x = np.array(range(len(df)), dtype=float)
y = np.array(df['total'].values, dtype=float)

x_smooth = np.linspace(x[0], x[-1], 300)
y_smooth = make_interp_spline(x, y, k=3)(x_smooth)

ax.plot(x_smooth, y_smooth, color=LINE, linewidth=2.5, solid_capstyle='round', zorder=3)
ax.scatter(x, y, color=DOT, s=55, zorder=5)

for xi, yi in zip(x, y):
    ax.text(xi, yi + 2.8, str(int(yi)), ha='center', va='bottom',
            fontsize=10, fontfamily='Calibri', fontweight='bold', color=ANNOT)

ax.annotate('',
    xy=(x[-1], y[-1] + 7),
    xytext=(x[0], y[0] + 7),
    arrowprops=dict(arrowstyle='->', color=RED, lw=1.5,
                    connectionstyle='arc3,rad=-0.18'))
ax.text((x[0] + x[-1]) / 2, y[0] + 15,
        '\u221222% artists since 2022',
        ha='center', va='bottom', fontsize=9.5, fontfamily='Calibri',
        fontweight='bold', color=RED)

ax.set_xticks(x)
ax.set_xticklabels(df['year'].astype(str),
                   fontsize=10.5, fontfamily='Calibri', color=ANNOT)

ax.set_ylim(120, 210)
ax.set_yticks([130, 150, 170, 190])
for label in ax.get_yticklabels():
    label.set_fontfamily('Calibri')
    label.set_color(MUTED)
    label.set_fontsize(9.5)

ax.yaxis.grid(True, color='#dddddd', linewidth=0.6, linestyle='--', zorder=0)
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#cccccc')

fig.text(0.055, 0.93, 'Coachella Lineup Size Has Declined Since 2022',
         fontsize=18, fontfamily='Calibri', fontweight='bold', color=ANNOT, ha='left')
fig.text(0.055, 0.885, 'Number of artists included in the initial lineup announcement',
         fontsize=14, fontfamily='Calibri', color=MUTED, ha='left')

fig.text(0.055, 0.02, 'Source: Chartmetric via Makeover Monday 2026 W23',
         fontsize=8.5, fontfamily='Calibri', color=MUTED, ha='left')
fig.text(0.97, 0.02, 'Rowan Olson | #MakeoverMonday',
         fontsize=8.5, fontfamily='Calibri', color=MUTED, ha='right')

plt.tight_layout(rect=[0, 0.04, 1, 0.88])
plt.savefig('coachella.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()