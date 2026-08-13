import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ======================================
# ======================================
df = pd.read_csv('FVC_HAF_HIF_basin_average_trend.csv')

# ======================================
# ======================================
df['FVC_diff'] = df['HAF_FVC'] - df['HIF_FVC']
df_sorted = df.sort_values(by='FVC_diff', ascending=False).reset_index(drop=True)


basins = np.arange(1, len(df_sorted) + 1)

# ======================================
# ======================================
diff_low = df_sorted['HAF_low'] - df_sorted['HIF_low']
diff_mod = df_sorted['HAF_moderate'] - df_sorted['HIF_moderate']
diff_high = df_sorted['HAF_high'] - df_sorted['HIF_high']


heatmap_data = np.vstack([
    diff_low.values,
    diff_mod.values,
    diff_high.values
])

# ======================================
# ======================================
cmap = LinearSegmentedColormap.from_list(
    'orange_white_green',
    ['#E69F00', '#FFFFFF', '#009E73'],
    N=256
)

# ======================================
# ======================================
fig, ax = plt.subplots(figsize=(18, 4))


x_edges = np.arange(heatmap_data.shape[1] + 1)
y_edges = np.arange(heatmap_data.shape[0] + 1)

im = ax.pcolormesh(
    x_edges,
    y_edges,
    heatmap_data,
    cmap=cmap,
    vmin=-0.2,
    vmax=0.2,
    edgecolors='black',
    linewidth=0.1
)

ax.invert_yaxis()  

# ======================================
# ======================================
ax.set_xticks(np.arange(0.5, len(basins), 10))
ax.set_xticklabels(np.arange(1, len(basins) + 1, 10), fontsize=21)

ax.set_yticks([0.5, 1.5, 2.5])
ax.set_yticklabels(
    ['Low density', 'Moderate density', 'High density'],
    fontsize=21
)

ax.set_xlabel(
    'Basins (ordered left to right by overall FVC trend difference between HAF and HIF)',
    fontsize=21
)
ax.tick_params(axis='both', which='major', length=6, width=1.2)

# ======================================
# ======================================
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label(
    'FVC trend difference\n(HAF − HIF)',
    fontsize=21
)
cbar.ax.tick_params(labelsize=21)
plt.savefig('Heatmep.png', dpi=500, bbox_inches='tight')
plt.tight_layout()
plt.show()


count_all_positive = (
    (df['HAF_low'] - df['HIF_low'] > 0) &
    (df['HAF_moderate'] - df['HIF_moderate'] > 0) &
    (df['HAF_high'] - df['HIF_high'] > 0)
).sum()

print(f'Basins with positive HAF−HIF trends in all three density classes: {count_all_positive}')
