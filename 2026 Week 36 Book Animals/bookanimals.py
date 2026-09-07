from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W36 Book Animals.csv')

df = df[df['pronoun'].isin(['he/him','she/her']) & df['pub_year'].notna()].copy()
df['Era'] = np.select([df['pub_year'] < 1975, df['pub_year'] <= 2000], ['Before 1975','1975–2000'], default='After 2000')
ERAS = ['Before 1975','1975–2000','After 2000']

trend = df.groupby(['animal_group','Era']).agg(n=('pronoun','size'), Female=('pronoun',lambda s:(s == 'she/her').mean())).reset_index()
keepers = trend[trend['n'] >= 5].groupby('animal_group')['Era'].nunique()
keepers = keepers[keepers == 3].index
trend = trend[trend['animal_group'].isin(keepers) & (trend['n'] >= 5)].copy()
trend['Era'] = pd.Categorical(trend['Era'], ERAS, ordered=True)
trend = trend.sort_values(['animal_group','Era'])

BG, TEXT, MUTED, GRID = '#FFFFFF', '#111111', '#666666', '#E3E3E3'
FONT = 'DejaVu Sans'
PALETTE = ['#8C6A4A','#4C72B0','#8172B2','#C44E52','#8A8A8A','#55A868','#D98C3F','#6A994E','#9C6ADE','#2A9D8F','#E76F51','#577590']

animals = list(keepers)
COLORS = {animal: PALETTE[i % len(PALETTE)] for i, animal in enumerate(animals)}
LABELS = {animal: animal.title() for animal in animals}
LABEL_OFFSETS = {'pig':(10,8),'cat':(10,-8),'rabbit':(10,9),'bear':(10,-9),'mouse':(10,-13),'dog':(10,8)}

fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for animal in animals:
    sub = trend[trend['animal_group'] == animal].set_index('Era').reindex(ERAS).reset_index()
    x = np.arange(3)
    y = sub['Female'].to_numpy()
    smooth_x = np.linspace(0, 2, 200)
    smooth_y = np.polyval(np.polyfit(x, y, 2), smooth_x)
    ax.plot(smooth_x, smooth_y, color=COLORS[animal], linewidth=2.8, zorder=2, solid_capstyle='round')
    ax.scatter(x, y, s=70, color=COLORS[animal], zorder=3)
    dx, dy = LABEL_OFFSETS.get(animal, (10,0))
    ax.annotate(LABELS[animal], xy=(2, y[-1]), xytext=(dx,dy), textcoords='offset points', fontsize=10.5, fontfamily=FONT, fontweight='bold', color=COLORS[animal], 
        ha='left', va='center')

ax.set_xlim(-0.08, 2.08)
ax.set_ylim(0, 0.75)
ax.set_xticks(range(3))
ax.set_xticklabels(ERAS, fontsize=11, fontfamily=FONT, fontweight='bold', color=TEXT)
ax.set_yticks([0,0.25,0.5,0.75])
ax.set_yticklabels(['0%','25%','50%','75%'], fontsize=10, fontfamily=FONT, color=MUTED)
ax.set_ylabel('SHARE OF GENDERED CHARACTERS THAT ARE FEMALE', fontsize=10, fontfamily=FONT, fontweight='bold', color=MUTED, labelpad=10)
ax.grid(True, axis='y', color=GRID, linewidth=0.7, alpha=0.8, zorder=0)
ax.tick_params(left=False, bottom=False)

for spine in ax.spines.values(): spine.set_visible(False)

fig.text(0.065, 0.955, 'BOOK ANIMALS HAVE VERY DIFFERENT GENDER HISTORIES', fontsize=25, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.065, 0.914, 'AFTER 2000, FAMILIAR ANIMALS LAND ON VERY DIFFERENT SIDES OF THE GENDER SPLIT', fontsize=12.2, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.065, 0.878, 'GENDER REPRESENTATION ACROSS THREE PUBLISHING ERAS', fontsize=11.5, fontfamily=FONT, fontweight='bold', color='#24466B', ha='left')
fig.text(0.035, 0.025, 'Source: MakeoverMonday 2026, Week 36 — Book Animals  |  Animal-era points require at least 5 gendered characters; animals shown have valid observations in all three eras  |  Rowan Olson · #MakeoverMonday', fontsize=8.3, fontfamily=FONT, color=MUTED, ha='left')

fig.subplots_adjust(left=0.065, right=0.965, top=0.82, bottom=0.13)
plt.savefig(HERE / 'bookanimals.png', dpi=180, facecolor=BG)
plt.show()