import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

np.random.seed(7)

df = pd.read_csv('MM2026 W25 UFO Sightings.csv', encoding='latin-1')

time_parts = df['time'].astype(str).str.split(':', expand=True)
df['hour_decimal'] = pd.to_numeric(time_parts[0], errors='coerce') + (
    pd.to_numeric(time_parts[1], errors='coerce') / 60
)

df['sighting_date'] = pd.to_datetime(df['date'], format='%m/%d/%y', errors='coerce')
df['year'] = df['sighting_date'].dt.year

WORD_MINUTES = {
    'few minutes long': 3, 'few minutes': 3, 'several minutes': 5,
    'couple minutes': 2, 'couple of minutes': 2, 'half hour': 30,
    'half hour so far': 30, 'less than a minute': 0.5, 'a minute': 1,
    'seconds': 0.25, 'minutes': 5, 'minute': 1,
    'an hour': 60, 'one hour': 60, 'about an hour': 60, 'over an hour': 60,
    'hour or longer': 60, 'several hours': 120, 'few hours': 120,
    'very brief': 0.5, 'brief': 0.5, 'short': 1,
}

UNPARSEABLE_PATTERNS = [
    'ongoing', 'still going', 'unknown', 'ufo?', 'captured a still image',
    'all during the night', 'still ongoing', 'filing at',
]

UNIT_TO_MINUTES = {
    'sec': 1 / 60, 'second': 1 / 60, 'seconds': 1 / 60,
    'min': 1, 'mins': 1, 'minute': 1, 'minutes': 1,
    'hr': 60, 'hrs': 60, 'hour': 60, 'hours': 60,
}

TIME_RANGE_RE = re.compile(
    r'from\s+(\d{1,2}:\d{2})\s*(am|pm)?\s*to\s+(\d{1,2}:\d{2})\s*(am|pm)?',
    re.IGNORECASE
)

NUM_RANGE_RE = re.compile(
    r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*'
    r'(sec|second|seconds|min|mins|minute|minutes|hr|hrs|hour|hours)',
    re.IGNORECASE
)

NUM_UNIT_RE = re.compile(
    r'(\d+(?:\.\d+)?)\s*\+?\s*'
    r'(sec|second|seconds|min|mins|minute|minutes|hr|hrs|hour|hours)',
    re.IGNORECASE
)

BARE_NUMBER_RE = re.compile(r'^\d+(?:\.\d+)?$')


def parse_clock(time_str, meridiem):
    h, m = time_str.split(':')
    h, m = int(h), int(m)

    if meridiem:
        meridiem = meridiem.lower()
        if meridiem == 'pm' and h != 12:
            h += 12
        elif meridiem == 'am' and h == 12:
            h = 0

    return h * 60 + m


def clean_duration(raw):
    if pd.isna(raw):
        return np.nan

    text = str(raw).strip().lower()
    text = text.replace('atleast', 'at least').replace('approx.', 'approx')

    if any(pattern in text for pattern in UNPARSEABLE_PATTERNS):
        return np.nan

    match = TIME_RANGE_RE.search(text)
    if match:
        start_min = parse_clock(match.group(1), match.group(2))
        end_min = parse_clock(match.group(3), match.group(4) or match.group(2))
        diff = end_min - start_min

        if diff < 0:
            diff += 24 * 60

        return diff

    match = NUM_RANGE_RE.search(text)
    if match:
        low, high, unit = float(match.group(1)), float(match.group(2)), match.group(3).lower()
        return ((low + high) / 2) * UNIT_TO_MINUTES[unit]

    match = NUM_UNIT_RE.search(text)
    if match:
        value, unit = float(match.group(1)), match.group(2).lower()
        return value * UNIT_TO_MINUTES[unit]

    for phrase, minutes in WORD_MINUTES.items():
        if phrase in text:
            return minutes

    if BARE_NUMBER_RE.match(text):
        return float(text)

    return np.nan


df['duration_minutes'] = df['duration'].apply(clean_duration)

df = df.dropna(subset=['hour_decimal', 'duration_minutes', 'year', 'population']).copy()
df = df[df['year'] < 2023].copy()

duration_cap = df['duration_minutes'].quantile(0.99)
df['duration_capped'] = df['duration_minutes'].clip(upper=duration_cap)

pop_bins = [0, 10_000, 50_000, 250_000, 1_000_000, np.inf]
pop_labels = ['Under 10k', '10k - 50k', '50k - 250k', '250k - 1M', '1M+']

df['population_bucket'] = pd.cut(
    df['population'],
    bins=pop_bins,
    labels=pop_labels,
    include_lowest=True
)

BG      = '#FFFFFF'
BLUE    = '#2C5F8A'
TEAL    = '#2F9C95'
GREEN   = '#4A9E4F'
ORANGE  = '#E08E2B'
RED     = '#C84236'
TEXT    = '#111111'
MUTED   = '#666666'
GRID    = '#D9D9D9'
FONT    = 'DejaVu Sans'

POP_COLORS = {
    'Under 10k': BLUE,
    '10k - 50k': TEAL,
    '50k - 250k': GREEN,
    '250k - 1M': ORANGE,
    '1M+': RED,
}

INNER_R = 1.30
RADIAL_SCALE = 0.82
R_JITTER = 0.020

df['theta'] = (df['hour_decimal'] / 24) * 2 * np.pi
df['theta_jittered'] = df['theta'] + np.deg2rad(np.random.uniform(-1.2, 1.2, len(df)))
df['r_log'] = np.log10(df['duration_capped'] + 1) * RADIAL_SCALE
df['r_plot'] = INNER_R + df['r_log'] + np.random.uniform(-R_JITTER, R_JITTER, len(df))

ring_minutes = [1, 5, 15, 60, 360]
ring_labels = ['1 min', '5 min', '15 min', '1 hr', '6 hr']
ring_r = [INNER_R + np.log10(m + 1) * RADIAL_SCALE for m in ring_minutes]

r_max = max(ring_r[-1], df['r_plot'].max()) + 0.12

df['year_facet'] = df['year'].apply(lambda y: 'Pre-2020' if y < 2020 else str(int(y)))
facet_order = [f for f in ['Pre-2020', '2020', '2021', '2022'] if f in set(df['year_facet'])]

fig, axes = plt.subplots(
    2,
    2,
    figsize=(15, 10.5),
    subplot_kw={'projection': 'polar'}
)

fig.patch.set_facecolor(BG)
axes = axes.flatten()

for ax in axes:
    ax.set_facecolor(BG)

for ax, facet in zip(axes, facet_order):
    sub = df[df['year_facet'] == facet].copy()

    for bucket in pop_labels:
        cells = sub[sub['population_bucket'] == bucket]

        if cells.empty:
            continue

        ax.scatter(
            cells['theta_jittered'],
            cells['r_plot'],
            s=8,
            c=POP_COLORS[bucket],
            alpha=0.55,
            edgecolors='none',
            zorder=3
        )

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    ax.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax.set_xticklabels(
        ['12 AM', '3 AM', '6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM'],
        fontsize=8.5,
        fontfamily=FONT,
        fontweight='bold',
        color=TEXT
    )

    ax.set_ylim(0, r_max)
    ax.set_yticks(ring_r)
    ax.set_yticklabels(
        ring_labels,
        fontsize=7.5,
        fontfamily=FONT,
        color=MUTED
    )
    ax.set_rlabel_position(8)

    inner_disk = plt.Circle(
        (0, 0),
        INNER_R - 0.06,
        transform=ax.transData._b,
        color=BG,
        zorder=4
    )
    ax.add_artist(inner_disk)

    count = len(sub)
    ax.text(
        0,
        0,
        f'{facet.upper()}\n{count:,} SIGHTINGS',
        ha='center',
        va='center',
        fontsize=10.5,
        fontfamily=FONT,
        fontweight='bold',
        color=TEXT,
        linespacing=1.35,
        zorder=5
    )

    ax.grid(True, color=GRID, linewidth=0.75, alpha=0.75, zorder=0)
    ax.spines['polar'].set_color('#CCCCCC')
    ax.spines['polar'].set_linewidth(0.8)

for ax in axes[len(facet_order):]:
    ax.set_visible(False)

legend_handles = [
    mpatches.Patch(facecolor=POP_COLORS[label], edgecolor='none', label=label)
    for label in pop_labels
]

leg = fig.legend(
    handles=legend_handles,
    title='CITY POPULATION',
    loc='upper right',
    bbox_to_anchor=(0.955, 0.918),
    frameon=False,
    prop={'family': FONT, 'size': 10.5},
    title_fontproperties={'family': FONT, 'size': 11.5, 'weight': 'bold'}
)

for text in leg.get_texts():
    text.set_color(TEXT)

leg.get_title().set_color(TEXT)

fig.text(
    0.04,
    0.965,
    'THE UFO CLOCK: YEAR BY YEAR',
    fontsize=30,
    fontfamily=FONT,
    fontweight='bold',
    color=TEXT,
    ha='left'
)

fig.text(
    0.04,
    0.922,
    "WHEN SIGHTINGS HAPPEN, HOW LONG THEY LAST, AND WHERE THEY'RE REPORTED",
    fontsize=13,
    fontfamily=FONT,
    fontweight='bold',
    color=BLUE,
    ha='left'
)

fig.text(
    0.04,
    0.887,
    'Each dot is one reported sighting. Angle shows time of day. Distance from center shows duration '
    '(log scale). Color shows city population.',
    fontsize=10.5,
    fontfamily=FONT,
    color=MUTED,
    ha='left'
)

fig.text(
    0.04,
    0.018,
    'Source: NUFORC (National UFO Reporting Center)  |  Rowan Olson · #MakeoverMonday',
    fontsize=8.5,
    fontfamily=FONT,
    color=MUTED,
    ha='left'
)

plt.tight_layout(rect=[0.035, 0.055, 0.89, 0.86], h_pad=2.5, w_pad=3.1)
plt.savefig('ufosightings.png', dpi=180, bbox_inches='tight', facecolor=BG)
plt.show()