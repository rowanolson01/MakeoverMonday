import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('MM2026 W28 Park Amenities.csv', encoding='utf-16', sep='\t')

AMENITY_MAP = {
    'Splashpads': 'Splashpads',
    'Swimming Pools': 'Swimming Pools',
    'Playgrounds, Inclusive or Accessible': 'Accessible Playgrounds',
    'Playgrounds (includes schoolyards)': 'Playgrounds',
    'Community Garden Sites': 'Community Gardens',
    'Walking Loops or Tracks (includes schoolyards)': 'Walking Loops/Tracks',
    'Dog Parks': 'Dog Parks',
    'Disc Golf Courses': 'Disc Golf',
    'Restroom Facilities': 'Restroom Facilities',
    'Recreation/Senior Centers': 'Recreation/Senior Centers',
    'Fitness / Exercise Zones': 'Fitness Zones',
    'Basketball Hoops (Includes schoolyards)': 'Basketball Hoops',
    'Multipurpose Rectangle/Diamond Overlays': 'Multipurpose Overlays',
    'Multipurpose or Other Fields': 'Multipurpose Fields',
    'Rectangular Fields (e.g. Soccer, Football)': 'Rectangular Fields',
    'Combined fields and diamonds': 'Combined Fields & Diamonds',
    'Baseball and Softball Diamonds': 'Baseball/Softball Diamonds',
    'Outdoor volleyball courts': 'Outdoor Volleyball',
    'Outdoor tennis courts, dedicated': 'Outdoor Tennis Courts',
    'Outdoor tennis courts, striped with pickleball (excludes dedicated tennis and pickleball)': 'Outdoor Tennis Courts',
    'Outdoor pickleball courts, dedicated': 'Pickleball',
    'Outdoor pickleball courts, dedicated + tennis overlays': 'Pickleball',
    'Skate Parks': 'Skate Parks',
    'Improved Trail Mileage': None
}

STRUCTURED = ['Basketball Hoops', 'Baseball/Softball Diamonds', 'Combined Fields & Diamonds', 'Rectangular Fields', 'Multipurpose Fields', 'Multipurpose Overlays', 'Outdoor Volleyball', 'Outdoor Tennis Courts', 'Pickleball', 'Disc Golf', 'Skate Parks', 'Swimming Pools', 'Fitness Zones']
FLEXIBLE = ['Playgrounds', 'Accessible Playgrounds', 'Splashpads', 'Community Gardens', 'Walking Loops/Tracks', 'Dog Parks', 'Recreation/Senior Centers', 'Restroom Facilities']
YOUTH = ['Playgrounds', 'Accessible Playgrounds', 'Splashpads', 'Skate Parks', 'Baseball/Softball Diamonds', 'Combined Fields & Diamonds', 'Multipurpose Fields', 'Rectangular Fields', 'Basketball Hoops']
ALL_AGES = ['Swimming Pools', 'Community Gardens', 'Walking Loops/Tracks', 'Dog Parks', 'Disc Golf', 'Restroom Facilities', 'Recreation/Senior Centers', 'Fitness Zones', 'Multipurpose Overlays', 'Outdoor Volleyball', 'Outdoor Tennis Courts', 'Pickleball']
ALL_21 = sorted(set(STRUCTURED + FLEXIBLE))

assert set(df['Amenity Type'].unique()) == set(AMENITY_MAP)
assert not set(STRUCTURED) & set(FLEXIBLE)
assert not set(YOUTH) & set(ALL_AGES)
assert set(STRUCTURED) | set(FLEXIBLE) == set(YOUTH) | set(ALL_AGES)
assert len(ALL_21) == 21

counts = df[df['Measure Names'] == 'Count'].copy()
counts['Clean Amenity'] = counts['Amenity Type'].map(AMENITY_MAP)
counts = counts[counts['Clean Amenity'].notna()].copy()
counts['Climate Zone'] = counts['Climate Zone'].fillna('Unknown')

city_meta = counts.groupby('City').agg(State=('State', 'first'), Climate=('Climate Zone', 'first'))
pivot = counts.pivot_table(index='City', columns='Clean Amenity', values='Measure Values', aggfunc='sum', fill_value=0).reindex(columns=ALL_21, fill_value=0)

cs = pd.DataFrame(index=pivot.index)
cs['Structured_n'] = pivot[STRUCTURED].sum(axis=1)
cs['Flexible_n'] = pivot[FLEXIBLE].sum(axis=1)
cs['Youth_n'] = pivot[YOUTH].sum(axis=1)
cs['AllAges_n'] = pivot[ALL_AGES].sum(axis=1)

valid_x = (cs['Structured_n'] + cs['Flexible_n']) > 0
valid_y = (cs['Youth_n'] + cs['AllAges_n']) > 0
cs = cs[valid_x & valid_y].copy()

cs['x'] = (cs['Flexible_n'] - cs['Structured_n']) / (cs['Flexible_n'] + cs['Structured_n'])
cs['y'] = (cs['AllAges_n'] - cs['Youth_n']) / (cs['AllAges_n'] + cs['Youth_n'])
cs = cs.join(city_meta).reset_index()

BG, TEXT, MUTED, GRID, BLUE, AXIS = '#FFFFFF', '#111111', '#666666', '#D9D9D9', '#24466B', '#8A8A8A'

ZONE_COLORS = {
    'Cold': '#4C72B0',
    'Hot-Dry': '#DD8452',
    'Hot-Humid': '#C44E52',
    'Mixed-Humid': '#55A868',
    'Marine': '#64B5CD',
    'Mixed-Dry': '#8172B2',
    'Very Cold': '#1B2A4A'
}

ZONE_ORDER = ['Cold', 'Hot-Dry', 'Hot-Humid', 'Mixed-Humid', 'Marine', 'Mixed-Dry', 'Very Cold']

LABEL_OFFSETS = {
    'Miami, FL': (-4, -18),
    'Fremont, CA': (14, 10),
    'New Orleans, LA': (24, -18),
    'Oakland, CA': (16, -18),
    'Irving, TX': (2, -16),
    'Norfolk, VA': (0, -16),
    'North Las Vegas, NV': (-5, -16),
    'Chesapeake, VA': (14, -16)
}

plt.rcParams['font.family'] = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(12, 10), facecolor=BG)
ax.set_facecolor(BG)

x_min, x_max = -0.75, 0.25
y_min, y_max = -0.75, 0.25
ticks = np.arange(-0.75, 0.251, 0.25)

for value in ticks:
    ax.axvline(value, color=GRID, linewidth=0.75, alpha=0.75, zorder=0)
    ax.axhline(value, color=GRID, linewidth=0.75, alpha=0.75, zorder=0)

ax.axvline(0, color=AXIS, linewidth=1.2, zorder=1)
ax.axhline(0, color=AXIS, linewidth=1.2, zorder=1)

for zone in ZONE_ORDER:
    sub = cs[cs['Climate'] == zone]
    if sub.empty:
        continue
    ax.scatter(sub['x'], sub['y'], s=95, color=ZONE_COLORS[zone], edgecolor='white', linewidth=0.7, alpha=0.88, zorder=3, label=zone)

for city, offset in LABEL_OFFSETS.items():
    row = cs.loc[cs['City'] == city]
    if row.empty:
        continue
    row = row.iloc[0]
    ax.annotate(city, xy=(row['x'], row['y']), xytext=offset, textcoords='offset points', ha='left', va='top', fontsize=10, color=TEXT, fontweight='medium', arrowprops=dict(arrowstyle='-', color=MUTED, linewidth=0.6), zorder=5)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_aspect('auto')
ax.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.tick_params(colors=MUTED, labelsize=10)

ax.text(0.02, 0.98, 'STRUCTURED + ALL AGES', transform=ax.transAxes, fontsize=11, color='#C3C3C3', ha='left', va='top', fontweight='bold')
ax.text(0.98, 0.98, 'FLEXIBLE + ALL AGES', transform=ax.transAxes, fontsize=11, color='#C3C3C3', ha='right', va='top', fontweight='bold')
ax.text(0.02, 0.02, 'STRUCTURED + YOUTH', transform=ax.transAxes, fontsize=11, color='#C3C3C3', ha='left', va='bottom', fontweight='bold')
ax.text(0.98, 0.02, 'FLEXIBLE + YOUTH', transform=ax.transAxes, fontsize=11, color='#C3C3C3', ha='right', va='bottom', fontweight='bold')

ax.text(0.02, -0.11, '←  STRUCTURED', transform=ax.transAxes, fontsize=13, color=MUTED, ha='left', fontweight='bold')
ax.text(0.98, -0.11, 'FLEXIBLE  →', transform=ax.transAxes, fontsize=13, color=MUTED, ha='right', fontweight='bold')
ax.text(-0.055, 0.83, 'ALL AGES', transform=ax.transAxes, fontsize=13, color=MUTED, ha='center', va='center', rotation=90, fontweight='bold')
ax.text(-0.055, 0.91, '↑', transform=ax.transAxes, fontsize=16, color=MUTED, ha='center', va='center', fontweight='bold')
ax.text(-0.055, 0.17, 'YOUTH', transform=ax.transAxes, fontsize=13, color=MUTED, ha='center', va='center', rotation=90, fontweight='bold')
ax.text(-0.055, 0.09, '↓', transform=ax.transAxes, fontsize=16, color=MUTED, ha='center', va='center', fontweight='bold')

legend = ax.legend(loc='upper left', bbox_to_anchor=(0.025, .95), frameon=False, fontsize=8, title='Climate Zone', title_fontsize=11, ncol=1, labelspacing=0.45, handletextpad=0.5, borderaxespad=0)
legend.get_title().set_color(TEXT)

fig.text(0.045, 0.955, 'WHO ARE AMERICAN CITIES BUILDING PARKS FOR?', fontsize=28, fontweight='bold', color=TEXT, ha='left')
fig.text(0.045, 0.908, 'MOST CITIES FAVOR STRUCTURED, YOUTH-ORIENTED RECREATION', fontsize=15, fontweight='bold', color=TEXT, ha='left')
fig.text(0.045, 0.865, 'PARK PERSONALITIES OF 99 U.S. CITIES BY RECREATIONAL LEAN', fontsize=14, fontweight='bold', color=BLUE, ha='left')
fig.text(0.045, 0.025, 'Source: MakeoverMonday 2026, Week 28 — Park Amenities  |  Rowan Olson · #MakeoverMonday', fontsize=9, color=MUTED, ha='left')

fig.subplots_adjust(left=0.08, right=0.985, top=0.80, bottom=0.14)
plt.savefig('parkamenities.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()