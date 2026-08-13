import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Input excel file
excel_file = "Riparian_LandCover_byYear.xlsx"

# Land-cover groups
vegetated = [
    "Cropland", "Forest", "Shrubland", "Grassland",
    "Tundra", "Wetland"
]

unvegetated = [
    "Impervious_surface", "Bare_areas", "Water_body",
    "Permanent_snow_ice", "Filled_value"
]

total_area_class = "Total_Riparian_Area"

# Read sheets
xls = pd.ExcelFile(excel_file)
years = sorted([int(s) for s in xls.sheet_names])

records = []  # store global statistics
std_records = []  # store std for each year

for yr in years:
    df = pd.read_excel(excel_file, sheet_name=str(yr))

    df = df.rename(columns={df.columns[0]: "Class"})  # class-column name may vary

    # Extract basin columns
    basin_cols = df.columns[1:]

    # ---- Compute totals across all basins ----
    df["Total"] = df.iloc[:, 1:].sum(axis=1)

    total_veg_global = df.loc[df["Class"].isin(vegetated), "Total"].sum()
    total_unveg_global = df.loc[df["Class"].isin(unvegetated), "Total"].sum()
    total_rip_global = df.loc[df["Class"] == total_area_class, "Total"].values[0]

    veg_prop_global = (total_veg_global / total_rip_global
                       if total_rip_global != 0 else np.nan)

    # ---- Basin-level vegetated proportion ----
    # For each basin:
    # (sum vegetated classes) / (total riparian area)
    basin_veg_prop = []

    for b in basin_cols:
        basin_total_rip = df.loc[df["Class"] == total_area_class, b].values[0]
        basin_veg = df.loc[df["Class"].isin(vegetated), b].sum()

        if basin_total_rip > 0:
            basin_veg_prop.append(basin_veg / basin_total_rip)
        else:
            basin_veg_prop.append(np.nan)

    # Standard deviation across basins
    veg_prop_std = np.nanstd(basin_veg_prop)

    # Store global results
    records.append([
        yr, total_veg_global, total_unveg_global,
        total_rip_global, veg_prop_global, veg_prop_std
    ])


# Convert to dataframe
results = pd.DataFrame(records, columns=[
    "Year", "Total_Vegetated", "Total_Unvegetated",
    "Total_Riparian_Area", "Vegetated_Proportion",
    "Vegetated_Proportion_Std"
])






results["Vegetated_Proportion_pct"] = results["Vegetated_Proportion"] * 100
results["Vegetated_Proportion_Std_pct"] = results["Vegetated_Proportion_Std"] * 100



# ---- Plot with shaded lower-std area ----
plt.figure(figsize=(10, 7))


line_color = '#00A087'   
fill_color = '#00A087'


plt.plot(
    results["Year"],
    results["Vegetated_Proportion_pct"],
    label="Vegetated proportion",
    marker="o",
    markersize=10,
    markerfacecolor='white',     
    markeredgecolor=line_color,  
    markeredgewidth=2,  
    color=line_color,
    linewidth=2
)


upper = results["Vegetated_Proportion_pct"] #+ results["Vegetated_Proportion_Std_pct"]
lower = results["Vegetated_Proportion_pct"] - results["Vegetated_Proportion_Std_pct"]
plt.fill_between(
    results["Year"],
    lower,
    upper,
    alpha=0.25,
    color=fill_color
)



max_idx = results["Vegetated_Proportion_pct"].idxmax()
min_idx = results["Vegetated_Proportion_pct"].idxmin()

max_year = results.loc[max_idx, "Year"]
max_val = results.loc[max_idx, "Vegetated_Proportion_pct"]

min_year = results.loc[min_idx, "Year"]
min_val = results.loc[min_idx, "Vegetated_Proportion_pct"]


plt.scatter(max_year, max_val, color="black", s=100, zorder=3)
plt.text(
    max_year, max_val + 2,
    f"Max: {max_val:.1f}%",
    color="black", fontsize=22, ha="center"
)


plt.scatter(min_year, min_val, color="black", s=100, zorder=3)
plt.text(
    min_year, min_val - 4,
    f"Min: {min_val:.1f}%",
    color="black", fontsize=22, ha="center"
)






plt.ylim(50, 100)


plt.axhline(90, color="black", linestyle="--", linewidth=1)


plt.xticks(fontsize=22)
plt.yticks(fontsize=22)

plt.ylabel("Classification agreement (%)", fontsize=22)
plt.xlabel("Year", fontsize=22)



text_left = (
    "Vegetated Land Cover:\n"
    "  • Cropland\n"
    "  • Wetland\n"
    "  • Forest\n"
    "  • Grassland\n"
    "  • Shrubland\n"
    "  • Tundra"
)


text_right = (
    "Non-vegetated Land Cover:\n"
    "  • Water_body\n"
    "  • Bare_areas\n"
    "  • Impervious_surface\n"
    "  • Permanent_snow_ice"
)

color_green = '#00A087'
color_orange = 'orange'


plt.text(
    0.02, 0.02,
    text_left,
    ha="left", va="bottom",
    fontsize=20,color=color_green,
    transform=plt.gca().transAxes
)


plt.text(
    0.52, 0.02,
    text_right,
    ha="left", va="bottom",
    fontsize=20,color=color_orange,
    transform=plt.gca().transAxes
)

plt.tight_layout()
plt.tick_params(axis='both', which='major', length=6, width=1.2, direction='out')
plt.savefig("vegetetaed accuracy.png", dpi=300)
plt.show()






# ---- Write output TXT ----
output_txt = "Riparian_global_statistics.txt"
with open(output_txt, "w") as f:
    f.write("Year\tTotal_Vegetated\tTotal_Unvegetated\tTotal_Riparian_Area\t"
            "Vegetated_Proportion\tVegetated_Proportion_STD\n")

    for _, row in results.iterrows():
        f.write(f"{row['Year']}\t"
                f"{row['Total_Vegetated']:.6f}\t"
                f"{row['Total_Unvegetated']:.6f}\t"
                f"{row['Total_Riparian_Area']:.6f}\t"
                f"{row['Vegetated_Proportion']:.6f}\t"
                f"{row['Vegetated_Proportion_Std']:.6f}\n")

print("All processing complete!")
print("TXT file saved as:", output_txt)
