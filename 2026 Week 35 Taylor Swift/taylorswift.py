from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W35 Taylor Swift.csv')

TOURS = ['Fearless Tour', 'Speak Now Tour', 'The Red Tour', 'The 1989 Tour', 'Reputation Tour', 'The Eras Tour']
TOUR_LABELS = ['Fearless', 'Speak Now', 'Red', '1989', 'Reputation', 'Eras']
df = df[df['Tour'].isin(TOURS)].copy()
df['TourOrder'] = df['Tour'].map({tour: i for i, tour in enumerate(TOURS)})

songs = df.groupby('Song').agg(Tours=('Tour', 'nunique'), First=('TourOrder', 'min')).reset_index()
songs = songs[songs['Tours'] >= 2].sort_values(['Tours', 'First', 'Song'], ascending=[False, True, True]).reset_index(drop=True)
songs['y'] = np.arange(len(songs))[::-1]

presence = df[df['Song'].isin(songs['Song'])].drop_duplicates(['Song', 'Tour']).assign(Present=1).pivot(index='Song', columns='Tour', values='Present').fillna(0)

BG, TEXT, MUTED, LIGHT = '#FFFFFF', '#111111', '#666666', '#D7DCE1'
BLUE, ORANGE = '#24466B', '#D96C2F'
FONT = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(13, 10))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for _, row in songs.iterrows():
    song, y = row['Song'], row['y']
    played = [i for i, tour in enumerate(TOURS) if presence.loc[song, tour] == 1]
    ax.plot([min(played), max(played)], [y, y], color=LIGHT, linewidth=2.2, zorder=1)
    for x in range(len(TOURS)):
        active = x in played
        highlight = song == 'Love Story'
        ax.scatter(x, y, s=165 if highlight and active else 105 if active else 28, color=ORANGE if highlight and active else BLUE if active else LIGHT, edgecolor=BG if active else 'none', linewidth=1.4 if active else 0, zorder=3 if active else 2)
    ax.text(5.28, y, f"{row['Tours']} tours", va='center', fontsize=9.5, fontfamily=FONT, fontweight='bold' if song == 'Love Story' else 'normal', color=ORANGE if song == 'Love Story' else MUTED)

ax.set_yticks(songs['y'])
ax.set_yticklabels(songs['Song'], fontsize=10.5, fontfamily=FONT, color=TEXT)
for label in ax.get_yticklabels():
    if label.get_text() == 'Love Story': label.set_color(ORANGE); label.set_fontweight('bold')

ax.set_xticks(range(6))
ax.set_xticklabels(TOUR_LABELS, fontsize=11, fontfamily=FONT, fontweight='bold', color=TEXT)
ax.xaxis.tick_top()
ax.tick_params(axis='x', length=0, pad=10)
ax.tick_params(axis='y', length=0, pad=8)
for x in range(6): ax.axvline(x, color=LIGHT, linewidth=0.8, zorder=0)
for spine in ax.spines.values(): spine.set_visible(False)

ax.set_xlim(-0.35, 6.05)
ax.set_ylim(-1, len(songs))
ax.grid(False)

fig.text(0.12, 0.955, 'LOVE STORY NEVER LEFT THE SETLIST', fontsize=24, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.12, 0.918, 'ACROSS SIX TOURS, ONLY ONE SONG APPEARS EVERY TIME', fontsize=13, fontfamily=FONT, fontweight='bold', color=ORANGE, ha='left')
fig.text(0.12, 0.885, 'SONGS SHOWN APPEARED ON AT LEAST TWO TOURS', fontsize=10.5, fontfamily=FONT, color=MUTED, ha='left')
fig.text(0.12, 0.035, 'Source: MakeoverMonday 2026, Week 35 — Taylor Swift Tours  |  Rowan Olson · #MakeoverMonday', fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

fig.subplots_adjust(left=0.30, right=0.89, top=0.82, bottom=0.08)
plt.savefig(HERE / 'taylorswift.png', dpi=180, facecolor=BG)
plt.show()