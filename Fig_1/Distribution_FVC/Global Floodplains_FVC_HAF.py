# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 16:12:27 2023

@author: Huang Sheng
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.ticker import FuncFormatter
import numpy as np

# ======================
# ======================
world_boundary = gpd.read_file('Data/wmoWorld/World_Boundary.shp')
world_map = gpd.read_file('Data/wmoWorld/wmobb_basins.shp')
basin_map = gpd.read_file('Data/Basin91/Basin91.shp')

ndvi_data = pd.read_csv('Data/Veg/VC_HAF_nearest_interpolation.csv', header=0)
merged_data = basin_map.merge(ndvi_data, on='newFID', how='left')

# ======================
# ======================
colors = [
    "#FEC44F",  
    "#FEE08B",   
    "#D9F0D3",  
    "#A6DBA0",  
    "#7BC8A4",  
    "#4DAC7D",  
    "#2F8F6F",  
    "#1B7F5C",  
    "#0B5D3B",  
]

boundaries = [-0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4]
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N)

# ======================
# ======================
fig, ax = plt.subplots(figsize=(10, 6))

# world_boundary.boundary.plot(ax=ax, linewidth=0.2, color='#D9D9D9')
world_map.plot(ax=ax, color='lightgray', alpha=0.6)


merged_data.plot(
    column='VC',
    cmap=cmap,
    norm=norm,
    ax=ax,
    linewidth=0.6,
    edgecolor='white'
)

# ======================
# ======================

pos_subset = merged_data[merged_data['MK'] >= 3]
ax.scatter(
    pos_subset.geometry.centroid.x,
    pos_subset.geometry.centroid.y,
    s=18,
    marker='+',
    color='black',
    linewidths=0.8
)


neg_subset = merged_data[merged_data['MK'] <= -3]
ax.scatter(
    neg_subset.geometry.centroid.x,
    neg_subset.geometry.centroid.y,
    s=18,
    marker='_',
    color='black',
    linewidths=1.2
)


ax.set_axis_off()

# ======================
# ======================
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

cbar = plt.colorbar(
    sm, ax=ax,
    boundaries=boundaries,
    ticks=boundaries,
    spacing='proportional',
    shrink=0.6,
    aspect=48,
    pad=-0.01,
    orientation='horizontal',
    location='bottom'
)

# cbar.set_label('ΔFVC (% per year)', fontsize=16)
# cbar.set_label(r'HAF $\Delta$FVC ($\times 10^{-2}\ \mathrm{yr^{-1}}$)', fontsize=16)
cbar.set_label(r'HAF $\Delta$FVC (% yr$^{-1}$)', fontsize=18)

def smart_formatter(x, pos):
    if abs(x - round(x)) < 1e-6:
        return f"{x:.1f}"
    else:
        return f"{x:.1f}".rstrip('0')


cbar.ax.xaxis.set_major_formatter(FuncFormatter(smart_formatter))
cbar.ax.tick_params(labelsize=18)

# ======================
# ======================
ax2 = plt.axes([0.16, 0.36, 0.12, 0.24])

continent_data = merged_data.groupby('Continent')['VC'].apply(list).reset_index()
all_data = sum(continent_data['VC'], [])
continent_data = pd.concat(
    [continent_data, pd.DataFrame([{'Continent': 'WD', 'VC': all_data}])],
    ignore_index=True
)

continent_order = ['WD', 'SA', 'OC', 'NA', 'EU', 'AS', 'AF']
continent_data['Continent'] = pd.Categorical(
    continent_data['Continent'],
    categories=continent_order,
    ordered=True
)
continent_data = continent_data.sort_values('Continent')

box_colors = ['none', '#BEB8DC', '#82B0D2', '#8ECFC9',
              '#FA7F6F', '#E7DAD2', '#FFBE7A']

bp = ax2.boxplot(
    continent_data['VC'],
    labels=continent_data['Continent'],
    vert=False,
    patch_artist=True,
    showfliers=False
)

for patch, color in zip(bp['boxes'], box_colors):
    patch.set_facecolor(color)

for median in bp['medians']:
    median.set_color('black')

ax2.set_xlim(-0.6, 2.0)
ax2.set_xticks(np.arange(-0.6, 2.0, 0.6))

ax2.set_xticklabels(
    [f'{x:.1f}' for x in ax2.get_xticks()],
    rotation=90,
    fontsize=18
)
ax2.tick_params(axis='y', labelsize=18)
ax2.spines[['top', 'right']].set_visible(False)



# ======================
# ======================
plt.savefig('HAF_FVC.png', dpi=500, bbox_inches='tight')
plt.show()







# ======================
# Continent-level statistics (mean & median)
# ======================

# Ensure VC is numeric
merged_data['VC'] = pd.to_numeric(merged_data['VC'], errors='coerce')

continent_stats = (
    merged_data
    .groupby('Continent')
    .agg(
        mean_VC=('VC', 'mean'),                 
        median_VC=('VC', 'median'),            
        num_VC_gt_0=('VC', lambda x: (x > 0).sum()),  
        num_basins=('VC', 'count')              
    )
    .reset_index()
)

# World (WD) statistics
wd_stats = pd.DataFrame([{
    'Continent': 'WD',
    'mean_VC': merged_data['VC'].mean(),
    'median_VC': merged_data['VC'].median(),
    'num_VC_gt_0': (merged_data['VC'] > 0).sum(),
    'num_basins': merged_data['VC'].count()
}])

continent_stats = pd.concat([wd_stats, continent_stats], ignore_index=True)

# Order continents
continent_order = ['WD', 'SA', 'OC', 'NA', 'EU', 'AS', 'AF']
continent_stats['Continent'] = pd.Categorical(
    continent_stats['Continent'],
    categories=continent_order,
    ordered=True
)
continent_stats = continent_stats.sort_values('Continent')

# Print nicely
print('\nContinent-level VC statistics:')
print(
    continent_stats.to_string(
        index=False,
        formatters={
            'mean_VC': '{:.3f}'.format,
            'median_VC': '{:.3f}'.format
        }
    )
)


