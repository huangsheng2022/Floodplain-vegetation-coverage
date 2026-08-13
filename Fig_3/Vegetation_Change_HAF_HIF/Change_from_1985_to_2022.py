import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({
    'font.size': 22,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'axes.labelsize': 22,
    'xtick.major.size': 2,
    'ytick.major.size': 2,
    'xtick.major.width': 1,
    'ytick.major.width': 1,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
})


selected_land_use_types = [ 
    'Cropland', 'Forest', 'Shrubland', 'Grassland', 
    'Wetland', 'Bare_areas', 'Water_body'
]


def read_data(fname):
    df85 = pd.read_excel(fname, sheet_name='1985', index_col=0).T
    df22 = pd.read_excel(fname, sheet_name='2022', index_col=0).T
    return df85, df22

df_1985, df_2022 = read_data('Area_all_years_km2_HAF.xlsx')



total_1985 = df_1985['Total_Riparian_Area']
total_2022 = df_2022['Total_Riparian_Area']


proportion_1985 = df_1985.div(total_1985, axis=0)
proportion_2022 = df_2022.div(total_2022, axis=0)


change = (proportion_2022[selected_land_use_types] - proportion_1985[selected_land_use_types]) * 100




remaining_types = [col for col in df_1985.columns if col not in selected_land_use_types + ['Total_Riparian_Area']]
change['Others'] = (
    proportion_2022[remaining_types].sum(axis=1)
    - proportion_1985[remaining_types].sum(axis=1)
) * 100


all_types = selected_land_use_types + ['Others']


colors_nature = {
    'Cropland': '#91D1C2',
    'Forest': '#00A087',
    'Shrubland': '#F39B7F',
    'Grassland': '#3C5488',
    'Wetland': '#8491B4',
    'Bare_areas': '#E64B35',
    'Water_body': '#4DBBD5',
    'Others': '#BBBBBB'
}
color_map = {lu: colors_nature[lu] for lu in all_types}

fig, ax = plt.subplots(figsize=(10, 7))
x = np.arange(1, 92)
bottom_positive = np.zeros(len(x))
bottom_negative = np.zeros(len(x))

for land_use in all_types:
    values = change[land_use].values
    positive = np.where(values > 0, values, 0)
    negative = np.where(values < 0, values, 0)

    ax.bar(x, positive, bottom=bottom_positive, color=color_map[land_use], label=land_use)
    ax.bar(x, negative, bottom=bottom_negative, color=color_map[land_use])
    
    bottom_positive += positive
    bottom_negative += negative

ax.legend(
    fontsize=20,
    title_fontsize=20,
    loc='upper left',
    ncol=2,
    columnspacing=0.2,   
    labelspacing=0.2,   
    borderpad=0.2,      
    handletextpad=0.6  
    
)


ax.axhline(0, color='black', linewidth=1)
ax.set_xlabel('Basin')
ax.set_ylabel('HAF composition change (%)')
ax.set_xticks(np.arange(1, 92, 10))
ax.set_yticks(np.arange(-100, 101, 20))
ax.set_xlim(0.5, 91.5)
ax.tick_params(axis='both', which='major', length=6, width=1.2, direction='out')
plt.tight_layout()
plt.savefig('Land_use_change_basins_updated.png', dpi=500, bbox_inches='tight')
plt.show()

