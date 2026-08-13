import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import theilslopes, kendalltau

# =====================================================
# 1. Theil–Sen slope + p value
# =====================================================
def theil_sen_with_pvalue(df):
    x = df['Year'].values
    y = df['AreaWeightedMean'].values

    slope, _, _, _ = theilslopes(y, x)
    tau, p_value = kendalltau(x, y)

    return slope, p_value


# =====================================================
# =====================================================
haf_file = 'Annual_Mean_Stats_HAF_with_Interpolation.xlsx'
hif_file = 'Annual_Mean_Stats_HIF_with_Interpolation.xlsx'
basin_file = 'FVC_HAF_HIF_basin_average_trend.csv'

sheets = {
    'Low density': 'RVC_low_summary',
    'Moderate density': 'RVC_moderate_summary',
    'High density': 'RVC_high_summary'
}

haf_slopes, hif_slopes = [], []
haf_pvals, hif_pvals = [], []


# =====================================================
# =====================================================
for label, sheet in sheets.items():
    df_haf = pd.read_excel(haf_file, sheet_name=sheet)
    df_hif = pd.read_excel(hif_file, sheet_name=sheet)

    slope_haf, p_haf = theil_sen_with_pvalue(df_haf)
    slope_hif, p_hif = theil_sen_with_pvalue(df_hif)

    haf_slopes.append(slope_haf * 100)
    hif_slopes.append(slope_hif * 100)

    haf_pvals.append(p_haf)
    hif_pvals.append(p_hif)


# =====================================================
# =====================================================
df_basin = pd.read_csv(basin_file)

density_levels = ['low', 'moderate', 'high']
haf_ratio, hif_ratio = [], []

for d in density_levels:
    haf = df_basin[f'HAF_{d}']
    hif = df_basin[f'HIF_{d}']

    total = len(df_basin)

    # haf_ratio.append((haf > hif).sum() / total * 100)
    # hif_ratio.append((haf <= hif).sum() / total * 100)
    haf_ratio.append((haf > 0).sum() / total * 100)
    hif_ratio.append((hif > 0).sum() / total * 100)
    


# =====================================================
# =====================================================
labels = list(sheets.keys())
x = np.arange(len(labels))
width = 0.22


haf_color = '#1B9E77'  
hif_color = '#7FCDBB'   



group_spacing = 0.7
x = np.arange(len(labels)) * group_spacing


labels = ['Low\ndensity', 'Moderate\ndensity', 'High\ndensity']

fig, ax1 = plt.subplots(figsize=(8, 6))


bars_haf = ax1.bar(x - width/2, haf_slopes, width,
                   label='HAF', color=haf_color)

bars_hif = ax1.bar(x + width/2, hif_slopes, width,
                   label='HIF', color=hif_color)


ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=19, linespacing=1.1)
ax1.tick_params(axis='y', labelsize=19)

ax1.set_ylabel(r'Global average FVC trend (% yr$^{-1}$)', fontsize=19)

ax1.axhline(0, color='black', linewidth=0.8)


ax1.set_xlim(x[0] - 0.45, x[-1] + 0.45)



def signif_star(p):
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    else:
        return ''

y_star = 0.02 * max(abs(np.array(haf_slopes + hif_slopes)))

for i in range(len(labels)):
    s = signif_star(haf_pvals[i])
    if s:
        ax1.text(x[i] - width/2, y_star, s,
                 ha='center', va='bottom', fontsize=19)

    s = signif_star(hif_pvals[i])
    if s:
        ax1.text(x[i] + width/2, y_star, s,
                 ha='center', va='bottom', fontsize=19)
ax1.tick_params(axis='both', which='major', length=6, width=1)


ax2 = ax1.twinx()
ax2.set_ylim(0, 100)
ax2.set_ylabel('Increasing-FVC basin proportion (%)', fontsize=19)
ax2.tick_params(axis='y', labelsize=19)

for i in range(len(labels)):
    ax2.plot([x[i] - width/2, x[i] + width/2],
             [haf_ratio[i], hif_ratio[i]],
             color='black', linewidth=1, zorder=1)

ax2.scatter(x - width/2, haf_ratio, color='black',#haf_color,
            s=50, zorder=2)
ax2.scatter(x + width/2, hif_ratio, color='black',#hif_color,
            s=50, zorder=2)

ax2.tick_params(axis='both', which='major', length=6, width=1.2)

ax1.legend(fontsize=19, frameon=False, loc='upper left')
plt.savefig('FVC_Trend_Bar.png', dpi=500, bbox_inches='tight')
# plt.tight_layout()
plt.show()



print('Basin counts by density level:')
total = len(df_basin)
print(f'Total basins: {total}\n')

for d in density_levels:
    haf_inc = (df_basin[f'HAF_{d}'] > 0).sum()
    hif_inc = (df_basin[f'HIF_{d}'] > 0).sum()

    print(f'{d.capitalize()} density:')
    print(f'  HAF: {haf_inc} basins ({haf_inc/total*100:.1f}%)')
    print(f'  HIF: {hif_inc} basins ({hif_inc/total*100:.1f}%)')
    print('')
print('Global average FVC trend (Theil–Sen slope, % yr^-1):\n')

for i, label in enumerate(labels):
    print(f'{label}:')
    print(f'  HAF: {haf_slopes[i]:.3f} % yr^-1 (p = {haf_pvals[i]:.3g})')
    print(f'  HIF: {hif_slopes[i]:.3f} % yr^-1 (p = {hif_pvals[i]:.3g})')
    print('')
# =====================================================
# =====================================================

total = len(df_basin)


haf_all_inc = (
    (df_basin['HAF_low'] > 0) &
    (df_basin['HAF_moderate'] > 0) &
    (df_basin['HAF_high'] > 0)
)


hif_all_inc = (
    (df_basin['HIF_low'] > 0) &
    (df_basin['HIF_moderate'] > 0) &
    (df_basin['HIF_high'] > 0)
)

haf_all_count = haf_all_inc.sum()
hif_all_count = hif_all_inc.sum()

haf_all_ratio = haf_all_count / total * 100
hif_all_ratio = hif_all_count / total * 100


print('Basins with increasing FVC in ALL vegetation density levels:')
print(f'Total basins: {total}\n')

print('HAF:')
print(f'  Count: {haf_all_count}')
print(f'  Ratio: {haf_all_ratio:.1f}%\n')

print('HIF:')
print(f'  Count: {hif_all_count}')
print(f'  Ratio: {hif_all_ratio:.1f}%')

