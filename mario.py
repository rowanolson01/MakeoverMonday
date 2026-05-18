import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('MM2026 W10 Mario.csv')
df['Sales (Units)'] = pd.to_numeric(df['Sales (Units)'].astype(str).str.replace(',', ''), errors='coerce')
df['firstYear'] = df.groupby('Title')['Year'].transform('min')
game = df[df['Console'] == 'All Consoles']
game = game[game['Title'] != 'Total sales']

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('#D9D9D9')
ax.set_facecolor('#D9D9D9')

era_colors = {
    'Super Mario Bros.': '#990000',
    'Super Mario Bros. 2': '#CC2222',
    'Super Mario Bros. 3': '#FF6666',
    'Super Mario Land': "#CEA56C",
    'Super Mario World': "#DFB57B",
    'Super Mario Land 2': "#E5C89E",
    'Super Mario All-Stars': "#E7C9A1",
    'Super Mario Land 3': "#CFAE7F",
    'Super Mario World 2: Yoshi\'s Island': '#EDD5B0',
    'Super Mario 64': "#BE8C0B",
    'Super Mario Sunshine': "#D6AE48FB",
    'New Super Mario Bros.': '#002266',
    'Super Mario Galaxy': '#003399',
    'New Super Mario Bros. Wii': '#0044BB',
    'Super Mario Galaxy 2': '#0055CC',
    'Super Mario 3D Land': '#0077EE',
    'New Super Mario Bros. 2': '#2288FF',
    'New Super Mario Bros. U': '#55AAFF',
    'New Super Luigi U': '#88CCFF',
    'Super Mario 3D World': "#3A1F0BFF",
    'Super Mario Maker': "#3F230EFF",
    'Super Mario Odyssey': "#58381CFF",
    'Super Mario Maker 2': "#664527FF",
    'Super Mario Bros. Wonder': "#75511FFF",
}
colors = [era_colors[title] for title in game['Title']]

game.plot(kind='barh', y='Sales (Units)', x='Title',ax=ax, color=colors) 
ax.invert_yaxis()
ax.set_ylabel('')
ax.set_xlabel('Units Sold')
plt.xticks(rotation=0)
ax.get_legend().remove()
ax.xaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M'))
plt.tight_layout()
plt.show()