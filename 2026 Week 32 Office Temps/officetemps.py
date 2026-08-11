from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W32 Office Temps.csv')

MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
monthly = df[df['value_type'] == 'Monthly'].groupby('period').agg(Old=('baseline_1961_1990','first'), New=('baseline_1991_2020','first')).reindex(MONTHS).reset_index()
monthly['Change'] = monthly['New'] - monthly['Old']
monthly['theta'] = np.linspace(0, 2 * np.pi, 12, endpoint=False)

assert monthly[['Old','New','Change']].notna().all().all()
assert (monthly['Change'] > 0).all()

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
BLUE, ORANGE = '#24466B', '#D96C2F'
FONT = 'DejaVu Sans'

LABEL_OFFSETS = {
    'January': (0, 8),
    'February': (0, 8),
    'March': (15, 5),
    'April': (12, 12),
    'May': (-10, 7),
    'June': (0, 7),
    'July': (-2, 12),
    'August': (-23, 0),
    'September': (-13, 4),
    'October': (15, 5),
    'November': (0, 6),
    'December': (-13, 12)
}

theta_closed = np.append(monthly['theta'].values, monthly['theta'].iloc[0])
change_closed = np.append(monthly['Change'].values, monthly['Change'].iloc[0])

fig, ax = plt.subplots(figsize=(11, 11), subplot_kw={'projection':'polar'})
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

ax.fill(theta_closed, change_closed, color=BLUE, alpha=0.11, zorder=1)
ax.plot(theta_closed, change_closed, color=BLUE, linewidth=2.2, zorder=2)
ax.scatter(monthly['theta'], monthly['Change'], s=110, color=ORANGE, edgecolor='white', linewidth=1.0, zorder=3)

for _, row in monthly.iterrows():
    dx, dy = LABEL_OFFSETS[row['period']]
    ax.annotate(f"+{row['Change']:.2f}°", xy=(row['theta'], row['Change']), xytext=(dx, dy), textcoords='offset points', fontsize=9, fontfamily=FONT, fontweight='bold', 
        color=ORANGE, ha='center', va='bottom')

ax.set_xticks(monthly['theta'])
ax.set_xticklabels([m[:3].upper() for m in MONTHS], fontsize=11, fontfamily=FONT, fontweight='bold', color=TEXT)
ax.set_ylim(0, 1.35)
ax.set_yticks([0.25, 0.5, 0.75, 1.0, 1.25])
ax.set_yticklabels([])
ax.grid(True, color=GRID, linewidth=0.7, alpha=0.85)
ax.spines['polar'].set_visible(False)

fig.text(0.08, 0.955, 'THE OFFICE YEAR OVER THE YEARS', fontsize=25, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.08, 0.915, 'FEBRUARY-APRIL’S NORMAL TEMPS SHIFTED BY MORE THAN 1°C. OCTOBER MOVED JUST 0.30°C.', fontsize=12, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.08, 0.88, 'CHANGE IN MONTHLY TEMPERATURE NORMALS, 1961–1990 TO 1991–2020', fontsize=12, fontfamily=FONT, fontweight='bold', color=BLUE, ha='left')
fig.text(0.04, 0.025, 'Source: MakeoverMonday 2026, Week 32 — Office Temps  |  Rowan Olson · #MakeoverMonday', fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

plt.tight_layout(rect=[0.04, 0.06, 0.96, 0.84])
plt.savefig(HERE / 'officetemps.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()