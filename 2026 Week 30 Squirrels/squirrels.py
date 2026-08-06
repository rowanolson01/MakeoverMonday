from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W30 Squirrels.csv', encoding='cp1252')

assert df['Squirrel ID'].notna().all()
assert df['Park Name'].notna().all()

activities = df['Activities'].fillna('').str.lower()
locations = df['Location'].fillna('').str.lower()

df['Food'] = activities.str.contains(r'forag|eat|dig|bury|food|nut', regex=True)
df['Active'] = activities.str.contains(r'run|chas|climb|jump|leap', regex=True)
df['Tree'] = locations.str.contains('above ground', regex=False) | activities.str.contains(r'climb|up tree|down tree', regex=True)

park = df.groupby('Park Name').agg(Observations=('Squirrel ID', 'size'), Food_n=('Food', 'sum'), Active_n=('Active', 'sum'), Tree_n=('Tree', 'sum')).reset_index()
park = park[park['Observations'] >= 10].copy()
park = park[(park['Food_n'] + park['Active_n']) > 0].copy()

park['x'] = (park['Food_n'] - park['Active_n']) / (park['Food_n'] + park['Active_n'])
park['y'] = park['Tree_n'] / park['Observations']

assert park['x'].between(-1, 1).all()
assert park['y'].between(0, 1).all()

park['Display'] = park['Park Name'].replace({'Riverside Park (Section Near Grant Memorial)': 'Riverside Park', 'John V. Lindsay East River Park': 'East River Park', 
    'Msgr. McGolrick Park': 'McGolrick Park'})

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
BLUE, ORANGE = '#24466B', '#D96C2F'
FONT = 'DejaVu Sans'

LABEL_OFFSETS = {
    'Marcus Garvey Park': (14, -8),
    'McGolrick Park': (12, 8),
    'Washington Square Park': (12, 12),
    'Stuyvesant Square Park': (16, -2),
    'Tompkins Square Park': (12, 18),
    'Fort Tryon Park': (12, 0)
}

fig, ax = plt.subplots(figsize=(12, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

obs_min, obs_max = park['Observations'].min(), park['Observations'].max()
sizes = 140 + ((park['Observations'] - obs_min) / (obs_max - obs_min)) ** 1.8 * 950
colors = np.where(park['x'] >= 0, ORANGE, BLUE)

ax.axvline(0, color=GRID, linewidth=1.0, zorder=0)
ax.axhline(0.5, color=GRID, linewidth=1.0, zorder=0)
ax.scatter(park['x'], park['y'], s=sizes, color=colors, edgecolor='white', linewidth=1.0, alpha=0.9, zorder=3)

for _, row in park.iterrows():
    if row['Display'] not in LABEL_OFFSETS:
        continue
    ax.annotate(row['Display'], xy=(row['x'], row['y']), xytext=LABEL_OFFSETS[row['Display']], textcoords='offset points', fontsize=9.4, fontfamily=FONT, fontweight='medium', 
        color=TEXT, ha='left', va='center', zorder=5)

ax.set_xlim(-0.75, 0.75)
ax.set_ylim(0.08, 1.02)
ax.set_xticks([-0.5, 0, 0.5])
ax.set_xticklabels(['More active', 'Balanced', 'More food-focused'], fontsize=10, fontfamily=FONT, color=MUTED)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=10, fontfamily=FONT, color=MUTED)
ax.set_ylabel('SHARE OBSERVED ABOVE GROUND OR CLIMBING', fontsize=10, fontfamily=FONT, fontweight='bold', color=MUTED, labelpad=12)
ax.grid(True, axis='y', color=GRID, linewidth=0.7, alpha=0.8, zorder=0)

for spine in ['top', 'right', 'left', 'bottom']:
    ax.spines[spine].set_visible(False)

ax.tick_params(left=False, bottom=False, colors=MUTED)

ax.text(0.02, 0.97, 'ACTIVE + TREE-ORIENTED', transform=ax.transAxes, fontsize=10.5, fontfamily=FONT, fontweight='bold', color='#B8B8B8', ha='left', va='top')
ax.text(0.98, 0.97, 'FOOD-FOCUSED + TREE-ORIENTED', transform=ax.transAxes, fontsize=10.5, fontfamily=FONT, fontweight='bold', color='#B8B8B8', ha='right', va='top')
ax.text(0.02, 0.03, 'ACTIVE + GROUND-ORIENTED', transform=ax.transAxes, fontsize=10.5, fontfamily=FONT, fontweight='bold', color='#B8B8B8', ha='left', va='bottom')
ax.text(0.98, 0.03, 'FOOD-FOCUSED + GROUND-ORIENTED', transform=ax.transAxes, fontsize=10.5, fontfamily=FONT, fontweight='bold', color='#B8B8B8', ha='right', va='bottom')
ax.text(0.02, -0.105, '←  MORE ACTIVE', transform=ax.transAxes, fontsize=12, fontfamily=FONT, fontweight='bold', color=BLUE, ha='left')
ax.text(0.98, -0.105, 'MORE FOOD-FOCUSED  →', transform=ax.transAxes, fontsize=12, fontfamily=FONT, fontweight='bold', color=ORANGE, ha='right')

fig.text(0.065, 0.955, 'NEW YORK PARKS HAVE DISTINCT SQUIRREL CULTURES', fontsize=25, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.065, 0.914, 'SOME PARKS ARE DEFINED BY CLIMBING AND CHASING. OTHERS BY THE SEARCH FOR FOOD.', fontsize=12.5, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.065, 0.878, 'BEHAVIORAL PERSONALITIES OF NYC PARKS WITH AT LEAST 10 OBSERVED SQUIRRELS', fontsize=12, fontfamily=FONT, fontweight='bold', color=BLUE, ha='left')
fig.text(0.04, 0.025, 'Source: NYC Squirrel Census via MakeoverMonday  |  Activity groups derived from observer notes  |  Circle size represents squirrels observed  |  Rowan Olson · #MakeoverMonday', fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

fig.subplots_adjust(left=0.11, right=0.96, top=0.82, bottom=0.16)
plt.savefig(HERE / 'squirrels.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()