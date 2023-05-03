import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Preprocessing.utils import ordered_columns_step_2

plt.rcParams["font.family"] = "Times New Roman"

# %%
df = pd.read_csv('Dataset/Tidy/1_dataset_renamed_preprocessed_dropped.csv')

# %% Column

# Xuất file csv
missing_percentage = (100 * df.isna().sum() / df.shape[0])
missing_percentage.sort_values(ascending=False, inplace=True)
# missing_percentage.to_csv('Preprocessing/utils/1_1_missing_percentage.csv')

# Visualize
missing_percentage_greater_than_5 = missing_percentage[missing_percentage > 5]

df_temp = df[missing_percentage_greater_than_5.index]
df_temp
labels = df_temp.columns
na_values = df_temp.isna().sum().values
not_na_values = df_temp.shape[0] - df_temp.isna().sum().values

width = 0.60  # the width of the bars: can also be len(x) sequence
fig, ax = plt.subplots(figsize=(4.5, 3))

ax.bar(labels, na_values, width, label='NA')
# ax.bar(labels, not_na_values, width, bottom=na_values,
#        label='Not NA')

ax.set_ylabel('Số lượng')
ax.set_title('Các cột có tỉ lệ missing trên 5%')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Chú thích cho từng cột
total = len(df_temp)
for i, p in enumerate(ax.patches):
    if i > 9:
        continue
    percentage = '{:.1f}%'.format(100 * p.get_height() / total)
    x = p.get_x() + p.get_width() / 2 - 0.47
    y = p.get_y() + p.get_height() + 0.5
    _ = ax.annotate(percentage, (x, y), size=10)

# Size của x y ticks
plt.xticks(fontsize=13)
plt.ylabel("count")
plt.yticks(fontsize=13)
# Size của x y labels
axes = plt.gca()
axes.xaxis.label.set_size(13)
axes.yaxis.label.set_size(13)

plt.tight_layout()
_ = plt.xticks(rotation=70)

plt.savefig('missing.png', bbox_inches='tight', dpi=250)


# plt.show()


# %%
def preprocess_has_touchscreen(string_in):
    """
    Trích ra giá trị phân biệt giữa
    laptop có hỗ trợ cảm ứng (1) và laptop không có hỗ trợ cảm ứng (0)
    """
    if string_in is None or str(string_in) == "nan":
        return 0
    else:
        return 1


def preprocess_sd_slot(string_in):
    """
    Trích ra số lượng các loại khe cảm thẻ nhớ được hỗ trợ
    """

    if string_in is None or str(string_in) == "nan":
        return 0
    else:
        return len(string_in.split('\n'))


df['has_touchscreen'] = df['has_touchscreen'].apply(preprocess_has_touchscreen)
df['num_sd_slot'] = df['sd_slot'].apply(preprocess_sd_slot)
df.drop(columns=['sd_slot'], inplace=True)

# %%
# Loại bỏ những cột có tỉ lệ missing values trên 35%

# Xuất file csv
missing_percentage = (100 * df.isna().sum() / df.shape[0])
missing_percentage = missing_percentage.apply(lambda percent: True if percent <= 5 else np.nan)
non_missing = missing_percentage.dropna()
selected_columns = list(non_missing.index)

# Sắp xếp lại thứ tự các cột
selected_columns_ordered = []
for column in ordered_columns_step_2:
    if column in selected_columns:
        selected_columns_ordered.append(column)
# %%
df = df[selected_columns_ordered]


# %% Row

def fill_missing(row_index, column_name, value):
    df.iloc[row_index - 2, df.columns.get_loc(column_name)] = value
    print(f'Đã điền cho lap ở dòng thứ {row_index} trong file EXCEL')


# %%

# Acer Swift 1 SF114 32 P2SG N5000/4GB/64GB/Win10 (NX.GZJSV.001)
fill_missing(34, 'storage', 128)

# Dell Inspiron 15 5584 i5 8265U/8GB/2TB/2GB MX130/Win10 (N5I5353W)
fill_missing(154, 'storage', 'HDD 1 TB')

# Dell Inspiron 5480 i5 8265U/8GB/256GB/2GB MX150/Office365/Win10 (X6C892)
fill_missing(157, 'released', 2018)

# Lenovo Legion Y530 15 i7 8750H/8GB/2TB+16GB/4GB GTX1050Ti/Win10 (81FV008LVN)
fill_missing(269, 'storage', 'HDD 1 TB')
# fill_missing(269,'webcam','')

# MacBook Pro Touch 16 inch 2019 i7 2.6GHz/16GB/512GB/4GB Radeon Pro 5300M (MVVJ2SA/A)
fill_missing(302, 'gpu_type', 'Radeon')
fill_missing(202, 'ram', 16)

# Apple Macbook Air 2015 MJVE2ZP/A i5 5250U/4GB/128GB
fill_missing(66, 'cpu_type', 'i5')
fill_missing(66, 'storage', 128)
fill_missing(66, 'os', 'MacOS')
fill_missing(66, 'released', '2015')

# Apple Macbook Air MMGF2ZP/A i5 1.6GHz/8GB/128GB (2015)
fill_missing(69, 'released', 2015)

# Apple Macbook Pro 2019 Touch i7 2.6GHz/16GB/256GB/ Radeon 555X (MV902SA/A)
fill_missing(70, 'gpu_type', 'Radeon')
fill_missing(70, 'released', 2019)

# Apple Macbook Pro MPXQ2SA/A i5 2.3GHz/8GB/128GB (2017)
fill_missing(71, 'released', 2017)

# Apple Macbook Pro Touch MLH12SA/A i5 6267U/8GB/256GB (2016)
fill_missing(72, 'released', 2016)

# Apple Macbook Pro Touch MPXV2SA/A i5 3.1GHz/8GB/256GB (2017)
fill_missing(73, 'released', 2017)

# %% Export
df.to_csv('Dataset/Tidy/2_dataset_missings_filtered.csv', index=False)
