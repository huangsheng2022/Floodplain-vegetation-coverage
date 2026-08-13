import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 读取数据
file_path = 'Data_PC.xlsx'
data = pd.read_excel(file_path,sheet_name='HAF')

# 列与颜色
columns_to_plot = ['CO2', 'RSA', 'VPD', 'TEMP', 'PREC', 'SRAD']
colors = ['#ED7D31', '#0084A8', '#7F7F7F', '#C00000', '#4A7EBB', '#6A4C9C']
p_values= ['p_CO2',	'p_RSA','p_VPD','p_TEMP','p_PREC','p_SRAD']

# 标签映射
label_map = {'CO2': 'CO$_2$', 'RSA': 'RSA', 'VPD': 'VPD', 'TEMP': 'TEMP', 'PREC': 'PREC', 'SRAD': 'SRAD'}
data_melted = pd.melt(data, value_vars=columns_to_plot, var_name='Metrics', value_name='Values')
data_melted['Metrics'] = data_melted['Metrics'].map(label_map)

# 绘图准备
sns.set_theme(style="white")
plt.figure(figsize=(10, 5))
ax = plt.gca()

# 小提琴图：使用你给的 colors
sns.violinplot(x='Metrics', y='Values', data=data_melted,
               palette=colors, inner=None, linewidth=1.2, alpha=0.6, ax=ax)

# 黑色箱线图叠加（在最上层）
sns.boxplot(x='Metrics', y='Values', data=data_melted, ax=ax,
            whis=1.5, width=0.1, showcaps=True, showfliers=False,
            boxprops={'facecolor': 'None', 'edgecolor': 'black', 'linewidth': 1.4},
            whiskerprops={'color': 'black', 'linewidth': 1.4},
            capprops={'color': 'black', 'linewidth': 1.4},
            medianprops={'color': 'black', 'linewidth': 1.4})



# 构建显著性散点数据集
significant_points = pd.DataFrame()

for col, p_col in zip(columns_to_plot, p_values):
    # 判断该列 p 值是否 < 0.05，提取对应的数据
    sig_data = data[[col, p_col]].copy()
    sig_data = sig_data[sig_data[p_col] < 0.05]
    sig_data['Metrics'] = label_map[col]
    sig_data = sig_data.rename(columns={col: 'Values'})
    significant_points = pd.concat([significant_points, sig_data[['Metrics', 'Values']]], axis=0)

# 只画显著点的散点图
sns.stripplot(x='Metrics', y='Values', data=significant_points,
              jitter=0.3, marker='v', facecolor='none', edgecolor='black',
              linewidth=1.5, alpha=0.5, size=10, ax=ax)


# 添加 y=0 虚线
ax.axhline(0, ls='--', lw=1.2, color='black')

# 字体 & 坐标轴美化
ax.set_ylabel('HAF path coefficients', fontsize=22)
ax.set_xlabel('')
ax.set_ylim(-1.6, 1.6)
ax.set_yticklabels([f"{tick:.1f}" for tick in ax.get_yticks()], fontsize=20)
ax.set_xticklabels(ax.get_xticklabels(), fontsize=20)

# 外刻度线
ax.tick_params(axis='both', which='both', direction='out', length=6, width=1.2, colors='black')

# 去边框白边
ax.patch.set_edgecolor('black')
ax.patch.set_linewidth(1.1)

# === 只保留左 & 下外刻度线 ===
ax.tick_params(
    axis='both',
    which='both',
    direction='out',
    bottom=True, top=False,
    left=True, right=False,
    length=6, width=1.2
)

ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_linewidth(1.2)
ax.spines['bottom'].set_linewidth(1.2)




plt.tight_layout()
plt.savefig('PC_violin_HAF.png', dpi=350, bbox_inches='tight')
plt.show()
