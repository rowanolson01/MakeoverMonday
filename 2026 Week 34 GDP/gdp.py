from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import textwrap

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE / 'MM2026 W34 GDP.csv')

df = df.sort_values('rank').reset_index(drop=True)
df['country'] = df['country'].replace({'Russian Federation': 'Russia', 'Korea, Rep.': 'S. Korea', 'United Kingdom': 'United\nKingdom'})
df['Share'] = df['value'] / df['value'].sum()
df['Cumulative'] = df['Share'].cumsum()

assert len(df) == 192
assert df['rank'].is_monotonic_increasing
assert df['value'].notna().all()

targets = [0.25, 0.50, 0.75]
bounds = [int(df.loc[(df['Cumulative'] - t).abs().idxmin(), 'rank']) for t in targets]
cuts = [0] + bounds + [int(df['rank'].max())]

df['Bucket'] = 0
for i in range(4):
    df.loc[(df['rank'] > cuts[i]) & (df['rank'] <= cuts[i + 1]), 'Bucket'] = i + 1

summary = df.groupby('Bucket').agg(Start=('rank','min'), End=('rank','max'), Countries=('country','size'), GDP=('value','sum')).reset_index()
summary['Share'] = summary['GDP'] / df['value'].sum()

BG, TEXT, MUTED = '#FFFFFF', '#111111', '#666666'
BLUE, MIDBLUE, ORANGE, GREY = '#24466B', '#5F7F9D', '#D96C2F', '#AAB4BD'
FONT = 'DejaVu Sans'
COLORS = [BLUE, MIDBLUE, ORANGE, GREY]

def split_treemap(values, labels, x, y, w, h):
    if len(values) == 1:
        return [(x, y, w, h, labels[0])]
    total = sum(values)
    cumulative = np.cumsum(values)
    split = int(np.argmin(np.abs(cumulative - total / 2))) + 1
    split = min(max(split, 1), len(values) - 1)
    first_values, second_values = values[:split], values[split:]
    first_labels, second_labels = labels[:split], labels[split:]
    first_share = sum(first_values) / total
    if w >= h:
        w1 = w * first_share
        return split_treemap(first_values, first_labels, x, y, w1, h) + split_treemap(second_values, second_labels, x + w1, y, w - w1, h)
    h1 = h * first_share
    return split_treemap(first_values, first_labels, x, y, w, h1) + split_treemap(second_values, second_labels, x, y + h1, w, h - h1)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.patch.set_facecolor(BG)
axes = axes.flatten()

for i, ax in enumerate(axes, start=1):
    sub = df[df['Bucket'] == i].sort_values('value', ascending=False).copy()
    rects = split_treemap(sub['value'].tolist(), sub['country'].tolist(), 0, 0, 1.5, 1)
    ax.set_facecolor(BG)

    for x, y, w, h, label in rects:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=COLORS[i - 1], edgecolor='white', linewidth=1.2))
        if i == 4:
            continue
        area = w * h
        if area > 0.18:
            fontsize, wrap = 15, 18
        elif area > 0.08:
            fontsize, wrap = 11, 15
        elif area > 0.04:
            fontsize, wrap = 9, 12
        elif area > 0.025:
            fontsize, wrap = 7.5, 10
        else:
            continue
        if label == 'Russia':
            fontsize *= 0.8
        wrapped = label if '\n' in label else '\n'.join(textwrap.wrap(label, width=wrap))
        ax.text(x + w / 2, y + h / 2, wrapped, ha='center', va='center', fontsize=fontsize, fontfamily=FONT, fontweight='bold', color='white', clip_on=True)

    row = summary[summary['Bucket'] == i].iloc[0]
    start, end = int(row['Start']), int(row['End'])
    rank_text = f"RANK {start}" if start == end else f"RANKS {start}–{end}"
    country_text = '1 ECONOMY' if row['Countries'] == 1 else f"{int(row['Countries'])} ECONOMIES"

    ax.text(0, 1.07, f"{row['Share']:.1%} OF GDP", transform=ax.transAxes, fontsize=15, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
    ax.text(0, 1.015, country_text, transform=ax.transAxes, fontsize=11, fontfamily=FONT, fontweight='bold', color=COLORS[i - 1], ha='left')
    ax.text(0, -0.055, rank_text, transform=ax.transAxes, fontsize=9.5, fontfamily=FONT, color=MUTED, ha='left')

    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

fig.text(0.055, 0.965, 'ONE ECONOMY PRODUCES A QUARTER OF WORLD GDP', fontsize=24, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.055, 0.925, 'THE NEXT QUARTER TAKES 3 ECONOMIES. THE FINAL QUARTER TAKES 177.', fontsize=12.5, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.055, 0.89, 'THE WORLD ECONOMY SPLIT INTO FOUR ROUGHLY EQUAL SHARES OF GDP, RANKED LARGEST TO SMALLEST', fontsize=11.5, fontfamily=FONT, fontweight='bold', 
    color=BLUE, ha='left')
fig.text(0.04, 0.025, 'Source: MakeoverMonday 2026, Week 34 — GDP  |  Bucket boundaries chosen nearest each cumulative 25% threshold  |  Rowan Olson · #MakeoverMonday', 
    fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

fig.subplots_adjust(left=0.055, right=0.945, top=0.82, bottom=0.11, wspace=0.04, hspace=0.28)
plt.savefig(HERE / 'gdp.png', dpi=180, facecolor=BG)
plt.show()