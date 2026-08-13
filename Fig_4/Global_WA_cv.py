import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# 读取地图数据
world_boundary = gpd.read_file('Data/wmoWorld/World_Boundary.shp')
world_map = gpd.read_file('Data/wmoWorld/wmobb_basins.shp')
basin_map = gpd.read_file('Data/Basin91/Basin91.shp')

# 读取NDVI数据
ndvi_data = pd.read_csv('Data/WA/cv.csv', header=0)

# 合并地图数据和NDVI数据
merged_data = basin_map.merge(ndvi_data, on='newFID', how='left')

# 定义颜色和区间
colors = [
    "#7D1315", "#EB1D22", "#EF5E21", "#FBCD11",
    "#9ABCE4", "#3C6DB4", "#3752A4", "#252B80"
]
boundaries = [-4, -3, -2, -1, 0, 1, 2, 3, 4]  # 定义区间

# 创建颜色分区映射
cmap = ListedColormap(colors)
norm = BoundaryNorm(boundaries, cmap.N, clip=True)

# 绘制地图
fig, ax = plt.subplots(figsize=(8, 6))
world_boundary.boundary.plot(ax=ax, linewidth=0.2, color='#A6A6A6')  
world_map.plot(ax=ax, color='lightgray', alpha=0.5)
merged_data.plot(column='WA_cv', cmap=cmap, linewidth=0.3, ax=ax, edgecolor='white', norm=norm)

# 绘制小黑圆点
mk3_data = merged_data[abs(merged_data['MK']) == 3]
mk4_data = merged_data[abs(merged_data['MK']) == 4]
# ax.scatter(mk3_data.geometry.centroid.x, mk3_data.geometry.centroid.y, edgecolors='black', facecolors='none', linewidths=0.5, s=2.1, marker='o', label='p < 0.05')
ax.scatter(mk4_data.geometry.centroid.x, mk4_data.geometry.centroid.y, color='black', s=2.1, marker='o', label='p < 0.05')
ax.scatter(mk4_data.geometry.centroid.x, mk4_data.geometry.centroid.y, color='black', s=2.1, marker='o', label='p < 0.01')

# 添加标题和标签
ax.set_axis_off()

# # 创建颜色图例
# sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
# sm.set_array([])
# cbar = plt.colorbar(sm, ax=ax, spacing='proportional', shrink=0.6, aspect=48, pad=-0.01, orientation='horizontal', location='bottom')
# cbar.set_label('Trend in annual WA_cv')

# 创建颜色图例
# 创建颜色图例
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.25, aspect=10, pad=-0.02, location='left',anchor=(1.8, 0.45))
# cbar.set_label('Trend in annual WA_cv')
cbar.ax.tick_params(labelsize=10)  # 设置刻度标签字体大小
cbar.ax.text(
    0.5, -0.12, r'$\mathrm{\Delta RSA_{ave}\ (\%)}$',
    ha='center', va='top',
    fontsize=11,
    transform=cbar.ax.transAxes
)
# 调整布局，避免标签被遮挡
plt.tight_layout()

# 保存图像
plt.savefig('map_WA_cv.png', dpi=500, bbox_inches='tight')

# 显示地图
plt.show()
