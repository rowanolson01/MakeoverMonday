import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('MM2026 W21 GPUs.csv')
df['Day'] = pd.to_datetime(df['Day'])

x_dates = pd.date_range('2008-01-01', '2033-01-01', periods=1000)
x_num = (x_dates - x_dates[0]).days.values
a = 0.72
b = 0.00072
y_curve = a * np.exp(b * x_num + 21.2)

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")
ax.set_ylim(1.7e8, 1.25e12)
ax.set_xlim(pd.Timestamp('2008-01-01'), pd.Timestamp('2033-01-01'))
ax.set_yscale('log')

ax.set_title('GPU Performance Per Dollar Is Growing Exponentially. \nWhere Might That Trend Lead?', fontfamily='Calibri', fontweight='bold', fontsize=24, loc='left')
ax.set_xlabel('')
ax.set_ylabel('')
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontfamily('Calibri')
    label.set_fontweight('bold')
    label.set_fontsize('16')

markers = {'AMD': 's', 'NVIDIA': 'o', 'Huawei': '^'}
colors = {'AMD': "#2A20B8", 'NVIDIA': "#5BCC26", 'Huawei': "#BB2C7B"}

ax.plot(x_dates, y_curve, color='black', linewidth=2, zorder=1)
for mfr, group in df.groupby('Manufacturer'):
    ax.scatter(group['Day'], group['GPU performance per dollar'], 
               marker=markers[mfr], label=mfr, zorder=2, color=colors[mfr])

ax.axvspan(pd.Timestamp('2024-03-01'), pd.Timestamp('2033-01-01'), alpha=0.1, color='red')

plt.axvline(x=pd.Timestamp('2030-01-01'), color='black', linestyle='--', linewidth=0.8)
ax.scatter(pd.Timestamp('2030-01-01'), 3.877e11, color='red', s=100, zorder=3)
ax.annotate('', xy=(pd.Timestamp('2025-01-01'), 3.877e11), xytext=(pd.Timestamp('2030-01-01'), 3.877e11), arrowprops=dict(arrowstyle='-', color='red'))
ax.text(pd.Timestamp('2027-06-01'), 2.75e11, '~388 Billion \nFLOPs/Dollar \nby 2030', fontfamily='Calibri', fontweight='bold', fontsize=20, ha='center')
ax.legend(loc='upper left', frameon=False, prop={'family': 'Calibri', 'weight': 'bold', 'size': 12})
ax.text(pd.Timestamp('2028-06-01'), 2e8, 'Projected', fontfamily='Calibri', fontweight='bold', fontsize=10, ha='center')

ax.text(pd.Timestamp('2007-06-01'), 8e7, 'Source: Epoch AI/Bureau of Labor Statistics via Makeover Monday', fontfamily='Calibri', fontweight='bold', fontsize=10)

plt.savefig('gpus.png', bbox_inches='tight')
plt.show()
