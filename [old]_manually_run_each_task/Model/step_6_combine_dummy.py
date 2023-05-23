import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

plt.rcParams["font.family"] = "Times New Roman"

from Preprocessing.utils import correct_dtypes


# In[2]:

def change_width(ax, new_value):
    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)


warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
pd.options.display.max_rows

# In[3]:
df = pd.read_csv('Dataset/Tidy/4_dataset_reprocessed.csv')
df = correct_dtypes(df)
df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)

# %%
COLUMNS_TO_COMBINE = ['brand', 'cpu_type']
hi = pd.get_dummies(df[COLUMNS_TO_COMBINE])
new_rows = []
for index, row in hi.iterrows():
    # Filter
    selected_dummies = row[row == 1]
    selected_dummies_names = [index for index in selected_dummies.index]
    # Concat columns
    combined_dummies_names = '_'.join([name.split('_')[-1] for name in selected_dummies_names])
    # Append to list
    new_rows.append(combined_dummies_names)
combined_column = pd.DataFrame({'_'.join(COLUMNS_TO_COMBINE): new_rows})
df_combined = pd.concat([combined_column, df['used_price']], axis=1)

# %%
df.drop(COLUMNS_TO_COMBINE, inplace=True, axis=1)
df = pd.concat([df_combined['_'.join(COLUMNS_TO_COMBINE)], df], axis=1)
df.to_csv('Dataset/Tidy/4_combined_column.csv', index=False)

# %% Plot high-level interactions
COLUMNS_TO_COMBINE = ['brand', 'cpu_type', 'ram']
MATCHED_VALUES = ['Acer_i7', 'HP_i7']

hi = pd.get_dummies(df[COLUMNS_TO_COMBINE])
new_rows = []
for index, row in hi.iterrows():
    # Filter
    selected_dummies = row[row == 1]
    selected_dummies_names = [index for index in selected_dummies.index]
    # Concat columns
    combined_dummies_names = '_'.join([name.split('_')[-1] for name in selected_dummies_names])
    # Append to list
    new_rows.append(combined_dummies_names)
combined_column_name = '_'.join(COLUMNS_TO_COMBINE)
combined_column = pd.DataFrame({combined_column_name: new_rows})
df_combined = pd.concat([combined_column, df['used_price']], axis=1)


def filter_row(value):
    for matched_value in MATCHED_VALUES:
        if matched_value in value:
            return True
    return False


hi = df_combined[combined_column_name].apply(filter_row)
df_combined = df_combined[hi]

plt.figure()
factor = df_combined[combined_column_name].nunique()
plt.figure(figsize=(1.5 + factor * 0.35, 4))

# Tạo group rồi sort theo median trước khi vẽ
grouped = df_combined.groupby(combined_column_name)
df2 = pd.DataFrame({col: vals['used_price'] for col, vals in grouped})
if str(df2.columns[0]).replace('.', '').isnumeric():
    df2 = df2[df2.columns.sort_values()]
else:
    meds = df2.median()
    meds.sort_values(ascending=True, inplace=True)
    df2 = df2[meds.index]
ax = sns.boxplot(data=df2)

# Bỏ viền xung quanh
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

# Size của x y ticks
plt.xticks(fontsize=15.65)
plt.yticks(fontsize=15.65)
# Size của x y labels
axes = plt.gca()
axes.xaxis.label.set_size(15.65)
axes.yaxis.label.set_size(15.65)

# Kích thước mỗi bar
change_width(ax, 0.7)

# Vẽ ticks của trục y
__ = ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
# Custom ticks của trục y
labels = [str(int(item / 1e6)) + ' tr' for item in ax.get_yticks()]
__ = ax.set_yticklabels(labels)

plt.tight_layout()
plt.show()
