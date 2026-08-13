# -*- coding: utf-8 -*-
"""
Created on Mon Dec 29 19:35:33 2025
@author: Huang Sheng
"""

import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import theilslopes, kendalltau

# ==============================
# File paths
# ==============================
file_hif = "Annual_Mean_Stats_HIF_with_Interpolation.xlsx"
file_haf = "Annual_Mean_Stats_HAF_with_Interpolation.xlsx"

variables = [
    ("FVC", "RVC_summary"),
    ("FNDVI", "RNDVI_summary")
]

# ==============================
# Plot settings
# ==============================
fig, ax = plt.subplots(figsize=(10, 6))

legend_fvc = []
legend_fndvi = []

# ==============================
# Loop through variables
# ==============================
for var, sheet in variables:

    df_hif = pd.read_excel(file_hif, sheet_name=sheet)
    df_haf = pd.read_excel(file_haf, sheet_name=sheet)

    year = df_hif["Year"]
    mean_hif = df_hif["AreaWeightedMean"]
    mean_haf = df_haf["AreaWeightedMean"]#SimpleMean
    # mean_hif = df_hif["SimpleMean"]
    # mean_haf = df_haf["SimpleMean"]#SimpleMean    

    # ==============================
    # Theil–Sen slope (original units)
    # ==============================
    slope_hif, intercept_hif, _, _ = theilslopes(mean_hif, year)
    slope_haf, intercept_haf, _, _ = theilslopes(mean_haf, year)

    # Kendall tau p-values
    _, p_hif = kendalltau(year, mean_hif)
    _, p_haf = kendalltau(year, mean_haf)

    # Trend lines (original scale)
    trend_hif = intercept_hif + slope_hif * year
    trend_haf = intercept_haf + slope_haf * year

    # ==============================
    # Style & units
    # ==============================
    # 情景配色（统一）
    if var == "FVC":
        color_haf = "#1B7837"     
        color_hif = "#5AAE61"    
        linestyle_main = "-"      
        unit = "%"
        slope_scale = 100
        legend_list = legend_fvc
    
    else:  # FNDVI
        color_haf = "#E08214"     
        color_hif = "#DFC27D"     
        linestyle_main = "-."     
        unit = r"$\times 10^{-2}$"
        slope_scale = 1e2
        legend_list = legend_fndvi





    # ==============================
    # Main lines
    # ==============================
    line1, = ax.plot(year, mean_hif, color=color_hif, linewidth=2.8)
    line2, = ax.plot(year, mean_haf, color=color_haf, linewidth=2.8)

    # Trend lines
    ax.plot(year, trend_hif, "--", color=color_hif, linewidth=1.5)
    ax.plot(year, trend_haf, "--", color=color_haf, linewidth=1.5)

    # ==============================
    # Legend text
    # ==============================
    legend_list.append(
        (
            line1,
            f"{var}-HIF (slope={slope_hif * slope_scale:.2f}{unit}, p={p_hif:.2f})"
        )
    )

    legend_list.append(
        (
            line2,
            f"{var}-HAF (slope={slope_haf * slope_scale:.2f}{unit}, p={p_haf:.2f})"
        )
    )

# ==============================
# Axis settings
# ==============================
ax.set_ylabel("FVC & FNDVI", fontsize=24)

ax.set_ylim(0.3, 1.0)
ax.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

ax.tick_params(
    axis="both",
    which="major",
    direction="out",
    length=8,
    width=1,
    labelsize=24,
    top=False,
    right=False
)

# Black frame
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color("black")
    spine.set_linewidth(1)

# ==============================
# Two separate legends
# ==============================
handles_fvc, labels_fvc = zip(*legend_fvc)
handles_fndvi, labels_fndvi = zip(*legend_fndvi)

leg1 = ax.legend(
    handles_fvc, labels_fvc,
    loc="upper left",
    frameon=False,
    fontsize=22
)
ax.add_artist(leg1)

ax.legend(
    handles_fndvi, labels_fndvi,
    loc="center right",
    bbox_to_anchor=(1.0, 0.37),  
    frameon=False,
    fontsize=22
)

plt.tight_layout()
plt.savefig('HAF_FVC_Global_Mean.png', dpi=500, bbox_inches='tight')
plt.show()
