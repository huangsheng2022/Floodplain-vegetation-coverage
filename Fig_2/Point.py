import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# =====================================================
# =====================================================
basin_file = 'FVC_HAF_HIF_basin_average_trend.csv'
df = pd.read_csv(basin_file)

total_basins = len(df)

# =====================================================
# =====================================================
# density_colors = {
#     1: '#C7E9C0',  # low
#     2: '#74C476',  # moderate
#     3: '#238B45'   # high
# }
density_colors = {
    1: '#E0F3DB',  
    2: '#74C476',  
    3: '#236B4D'   
}


markers = {
    'HAF': '^',
    'HIF': 's'
}

# =====================================================
# =====================================================
results = []

for system in ['HAF', 'HIF']:
    dom_col = f'{system}_Dominant'
    fvc_col = f'{system}_FVC'

    for d in [1, 2, 3]:
        sub = df[df[dom_col] == d]
        if sub.empty:
            continue

        results.append({
            'System': system,
            'Type': d,
            'Mean': sub[fvc_col].mean(),
            'Std':  sub[fvc_col].std(),
            'Ratio': len(sub) / total_basins * 100
        })

df_plot = pd.DataFrame(results)

# =====================================================
# =====================================================
fig, ax = plt.subplots(figsize=(9, 6))

for system in ['HAF', 'HIF']:
    df_sys = df_plot[df_plot['System'] == system]

    for _, row in df_sys.iterrows():
        ax.errorbar(
            row['Ratio'],
            row['Mean'],
            yerr=row['Std'],
            fmt=markers[system],
            markersize=18,                
            markerfacecolor=density_colors[row['Type']],
            markeredgecolor='black',
            markeredgewidth=0.8,          
            ecolor='black',
            elinewidth=1.2,
            capsize=4,
            linestyle='none',
            zorder=3
        )

        ax.plot(
            df_sys['Ratio'],
            df_sys['Mean'],
            linestyle='--',
            color='black',
            linewidth=1,
            zorder=1
        )
# =====================================================
# =====================================================
ax.set_xlabel('Basin proportion by dominant vegetation types (%)', fontsize=20)
ax.set_ylabel(r'Average FVC trend (% yr$^{-1}$)', fontsize=20)

ax.tick_params(axis='both', which='major',
               labelsize=20, length=6, width=1.2)

# ax.axhline(0, color='black', linewidth=0.8)

for spine in ax.spines.values():
    spine.set_linewidth(1.2)

# =====================================================
# =====================================================
legend_elements = [
    Line2D([0], [0], marker='^', color='none',
           markerfacecolor=density_colors[1], markeredgecolor='black',
           markersize=16, label='HAF low'),
    Line2D([0], [0], marker='^', color='none',
           markerfacecolor=density_colors[2], markeredgecolor='black',
           markersize=16, label='HAF moderate'),
    Line2D([0], [0], marker='^', color='none',
           markerfacecolor=density_colors[3], markeredgecolor='black',
           markersize=16, label='HAF high'),

    Line2D([0], [0], marker='s', color='none',
           markerfacecolor=density_colors[1], markeredgecolor='black',
           markersize=16, label='HIF low'),
    Line2D([0], [0], marker='s', color='none',
           markerfacecolor=density_colors[2], markeredgecolor='black',
           markersize=16, label='HIF moderate'),
    Line2D([0], [0], marker='s', color='none',
           markerfacecolor=density_colors[3], markeredgecolor='black',
           markersize=16, label='HIF high'),
]

ax.legend(
    handles=legend_elements,
    loc='upper left',
    ncol=2,
    frameon=False,
    fontsize=19,
    columnspacing=0.8,
    handletextpad=0.4  
)

plt.savefig('Point.png', dpi=500, bbox_inches='tight')
# plt.tight_layout()
plt.show()


print('Scatter point data (used in Point.png):\n')
print('System\tDensity\tBasin_ratio(%)\tMean_FVC_trend(%/yr)\tStd\tN')

for _, row in df_plot.iterrows():
    n = int(round(row['Ratio'] / 100 * total_basins))
    density = {1: 'Low', 2: 'Moderate', 3: 'High'}[row['Type']]

    print(f"{row['System']}\t{density}\t"
          f"{row['Ratio']:.2f}\t"
          f"{row['Mean']:.3f}\t"
          f"{row['Std']:.3f}\t"
          f"{n}")
