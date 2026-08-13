# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 23:57:03 2024

@author: Huang Sheng
"""

import pandas as pd
import numpy as np

# 读取 Excel 数据
file_path = 'Data.xlsx'
sheet_name='2For_alluvial'
df = pd.read_excel(file_path,sheet_name)

# 区间定义
bins = [0, 0.2, 0.4, 0.6, 0.8, 1]
labels = ['A', 'B', 'C', 'D', 'E']

# 分组函数，处理左闭右开的区间以及最后一个区间的右闭
def categorize(value):
    # 处理值是否在定义的范围内
    if value < bins[0] or value > bins[-1]:
        return 'F'  # 或者其他适当的处理

    # 使用 np.digitize 并调整索引
    index = np.digitize([value], bins, right=False)[0]
    
    # 确保最后一个区间（右边界闭合）
    if value == bins[-1]:
        index -= 1

    return labels[index - 1] if index > 0 else labels[0]


df['Year1990_cat'] = df['Year1990'].apply(categorize)
df['Year2000_cat'] = df['Year2000'].apply(categorize)
df['Year2010_cat'] = df['Year2010'].apply(categorize)
df['Year2020_cat'] = df['Year2020'].apply(categorize)

# 计算转换情况的函数
def calculate_transitions(df, year1, year2):
    counts = pd.DataFrame(index=labels, columns=labels).fillna(0)
    for cat1 in labels:
        for cat2 in labels:
            counts.at[cat1, cat2] = ((df[f'{year1}_cat'] == cat1) & (df[f'{year2}_cat'] == cat2)).sum()
    return counts

# 计算各年份之间的转换情况
transitions_90_to_00 = calculate_transitions(df, 'Year1990', 'Year2000')
transitions_00_to_10 = calculate_transitions(df, 'Year2000', 'Year2010')
transitions_10_to_20 = calculate_transitions(df, 'Year2010', 'Year2020')

# 打印结果
print("1990年到2000年各分类的转换情况:")
print(transitions_90_to_00)
print("\n2000年到2010年各分类的转换情况:")
print(transitions_00_to_10)
print("\n2010年到2020年各分类的转换情况:")
print(transitions_10_to_20)



# 保存结果到 TXT 文件
def save_transitions_to_txt(transitions_list, file_name):
    zero_count = 0
    with open(file_name, 'w') as f:
        for year1, year2, transitions in transitions_list:
            for cat1 in labels:
                for cat2 in labels:
                    count = transitions.at[cat1, cat2]
                    if count > 0:  # 只写入有转换的情况
                        f.write(f"{cat1}{year1}s,{cat2}{year2}s,{int(count)}\n")
                    else:
                        zero_count += 1
    return zero_count

# 文件名
file_name = 'transitions.txt'

# 组合各年份间的转换情况
transitions_list = [
    ('1990', '2000', transitions_90_to_00),
    ('2000', '2010', transitions_00_to_10),
    ('2010', '2020', transitions_10_to_20)
]

# 保存各年份之间的转换情况到 TXT 文件，并统计转换个数为0的记录数量
zero_count = save_transitions_to_txt(transitions_list, file_name)

print(f"转换情况已保存到 {file_name}")
print(f"转换个数为0的记录数量: {zero_count}")


