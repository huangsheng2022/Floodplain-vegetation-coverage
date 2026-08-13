% 第一步：读取水面积数据（37年 x 91个流域）
water_data = xlsread('Results_Zscore_WATER.xlsx', 'mean');  % 37x91

% 第二步：对每个流域进行最小-最大归一化
% 初始化归一化后的矩阵
normalized_data = zeros(size(water_data));  % 37x91

for i = 1:size(water_data, 2)  % 对每一列（每个流域）归一化
    col = water_data(:, i);
    min_val = min(col);
    max_val = max(col);
    if max_val > min_val
        normalized_data(:, i) = (col - min_val) / (max_val - min_val);
    else
        % 若最大最小值相同，则说明没有波动，设为0（或1都可以）
        normalized_data(:, i) = 0;
    end
end

% 第三步：定义每行对应的年份
years = (1985:2021)';

% 创建每个年代的掩码
decades = {
    '1990s', years >= 1990 & years <= 1999;
    '2000s', years >= 2000 & years <= 2009;
    '2010s', years >= 2010 & years <= 2019;
    '2020s', years >= 2020 & years <= 2021;
};

% 初始化结果矩阵
num_basins = size(normalized_data, 2);  % 91
num_decades = size(decades, 1);  % 4
result = zeros(num_basins, num_decades);  % 91x4

% 第四步：计算每个年代的平均归一化值
for i = 1:num_decades
    mask = decades{i, 2};
    mean_by_decade = mean(normalized_data(mask, :), 1);  % 1x91
    result(:, i) = mean_by_decade';  % 91x1
end

% 第五步：写入Excel文件
headers = {'1990s', '2000s', '2010s', '2020s'};
xlswrite('normalized_water_area_by_decade.xlsx', [headers; num2cell(result)]);
