import numpy as np
import pandas as pd
from Preprocessing.utils import correct_dtypes, alternative_names, rename_columns, remove_duplicate_laptops

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

df = pd.read_csv('Dataset/Tidy/2_dataset_missings_filtered.csv')
df = correct_dtypes(df)


# %% Biến đổi + gom nhóm các thuộc tính


def reprocess_storage(string_in):
    """
        Trích ra dung lượng ổ cứng
    """
    # Kiểm tra giá trị trong ô trước khi bắt đầu xử lí
    if string_in is None or str(string_in) == "nan":
        return np.nan

    common_drive_capacity = ["HDD 1 TB", "128 GB", "256 GB", "512 GB", "1 TB"]
    new_drive = np.nan

    if string_in is not None and str(string_in) != "nan":
        drive_tight_uppercased = string_in.upper()
        for capacity in common_drive_capacity:
            if capacity in drive_tight_uppercased:
                new_drive = capacity
                break

    if "HDD SATA (nâng cấp tối đa 2TB) 1 TB" in string_in:
        return "HDD 1 TB"
    return new_drive


def reprocess_material(string_in):
    """
    Trích ra chất liệu laptop
    """
    # Kiểm tra giá trị trong ô trước khi bắt đầu xử lí
    if string_in is None or str(string_in) == "nan":
        return np.nan

    # Chia material thành 3 nhóm: Kim loại, hợp kim và nhựa

    string_in = string_in.lower()
    if ('nhôm' in string_in) or ('magie' in string_in) or ('hợp kim' in string_in):
        return 'Kim loại'
    elif 'nhựa' in string_in:
        if 'kim loại' in string_in:
            return 'Nhựa + kim loại'
        else:
            return 'Nhựa'
    else:
        return 'Kim loại'


def reprocess_num_sd_slot(string_in):
    if string_in is None or str(string_in) == 'nan':  # None hoặc nan -> np.nan
        return np.nan
    else:
        if string_in > 0:
            return 1
        else:
            return 0


def reprocess_screen_size(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan

    typical_screen_sizes = [13.3, 14.0, 15.6]

    if string_in in typical_screen_sizes:
        return str(string_in)
    else:
        return 'Others'


def reprocess_resolution(string_in):
    if string_in is None or str(string_in) == "nan":
        return np.nan

    else:
        numbers = [int(x) for x in string_in.split('x')]
        if numbers[0] * numbers[1] > 1920 * 1080:
            return "> Full HD"
        elif numbers[0] * numbers[1] < 1920 * 1080:
            return "< Full HD"
        else:
            return "Full HD"


# %% check
# use raw 'material' and 'storage' column
df_raw = pd.read_csv('Dataset/Raw/raw_data_TGDD_used.csv')
df_raw = rename_columns(df_raw, alternative_name=alternative_names)
df_raw = remove_duplicate_laptops(df_raw)
df['material'] = df_raw['material'].apply(reprocess_material)
df['storage'] = df_raw['storage'].apply(reprocess_storage)

# df['has_sd_slot'] = df['num_sd_slot'].apply(reprocess_num_sd_slot)
# df.drop('num_sd_slot', axis=1, inplace=True)

df['screen_size'] = df['screen_size'].apply(reprocess_screen_size)
df['resolution'] = df['resolution'].apply(reprocess_resolution)


# %% Bin features

def bin_column(column, num_bin):
    """
    Input: cột muốn bin và số nhóm muốn chia (vd: df['cpu_speed'], 3: chia cột cpu_speed làm 3 bin)
    Output: cột sau khi bin
    """
    set_ = list(set(column))
    min_value = column.min()
    max_value = column.max()

    bins = np.linspace(min_value, max_value, num_bin + 1)
    set_ = [x for x in set_ if str(x) != 'nan']
    first_bin_without_nan = abs(set_ - bins[1])
    second_bin_without_nan = abs(set_ - bins[2])

    bin_1 = set_[np.argmin(first_bin_without_nan)]
    bin_2 = set_[np.argmin(second_bin_without_nan)]

    labels = [f'<{bin_1}', f'{bin_1}-{bin_2}', f'>{bin_2}']
    # print(labels)
    column = pd.cut(column, bins=bins, labels=labels, include_lowest=True)
    return column


# %%
df['cpu_speed'] = bin_column(df['cpu_speed'], 3)
df['max_cpu_speed'] = bin_column(df['max_cpu_speed'], 3)

# %%

df.to_csv("Dataset/Tidy/3_dataset_reprocessed.csv", index=False)
