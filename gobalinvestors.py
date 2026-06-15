import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

df = pd.read_csv('MM2026 W24 Global Investors.csv', encoding='latin-1')
df.columns = ['fdi', 'country', 'abbr']

df20 = df.head(20).copy()
df20['fdi_b'] = df20['fdi'] / 1000
df20['is_conduit'] = df20['country'].isin({'Luxembourg', 'British Virgin Islands', 'Cayman Islands', 'Ireland'})
df20 = df20.sort_values('fdi_b', ascending=True).reset_index(drop=True)

BG      = '#FFFFFF'
NAVY    = '#2C5F8A'
CONDUIT = '#999999'
GERMANY = '#C0392B'
TEXT    = '#1a1a1a'
MUTED   = '#666666'
ANNOT_R = '#C0392B'
FONT    = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(15, 10.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

def bar_color(row):
    if row['country'] == 'Germany': return GERMANY
    elif row['is_conduit']: return CONDUIT
    else: return NAVY

colors = [bar_color(row) for _, row in df20.iterrows()]
ax.barh(range(len(df20)), df20['fdi_b'], color=colors, height=0.62, zorder=3)

for i, (val, is_c, country) in enumerate(zip(df20['fdi_b'], df20['is_conduit'], df20['country'])):
    if country == 'Germany': col, fw = GERMANY, 'bold'
    elif is_c: col, fw = MUTED, 'normal'
    else: col, fw = TEXT, 'bold'
    ax.text(val + 1.8, i, f'${val:.0f}B', va='center', ha='left',
            fontsize=9, fontfamily=FONT, color=col, fontweight=fw)

ax.set_yticks(range(len(df20)))
ax.set_yticklabels(df20['country'], fontsize=10, fontfamily=FONT)
for tick, (_, row) in zip(ax.get_yticklabels(), df20.iterrows()):
    if row['country'] == 'Germany': tick.set_color(GERMANY); tick.set_fontweight('bold')
    elif row['is_conduit']: tick.set_color(MUTED)
    else: tick.set_color(TEXT)

lu_idx = df20[df20['country'] == 'Luxembourg'].index[0]
lu_val = df20.loc[lu_idx, 'fdi_b']

ax.text(200, lu_idx,
        "Population: 680,000\nThat's less than 1% of Germany's population.",
        va='center', ha='left', fontsize=8.5, fontfamily=FONT,
        color=TEXT, linespacing=1.5)

ax.plot([lu_val + 18, 198], [lu_idx, lu_idx],
        color='#BBBBBB', lw=0.8, linestyle='dotted', zorder=2)

de_idx = df20[df20['country'] == 'Germany'].index[0]
de_val = df20.loc[de_idx, 'fdi_b']
ratio  = lu_val / de_val

bracket_x = 155
ax.plot([bracket_x, bracket_x], [de_idx, lu_idx], color=ANNOT_R, lw=1.5, zorder=4)
ax.plot([bracket_x - 2, bracket_x], [de_idx, de_idx], color=ANNOT_R, lw=1.5, zorder=4)
ax.plot([bracket_x - 2, bracket_x], [lu_idx, lu_idx], color=ANNOT_R, lw=1.5, zorder=4)
ax.text(bracket_x + 2.5, (de_idx + lu_idx) / 2,
        f'Luxembourg invested\n{ratio:.1f}× more than\nGermany in 2024',
        va='center', ha='left', fontsize=9.5, fontfamily=FONT,
        color=ANNOT_R, fontweight='bold', linespacing=1.5)

conduit_total = df20[df20['is_conduit']]['fdi_b'].sum()
ax.text(0.99, -0.065, f'Conduit economies (grey) combined: ${conduit_total:.0f}B',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=9, fontfamily=FONT, color=MUTED, style='italic')

ax.xaxis.grid(True, color='#eeeeee', linewidth=0.8, linestyle='--', zorder=0)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(axis='x', colors=MUTED, labelsize=9)
ax.tick_params(axis='y', length=0)
ax.set_xlabel('FDI Outflows, 2024  (USD Billions)', fontsize=9.5,
              fontfamily=FONT, color=MUTED, labelpad=10)
ax.set_xlim(0, 300)

real_patch = mpatches.Patch(facecolor=NAVY,    edgecolor='none', label='Real economy investor')
cond_patch = mpatches.Patch(facecolor=CONDUIT, edgecolor='none', label='Financial conduit')
de_patch   = mpatches.Patch(facecolor=GERMANY, edgecolor='none', label='Germany (comparison)')
leg = ax.legend(handles=[real_patch, cond_patch, de_patch], loc='lower right',
                frameon=False, prop={'family': FONT, 'size': 9.5})
for t in leg.get_texts():
    t.set_color(TEXT)

fig.text(0.04, 0.965, 'Why Is Luxembourg Outinvesting Germany?',
         fontsize=26, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.04, 0.922,
         'Several top "investor countries" are financial conduits where capital passes through on its way elsewhere.\n'
         'Top 20 countries by FDI outflows, 2024.',
         fontsize=11, fontfamily=FONT, color=MUTED, ha='left', linespacing=1.6)

fig.text(0.04, 0.018, 'Source: UNCTAD, 2024 FDI Outflows  |  Rowan Olson · #MakeoverMonday',
         fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

plt.tight_layout(rect=[0, 0.04, 1, 0.895])
plt.savefig('globalinvestors.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()