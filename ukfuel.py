import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('MM2026 W20 UK Fuel.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.drop(columns=['Unleaded pump (exc VAT)', 'Diesel pump (exc VAT)'])
df['Unleaded Margin'] = df['Unleaded pump (inc VAT)']-df['Unleaded delivered wholesale']
df['Diesel Margin'] = df['Diesel pump (inc VAT)']-df['Diesel delivered wholesale']

fig, ax = plt.subplots(figsize=(15, 8))
fig.patch.set_facecolor('#D9D9D9')
ax.set_facecolor('#D9D9D9')

ax.plot(df['Date'], df['Unleaded pump (inc VAT)'], color="#373AD1", linewidth=1.2, label='Unleaded')
ax.plot(df['Date'], df['Diesel pump (inc VAT)'], color="#D4851E", linewidth=1.2, label='Diesel')
ax.set_title('UK Fuel Prices over Time', fontfamily='Calibri', fontweight='bold', fontsize=16)
ax.set_xlabel('')
ax.set_ylabel('Price (Pence/L)', fontfamily='Calibri', fontweight='bold')
ax.yaxis.set_major_formatter(plt.matplotlib.ticker.FuncFormatter(lambda x, _: f'{x:,.0f}p'))
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontfamily('Calibri')
    label.set_fontweight('bold')

plt.axvline(x=pd.Timestamp('2014-11-27'), color='black', linestyle='--', linewidth=0.8)
plt.axvline(x=pd.Timestamp('2020-03-01'), color='black', linestyle='--', linewidth=0.8)
plt.axvline(x=pd.Timestamp('2022-02-24'), color='black', linestyle='--', linewidth=0.8)
plt.axvline(x=pd.Timestamp('2026-02-28'), color='black', linestyle='--', linewidth=0.8)
ax.text(pd.Timestamp('2013-06-27'), 150, 'OPEC Price Crash', fontfamily='Calibri', fontweight='bold')
ax.text(pd.Timestamp('2018-01-01'), 142, 'COVID-19 Demand Collapse', fontfamily='Calibri', fontweight='bold')
ax.text(pd.Timestamp('2020-04-26'), 157, 'Russia Invades Ukraine', fontfamily='Calibri', fontweight='bold')
ax.text(pd.Timestamp('2024-03-10'), 162, 'US and Israel Invade Iran', fontfamily='Calibri', fontweight='bold')
ax.annotate('', xy=(pd.Timestamp('2013-06-27'), 149), xytext=(pd.Timestamp('2014-12-01'), 149), arrowprops=dict(arrowstyle='-', color='black'))
ax.annotate('', xy=(pd.Timestamp('2018-01-01'), 141), xytext=(pd.Timestamp('2020-03-06'), 141), arrowprops=dict(arrowstyle='-', color='black'))
ax.annotate('', xy=(pd.Timestamp('2020-04-26'), 156), xytext=(pd.Timestamp('2022-03-01'), 156), arrowprops=dict(arrowstyle='-', color='black'))
ax.annotate('', xy=(pd.Timestamp('2024-03-10'), 161), xytext=(pd.Timestamp('2026-03-05'), 161), arrowprops=dict(arrowstyle='-', color='black'))

ax.legend(loc='upper left', frameon=False, prop={'family': 'Calibri', 'weight': 'bold'})
plt.show()