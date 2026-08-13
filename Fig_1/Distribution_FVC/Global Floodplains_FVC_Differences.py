# -*- coding: utf-8 -*-
"""
HAF - HIF ΔFVC spatial pattern
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.ticker import FuncFormatter
import numpy as np

# ======================
# ======================
world_map = gpd.read_file('Data/wmoWorld/wmobb_basins.shp')
basin_map = gpd.read_file('Data/Basin91/Basin91.shp')

# ======================
# ======================
haf = pd.read_csv('Data/Veg/VC_HAF_nearest_interpolation.csv')
hif = pd.read_csv('Data/Veg/VC_HIF_nearest_interpolation.csv')

haf = haf[['newFID', 'VC', 'MK']].rename(
    columns={'VC': 'VC_HAF', 'MK': 'MK_HAF'}
)
hif = hif[['newFID', 'VC', 'MK']].rename(
    columns={'VC': 'VC_HIF', 'MK': 'MK_HIF'}
)

vc_data = haf.merge(hif, on='newFID', how='inner')
vc_data['VC_DIFF'] = vc_data['VC_HAF'] - vc_data['VC_HIF']

merged_data = basin_map.merge(vc_data, on='newFID', how='left')

# ======================
# ======================
colors = [
    "#FEC44F",  # -0.8 ~ -0.6
    "#FEE08B",  # -0.6 ~ -0.4
    "#FFF7BC",  # -0.4 ~ -0.2
    "#FFFFD4",  # -0.2 ~ 0
    "#E5F5E0",  # 0 ~ 0.2
    "#C7E9C0",  # 0.2 ~ 0.4
    "#74C476",  # 0.4 ~ 0.6
    "#238B45",  # 0.6 ~ 0.8
]

boundaries = np.arange(-0.8, 1.0, 0.2)
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N)

# ======================
# ======================
fig, ax = plt.subplots(figsize=(10, 6))

world_map.plot(ax=ax, color='lightgray', alpha=0.6)

merged_data.plot(
    column='VC_DIFF',
    cmap=cmap,
    norm=norm,
    ax=ax,
    linewidth=0.3,
    edgecolor='black'
)

# # ======================
# # ======================
# sig_subset = merged_data[
#     ((merged_data['MK_HAF'] >= 3) & (merged_data['MK_HIF'] >= 3)) |
#     ((merged_data['MK_HAF'] <= -3) & (merged_data['MK_HIF'] <= -3))
# ]

# ax.scatter(
#     sig_subset.geometry.centroid.x,
#     sig_subset.geometry.centroid.y,
#     s=8,
#     facecolors='none',
#     edgecolors='black',
#     linewidths=0.8
# )

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

cbar.set_label(r'[HAF $\Delta$FVC] - [HIF $\Delta$FVC] (% yr$^{-1}$)', fontsize=18)
cbar.ax.tick_params(labelsize=18)

def smart_formatter(x, pos):
    if abs(x) < 1e-6:
        return '0'
    return f'{x:.1f}'

cbar.ax.xaxis.set_major_formatter(FuncFormatter(smart_formatter))

# # ======================
# # ======================
# ax2 = plt.axes([0.16, 0.28, 0.18, 0.20])

# green_count = (merged_data['VC_DIFF'] > 0).sum()
# yellow_count = (merged_data['VC_DIFF'] < 0).sum()
# sizes = [green_count, yellow_count]

# ax2.pie(
#     sizes,
#     colors=['#238B45', '#FEC44F'],
#     startangle=90,
#     counterclock=False,
#     autopct=lambda p: f'{p:.0f}%',
#     textprops={'fontsize': 18}
# )

# ======================
# ======================
ax2 = plt.axes([0.14, 0.26, 0.22, 0.22])
ax2.set_facecolor('none')



vc_diff = merged_data['VC_DIFF'].dropna()
counts, _ = np.histogram(vc_diff, bins=boundaries)
percentages = counts / counts.sum() * 100


x = np.arange(len(percentages))

bars = ax2.bar(
    x,
    percentages,
    color=colors,
    width=0.9,
    edgecolor='black',
    linewidth=0.5
)

# ======================
# ======================
for bar, p in zip(bars, percentages):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f'{p:.0f}%',
        ha='center',
        va='bottom',
        fontsize=12
    )

# ======================
# ======================


ax2.set_xticks([])
ax2.set_yticks([])


ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(True)
ax2.spines['bottom'].set_visible(True)


# ax2.set_ylim(0, percentages.max() * 1.25)

# ======================
# ======================

ax2.annotate(
    '',
    xy=(1.02, 0),
    xytext=(0, 0),
    xycoords='axes fraction',
    arrowprops=dict(arrowstyle='->', linewidth=1.0)
)


ax2.annotate(
    '',
    xy=(0, 1.1),
    xytext=(0, 0),
    xycoords='axes fraction',
    arrowprops=dict(arrowstyle='->', linewidth=1.0)
)



# ======================
# ======================
plt.savefig('HAF_minus_HIF_FVC.png', dpi=500, bbox_inches='tight')
plt.show()
