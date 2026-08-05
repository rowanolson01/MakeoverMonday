import re
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('MM2026 W29 Data Centers.csv')

def parse_mw(v):
    if pd.isna(v): return np.nan
    s = str(v).strip().replace(',', '')
    nums = re.findall(r'\d+\.?\d*', s)
    if not nums: return np.nan
    nums = [float(n) for n in nums]
    return nums[0] if len(nums) == 1 else sum(nums[:2]) / 2

df['mw_parsed'] = df['mw'].apply(parse_mw)

STAGES = ['Operating', 'Expanding', 'Approved/Permitted/Under construction', 'Proposed']
DISPLAY = {'Operating':'OPERATING','Expanding':'EXPANDING','Approved/Permitted/Under construction':'UNDER CONSTRUCTION','Proposed':'PROPOSED'}
POSITION = {'Operating':4,'Expanding':3,'Approved/Permitted/Under construction':2,'Proposed':1}

data = df[df['status'].isin(STAGES) & df['mw_parsed'].notna() & (df['mw_parsed'] > 0)].copy()
data['log_mw'] = np.log10(data['mw_parsed'])

BG,TEXT,MUTED,GRID = '#FFFFFF','#111111','#666666','#E3E3E3'
FONT = 'DejaVu Sans'
COLORS = {'Operating':'#9AA5AD','Expanding':'#6C8BA8','Approved/Permitted/Under construction':'#2F5F86','Proposed':'#E8702A'}

fig,ax = plt.subplots(figsize=(13.5,9.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

stats = {}
for stage in STAGES:
    vals = data.loc[data['status'] == stage, 'mw_parsed']
    stats[stage] = {'n':len(vals),'median':vals.median(),'q1':vals.quantile(.25),'q3':vals.quantile(.75)}

parts = ax.violinplot([data.loc[data['status']==s,'log_mw'].values for s in STAGES],positions=[POSITION[s] for s in STAGES],vert=False,widths=.85,showmedians=False,showextrema=False)

for stage,body in zip(STAGES,parts['bodies']):
    body.set_facecolor(COLORS[stage])
    body.set_edgecolor(BG)
    body.set_linewidth(1.2)
    body.set_alpha(.92)
    body.set_zorder(3)

for stage in STAGES:
    y,s = POSITION[stage],stats[stage]
    ax.plot([np.log10(s['q1']),np.log10(s['q3'])],[y,y],color=TEXT,linewidth=2.2,zorder=4,solid_capstyle='round')
    ax.scatter([np.log10(s['median'])],[y],s=70,color='white',edgecolor=TEXT,linewidth=1.6,zorder=5)

ax.set_xlabel('FACILITY CAPACITY (MEGAWATTS, LOG SCALE)',fontsize=10,fontfamily=FONT,color=MUTED,labelpad=10,fontweight='bold')
ax.set_yticks([POSITION[s] for s in STAGES])
ax.set_yticklabels([f"{DISPLAY[s]}\n{stats[s]['n']} Facilities" for s in STAGES],fontsize=11.5,fontfamily=FONT,color=TEXT,fontweight='bold')
ax.set_ylim(.3,4.8)
ax.grid(True,axis='x',color=GRID,linewidth=.7,alpha=.9,zorder=0)

for spine in ['top','right','left']: ax.spines[spine].set_visible(False)

ax.spines['bottom'].set_color('#CCCCCC')
ax.tick_params(left=False,bottom=True,labelsize=10,colors=MUTED)

tick_mw = [1,3,10,30,100,300,1000,3000]
ax.set_xticks(np.log10(tick_mw))
ax.set_xticklabels([f'{v:,}' for v in tick_mw],fontsize=10,fontfamily=FONT,color=MUTED)
ax.set_xlim(np.log10(3),np.log10(3000))

for stage in STAGES:
    y,med = POSITION[stage],stats[stage]['median']
    label = f'{med:,.0f} MW' if med >= 10 else f'{med:.1f} MW'
    ax.annotate(f'median {label}',xy=(np.log10(med),y),xytext=(0,14),textcoords='offset points',ha='center',fontsize=9.5,fontfamily=FONT,fontweight='bold',color=TEXT,zorder=6)

fig.text(0.195,0.9,"WE AREN'T JUST BUILDING MORE DATA CENTERS. \nWE'RE BUILDING BIGGER ONES.",fontsize=19,fontfamily=FONT,fontweight='bold',color=TEXT,ha='left')
fig.text(0.195,0.87,'THE TYPICAL PROPOSED FACILITY HAS OVER 15 TIMES THE CAPACITY OF ONE OPERATING TODAY',fontsize=12,fontfamily=FONT,fontweight='bold',color='black',ha='left')
fig.text(0.195,0.85,'U.S. DATA CENTER CAPACITY BY PIPELINE STAGE, IN MEGAWATTS',fontsize=12,fontfamily=FONT,fontweight='bold',color='#2F5F86',ha='left')

plt.tight_layout(rect=[0.04,0.17,0.98,0.85])
plt.savefig('datacenters.png',dpi=180,facecolor=BG)
plt.show()