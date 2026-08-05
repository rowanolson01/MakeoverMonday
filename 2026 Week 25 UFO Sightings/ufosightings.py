import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

np.random.seed(7)

df = pd.read_csv('MM2026 W25 UFO Sightings.csv', encoding='latin-1')
time_parts = df['time'].astype(str).str.split(':', expand=True)
df['hour_decimal'] = pd.to_numeric(time_parts[0], errors='coerce') + pd.to_numeric(time_parts[1], errors='coerce') / 60
df['sighting_date'] = pd.to_datetime(df['date'], format='%m/%d/%y', errors='coerce')
df['year'] = df['sighting_date'].dt.year

WORD_MINUTES = {'few minutes long': 3, 'few minutes': 3, 'several minutes': 5, 'couple minutes': 2, 'couple of minutes': 2, 'half hour': 30, 'half hour so far': 30, 
    'less than a minute': 0.5, 'a minute': 1, 'seconds': 0.25, 'minutes': 5, 'minute': 1, 'an hour': 60, 'one hour': 60, 'about an hour': 60, 'over an hour': 60, 'hour or longer': 60, 'several hours': 120, 'few hours': 120, 'very brief': 0.5, 'brief': 0.5, 'short': 1}
UNPARSEABLE_PATTERNS = ['ongoing', 'still going', 'unknown', 'ufo?', 'captured a still image', 'all during the night', 'still ongoing', 'filing at']
UNIT_TO_MINUTES = {'sec': 1/60, 'second': 1/60, 'seconds': 1/60, 'min': 1, 'mins': 1, 'minute': 1, 'minutes': 1, 'hr': 60, 'hrs': 60, 'hour': 60, 'hours': 60}

TIME_RANGE_RE = re.compile(r'from\s+(\d{1,2}:\d{2})\s*(am|pm)?\s*to\s+(\d{1,2}:\d{2})\s*(am|pm)?', re.IGNORECASE)
NUM_RANGE_RE = re.compile(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(sec|second|seconds|min|mins|minute|minutes|hr|hrs|hour|hours)', re.IGNORECASE)
NUM_UNIT_RE = re.compile(r'(\d+(?:\.\d+)?)\s*\+?\s*(sec|second|seconds|min|mins|minute|minutes|hr|hrs|hour|hours)', re.IGNORECASE)
BARE_NUMBER_RE = re.compile(r'^\d+(?:\.\d+)?$')

def parse_clock(time_str, meridiem):
    h, m = map(int, time_str.split(':'))
    if meridiem:
        meridiem = meridiem.lower()
        if meridiem == 'pm' and h != 12: h += 12
        elif meridiem == 'am' and h == 12: h = 0
    return h * 60 + m

def clean_duration(raw):
    if pd.isna(raw): return np.nan
    text = str(raw).strip().lower().replace('atleast', 'at least').replace('approx.', 'approx')
    if any(x in text for x in UNPARSEABLE_PATTERNS): return np.nan

    match = TIME_RANGE_RE.search(text)
    if match:
        start = parse_clock(match.group(1), match.group(2))
        end = parse_clock(match.group(3), match.group(4) or match.group(2))
        diff = end - start
        return diff + 24 * 60 if diff < 0 else diff

    match = NUM_RANGE_RE.search(text)
    if match: return ((float(match.group(1)) + float(match.group(2))) / 2) * UNIT_TO_MINUTES[match.group(3).lower()]

    match = NUM_UNIT_RE.search(text)
    if match: return float(match.group(1)) * UNIT_TO_MINUTES[match.group(2).lower()]

    for phrase, minutes in WORD_MINUTES.items():
        if phrase in text: return minutes

    if BARE_NUMBER_RE.match(text): return float(text)
    return np.nan

df['duration_minutes'] = df['duration'].apply(clean_duration)
df = df.dropna(subset=['hour_decimal', 'duration_minutes', 'year']).copy()
df = df[df['year'] < 2023].copy()

duration_cap = df['duration_minutes'].quantile(0.99)
df['duration_capped'] = df['duration_minutes'].clip(upper=duration_cap)

BG, TEXT, MUTED, GRID, BLUE = '#FFFFFF', '#111111', '#666666', '#D9D9D9', '#2C5F8A'
FONT, INNER_R, RADIAL_SCALE, R_JITTER = 'DejaVu Sans', 1.30, 0.82, 0.020

df['theta'] = (df['hour_decimal'] / 24) * 2 * np.pi
df['theta_jittered'] = df['theta'] + np.deg2rad(np.random.uniform(-1.2, 1.2, len(df)))
df['r_log'] = np.log10(df['duration_capped'] + 1) * RADIAL_SCALE
df['r_plot'] = INNER_R + df['r_log'] + np.random.uniform(-R_JITTER, R_JITTER, len(df))

ring_minutes, ring_labels = [1, 5, 15, 60, 360], ['1 min', '5 min', '15 min', '1 hr', '6 hr']
ring_r = [INNER_R + np.log10(x + 1) * RADIAL_SCALE for x in ring_minutes]
r_max = max(ring_r[-1], df['r_plot'].max()) + 0.12

df['year_facet'] = np.where(df['year'] < 2022, 'Pre-2022', '2022')
facet_order = ['Pre-2022', '2022']

duration_norm = LogNorm(vmin=1, vmax=df['duration_capped'].max())
cmap = plt.cm.turbo

fig, axes = plt.subplots(1, 2, figsize=(15.5, 9.2), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor(BG)
axes = np.atleast_1d(axes)

for ax, facet in zip(axes, facet_order):
    sub = df[df['year_facet'] == facet]

    ax.set_facecolor(BG)
    ax.scatter(sub['theta_jittered'], sub['r_plot'], s=14, c=sub['duration_capped'], cmap=cmap, norm=duration_norm, alpha=0.70, edgecolors='none', zorder=3)

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax.set_xticklabels(['12 AM', '3 AM', '6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM'], fontsize=9, fontfamily=FONT, fontweight='bold', color=TEXT)

    ax.set_ylim(0, r_max)
    ax.set_yticks(ring_r)
    ax.set_yticklabels(ring_labels, fontsize=8, fontfamily=FONT, color=MUTED)
    ax.set_rlabel_position(8)

    ax.add_artist(plt.Circle((0, 0), INNER_R - 0.06, transform=ax.transData._b, color=BG, zorder=4))
    ax.text(0, 0, f'{facet.upper()}\n{len(sub):,} REPORTS', ha='center', va='center', fontsize=11, fontfamily=FONT, fontweight='bold', color=TEXT, linespacing=1.35, zorder=5)

    ax.grid(True, color=GRID, linewidth=0.75, alpha=0.75)
    ax.spines['polar'].set_color('#CCCCCC')
    ax.spines['polar'].set_linewidth(0.8)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=duration_norm)
sm.set_array([])

cbar = fig.colorbar(sm, ax=axes, orientation='horizontal', fraction=0.035, pad=0.18, aspect=55)
cbar.set_label('Duration (minutes)', fontsize=10, fontfamily=FONT, labelpad=6)
cbar.ax.tick_params(labelsize=8)

fig.text(0.055, 0.950, 'THE UFO CLOCK', fontsize=30, fontfamily=FONT, fontweight='bold', color=TEXT, ha='left')
fig.text(0.055, 0.910, 'COMPARING UFO REPORTS BEFORE AND DURING 2022', fontsize=13, fontfamily=FONT, fontweight='bold', color=BLUE, ha='left')
fig.text(0.055, 0.878, 'Each point represents one reported UFO sighting. Position around the clock indicates time of day. Distance from the center and color both represent ' \
    'reported duration.', fontsize=10, fontfamily=FONT, color=MUTED, ha='left')
fig.text(0.055, 0.025, 'Source: NUFORC (National UFO Reporting Center)  |  Rowan Olson · #MakeoverMonday', fontsize=8.5, fontfamily=FONT, color=MUTED, ha='left')

plt.tight_layout(rect=[0.03, 0.16, 0.99, 0.84], w_pad=4)
plt.savefig('ufosightings.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()