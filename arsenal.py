import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

df = pd.read_csv('MM2026 W22 Arsenal.csv')

def get_top10(df):
    matches = df[['game_id', 'Home_Team', 'Away_Team', 'Match_Score']].drop_duplicates()
    
    def parse_score(score):
        try:
            h, a = score.replace('–', '-').split('-')
            return int(h.strip()), int(a.strip())
        except:
            return None, None
    
    points = {}
    for _, row in matches.iterrows():
        h, a = parse_score(row['Match_Score'])
        if h is None:
            continue
        home, away = row['Home_Team'], row['Away_Team']
        points.setdefault(home, 0)
        points.setdefault(away, 0)
        if h > a:
            points[home] += 3
        elif a > h:
            points[away] += 3
        else:
            points[home] += 1
            points[away] += 1
    
    standings = pd.Series(points).sort_values(ascending=False)
    top10 = standings.head(10).index.tolist()
    top10 = [t for t in top10 if t != 'Arsenal']
    return top10

top10 = get_top10(df)
arsenal = df[df['Team'] == 'Arsenal'].copy()
arsenal['Opponent'] = np.where(arsenal['Home_Team'] == 'Arsenal', arsenal['Away_Team'], arsenal['Home_Team'])
arsenal['BigGame'] = arsenal['Opponent'].isin(top10)

def per90(goals, assists, minutes):
    if minutes == 0:
        return 0
    return (goals + assists) / minutes * 90

stats = arsenal.groupby(['Player', 'BigGame']).agg(
    Goals=('Goals', 'sum'),
    Assists=('Assists', 'sum'),
    Minutes=('Minutes', 'sum')
).reset_index()
stats['G+A per90'] = stats.apply(lambda r: per90(r['Goals'], r['Assists'], r['Minutes']), axis=1)

stats_pivot = stats.pivot(index='Player', columns='BigGame', values='G+A per90').fillna(0)
stats_pivot.columns = ['Small', 'Big']
arsenalminutes = arsenal.groupby(['Player', 'BigGame'])['Minutes'].sum().unstack().fillna(0)
arsenalminutes = arsenalminutes[(arsenalminutes[True] + arsenalminutes[False]) >= 500]
stats_pivot = stats_pivot[stats_pivot.index.isin(arsenalminutes.index)]

font = {'family': 'Calibri', 'weight': 'bold', 'color': 'black'}
max_val = 1.0
fig, ax = plt.subplots(figsize=(8, 8))

dist = np.sqrt(stats_pivot['Small']**2 + stats_pivot['Big']**2)
norm = mcolors.Normalize(vmin=dist.min(), vmax=dist.max())
cmap = plt.cm.RdYlGn
colors = [cmap(norm(d)) for d in dist]

ax.plot([0, max_val], [0, max_val], color='gray', linestyle='--', linewidth=1, alpha=0.4, zorder=1)
ax.text(0.60, 0.63, 'equal performance', color='black', fontsize=10, rotation=45, fontfamily='Calibri', fontweight='bold')
ax.scatter(stats_pivot['Small'], stats_pivot['Big'], c=colors, s=120, zorder=3, edgecolors='none')

label_offsets = {
    'Mikel Merino':     (6, 4),
    'Kai Havertz':      (-8, -14),
    'Bukayo Saka':      (4, 10),
    'Viktor Gyökeres':  (6, -14),
    'Eberechi Eze':     (6, 4),
    'Leandro Trossard': (6, 4),
    'Martin Ødegaard':  (6, 4),
}

for player, (dx, dy) in label_offsets.items():
    row = stats_pivot.loc[player]
    ax.annotate(player, (row['Small'], row['Big']),
                textcoords='offset points', xytext=(dx, dy),
                fontsize=11, fontfamily='Calibri', fontweight='bold', color='black')
ax.annotate('Shows up when it counts\n0.46 → 0.70 G+A per 90 in big games',
            xy=(stats_pivot.loc['Mikel Merino', 'Small'], stats_pivot.loc['Mikel Merino', 'Big']),
            xytext=(0.18, 0.78),
            fontsize=10, fontfamily='Calibri', fontweight='bold', color='#2d6a2d',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
ax.annotate('Goes missing\n0.86 → 0.28 G+A per 90 in big games',
            xy=(stats_pivot.loc['Viktor Gyökeres', 'Small'], stats_pivot.loc['Viktor Gyökeres', 'Big']),
            xytext=(0.70, 0.04),
            fontsize=10, fontfamily='Calibri', fontweight='bold', color='#8b1a1a',
            arrowprops=dict(arrowstyle='->', color='black', lw=1.2))

ax.set_xlabel('G+A Per 90 vs Bottom-Half Opponents', fontsize=11, **font)
ax.set_ylabel('G+A Per 90 vs Top-Half Opponents', fontsize=11, **font)
ax.set_title('Who shows up when it matters?\nArsenal 25/26 — big game vs small game output',
             fontsize=18, loc='left', fontfamily='Calibri', fontweight='bold', color='black')
ax.set_xlim(-0.02, max_val)
ax.set_ylim(-0.02, max_val)
ax.set_aspect('equal')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(labelsize=9)
for tick in ax.get_xticklabels() + ax.get_yticklabels():
    tick.set_fontfamily('Calibri')
    tick.set_fontweight('bold')
    tick.set_color('black')

fig.text(0.02, 0.01,
         'Data: FBref | Article: arsenal.com | Makeover Monday W22',
         fontsize=8, fontfamily='Calibri', color='gray')

plt.tight_layout()
plt.savefig('arsenal.png', dpi=150, bbox_inches='tight')
plt.show()