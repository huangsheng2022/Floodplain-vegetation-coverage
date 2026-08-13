import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


plt.rcParams.update({
    'font.size': 22,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'axes.labelsize': 22,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
})


land_use_types = [
    'Cropland', 'Forest', 'Shrubland', 'Grassland', 'Tundra',
    'Wetland', 'Impervious_surface', 'Bare_areas', 'Water_body',
    'Permanent_snow_ice'
]


colors_nature = {
    'Cropland': '#91D1C2',
    'Forest': '#00A087',
    'Shrubland': '#F39B7F',
    'Grassland': '#3C5488',
    'Wetland': '#8491B4',
    'Bare_areas': '#E64B35',
    'Water_body': '#4DBBD5',
    'Tundra': '#BBBBBB',
    'Impervious_surface': '#BBBBBB',
    'Permanent_snow_ice': '#BBBBBB',

}

# =====================================================================
# =====================================================================
def process_with_weighted_sort_all_years(file_path):

    xls = pd.ExcelFile(file_path)
    sheets = xls.sheet_names

    df_list = []


    for sh in sheets:
        try:
            df = pd.read_excel(file_path, sheet_name=sh, index_col=0).T
            df_list.append(df)
        except:
            continue


    df_all = pd.concat(df_list, axis=0)


    df_mean = df_all.groupby(df_all.index).mean()


    total_area = df_mean['Total_Riparian_Area']


    proportions = df_mean[land_use_types].div(total_area, axis=0)


    weighted_means = (proportions.T @ total_area) / total_area.sum()
    sorted_types = weighted_means.sort_values(ascending=False).index.tolist()

    df_long = proportions.melt(var_name='Land Use Type', value_name='Proportion')
    df_long['Land Use Type'] = pd.Categorical(df_long['Land Use Type'], categories=sorted_types, ordered=True)

    return df_long, weighted_means


# =====================================================================
# =====================================================================
prop_mean, wmean_mean = process_with_weighted_sort_all_years('Area_all_years_km2.xlsx')

sorted_types = prop_mean['Land Use Type'].cat.categories.tolist()
prop_mean['Land Use Label'] = pd.Categorical(
    prop_mean['Land Use Type'],
    categories=sorted_types,
    ordered=True
)


fig, ax = plt.subplots(figsize=(10, 7))
palette = [colors_nature[typ] for typ in sorted_types]

sns.boxplot(
    x='Land Use Label', y='Proportion', data=prop_mean, ax=ax,
    palette=palette, showfliers=False, width=0.6,
    boxprops=dict(linewidth=1),
    whiskerprops=dict(linewidth=1),
    capprops=dict(linewidth=0),
    medianprops=dict(color='black', linewidth=2)
)

vegetated_types = ['Cropland', 'Forest', 'Shrubland', 'Grassland', 'Tundra', 'Wetland']
color_green = '#00A087'
color_orange = '#E64B35'

for i, land_use in enumerate(sorted_types):
    whiskers_for_box = [line for line in ax.lines if abs(line.get_xdata().mean() - i) < 0.01]
    if whiskers_for_box:
        y_whisker_top = max(line.get_ydata().max() for line in whiskers_for_box)
        text_color = color_green if land_use in vegetated_types else color_orange
        x_pos = i + 0.1 if land_use == 'Cropland' else i
        ax.text(
            x_pos, y_whisker_top + 0.02,
            f"{wmean_mean[land_use]*100:.1f}%",
            ha='center', va='bottom',
            fontsize=16,  fontweight='bold',color=text_color
        )#




for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1)
    spine.set_edgecolor('black')

ax.set_ylim(0, 1)
ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_title('')
ax.set_xlabel('')
ax.set_ylabel('HIF composition (%)')

for label in ax.get_xticklabels():
    label.set_rotation(45)
    label.set_rotation_mode("anchor")
    label.set_ha("right")#center
    label.set_va("top")
    label.set_x(label.get_position()[0] + 0.1)

max_whisker_y = max([line.get_ydata().max() for line in ax.lines])
# ax.set_ylim(0, max_whisker_y + 0.1)
ax.set_ylim(0, max(1.0, max_whisker_y + 0.1))


import matplotlib.ticker as mticker
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y*100:.0f}"))


plt.tight_layout()
plt.savefig('box-plot_land_use_proportion_ALL_YEARS_AVG_HIF.png', dpi=300, bbox_inches='tight')
plt.show()
