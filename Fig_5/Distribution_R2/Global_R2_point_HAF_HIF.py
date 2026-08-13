import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import seaborn as sns

# 读取地图数据
world_boundary = gpd.read_file('Data/wmoWorld/World_Boundary.shp')
world_map = gpd.read_file('Data/wmoWorld/wmobb_basins.shp')
basin_map = gpd.read_file('Data/Basin91/Basin91.shp')
# 读取R2数据
R2_data = pd.read_csv('Data/R2/r2_HAF.csv', header=0)
# 合并地图数据和R2数据
merged_data = basin_map.merge(R2_data, on='newFID', how='left')

# 定义颜色映射
colors = ["#8C85A9", "#B29EBC", "#D6B9D0", "#F8D6E5", '#B3CDE4', '#78A3CC', "#3C79B4","#2F5D99"]##3752A4
boundaries = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
cmap = ListedColormap(colors, N=len(colors))
norm = BoundaryNorm(boundaries, cmap.N)

# 绘制地图
fig, ax = plt.subplots(figsize=(10, 6))
world_boundary.boundary.plot(ax=ax, linewidth=0.2, color='#A6A6A6')
world_map.plot(ax=ax, color='lightgray', alpha=0.5)
merged_data.plot(column='R2', cmap=cmap, linewidth=0.3, ax=ax, edgecolor='white', norm=norm)

# 绘制点
mk1_data = merged_data[(abs(merged_data['p_CO2']) < 0.05)]
mk2_data = merged_data[(abs(merged_data['p_RSA']) < 0.05)]
ax.scatter(
    mk1_data.geometry.centroid.x,
    mk1_data.geometry.centroid.y,
    edgecolors='black',
    facecolors='none',
    linewidths=0.8,
    s=20,
    marker='o',
    label=r"$p[CO_2] < 0.05$"  # 使用Tex表达式将2变为下标
)

ax.scatter(
    mk2_data.geometry.centroid.x,
    mk2_data.geometry.centroid.y,
    color='black',
    linewidths=0.8,
    s=20,
    marker='x',
    label=r"$p[RSA] < 0.05$" 
)




# 添加图例，调整位置
ax.legend(loc='lower left', bbox_to_anchor=(0.36, -0.036), fontsize=13, ncol=2,labelspacing=1 )

# 添加标题和标签
ax.set_axis_off()

# 创建颜色图例
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, boundaries=boundaries, ticks=boundaries, spacing='proportional', shrink=0.6, aspect=48, pad=0.02, orientation='horizontal', location='bottom')
cbar.set_label(r'HAF $\mathrm{R}^2$', fontsize=15)
cbar.ax.tick_params(labelsize=14)  # 设置刻度字体大小为12



# #############################################################纵向箱线图+WD
# # # 左下角绘制箱线图 (B图)
ax2 = plt.axes([0.16, 0.32, 0.12, 0.24])  # 调整位置和大小:创建一个位于整个图形的相对位置为(0.16, 0.32)，并具有宽度为0.12，高度为0.24的坐标轴
continent_data = merged_data.groupby('Continent')['R2'].apply(list).reset_index(name='R2')
# 将所有大洲的R2数据合并
all_data = continent_data['R2'].sum()

new_row = pd.DataFrame([{'Continent': 'WD', 'R2': all_data}])
continent_data = pd.concat([continent_data, new_row], ignore_index=True)


colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#BEB8DC', '#E7DAD2']  # 设置不同大洲的颜色，最后一个颜色为"WD"

# 仅保留大洲数据（去掉"WD"）
continent_data = continent_data[continent_data['Continent'] != 'WD']



# 按指定顺序排序continent_data
continent_order = ['SA','OC','NA','EU','AS','AF']
continent_data['Continent'] = pd.Categorical(continent_data['Continent'], categories=continent_order, ordered=True)
continent_data = continent_data.sort_values('Continent')
# 为每个大洲设置箱线图的颜色
boxplot_patches = ax2.boxplot(continent_data['R2'], labels=continent_data['Continent'], patch_artist=True, vert=False)
for patch, color in zip(boxplot_patches['boxes'], colors):
    patch.set_facecolor(color)
# 修改箱线图中间的横线颜色为黑色
for line in boxplot_patches['medians']:
    line.set_color('black')
# 修改纵坐标刻度为0.1为单位
plt.xticks([i * 0.2 for i in range(0, 5)])
# 设置ax2横坐标标签竖着显示，并保留小数点后一位数字
ax2.set_xticklabels([f'{label:.1f}' for label in ax2.get_xticks()], rotation=90, fontsize=15)#, rotation=90
# 去除图框线
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.tick_params(axis='y', labelsize=15)  # 设置 y 轴（大洲标签）字体大小为 14





# 保存图像
plt.savefig('map_image_R2_HAF.png', dpi=500, bbox_inches='tight')
# 显示地图
plt.show()
