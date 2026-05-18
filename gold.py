import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker

df = pd.read_csv('MM2026 W5 Gold Price.csv')
df = df.sort_values('Date')
df['Volatility'] = df['High (kg)']-df['Low (kg)']
df['VolatilitySmooth'] = df['Volatility'].rolling(3).mean()

fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor('#D9D9D9')
ax.set_facecolor('#D9D9D9')

df['Date'] = pd.to_datetime(df['Date'])

ax.plot(df['Date'], df['Close (kg)'] / 1000, color='black', linewidth=1.5)
ax.set_title('Gold Close Price Over Time')
ax.set_xlabel('')
ax.set_ylabel('Price (USD/g)')

ax2 = ax.twinx()
ax2.plot(df['Date'], df['VolatilitySmooth'] / 1000, color='blue', linewidth=1)
ax2.set_ylabel('Volatility (USD/g)', color='black')
ax2.tick_params(axis='y', labelcolor='black')

ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))
plt.xticks(rotation=0)
ax.yaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
ax.set_xlim(df['Date'].min(), df['Date'].max())
plt.tight_layout()
plt.show()