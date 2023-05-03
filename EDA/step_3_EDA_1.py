import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
from Preprocessing.utils import correct_dtypes

plt.rcParams["font.family"] = "Times New Roman"

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
pd.options.display.max_rows

# %%

df = pd.read_csv('Dataset/Tidy/3_dataset_reprocessed.csv')
df = correct_dtypes(df)
quanti_cols = df.select_dtypes(include='number').columns
quali_df = df.select_dtypes(include='object')
quali_cols = quali_df.columns


# %% md

# MIỀN GIÁ TRỊ (BASIC INSIGHTS)

# %%
# Barplot
# Biến rời rạc


def change_width(ax, new_value):
    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)


for column in quali_cols:
    selected_columns = ['brand', 'max_cpu_speed', 'ram', 'material']
    if column not in selected_columns:
        continue

    plt.figure()
    factor = df[column].nunique()
    plt.figure(figsize=(1.5 + factor * 0.35, 4.5))
    temp = df[column].value_counts().sort_values(ascending=False)
    ax = sns.barplot(x=temp.index, y=temp, order=temp.index)

    # Size của x y ticks
    plt.xticks(fontsize=13.5)
    plt.ylabel("count")
    plt.yticks(fontsize=13.5)
    # Size của x y labels
    axes = plt.gca()
    axes.xaxis.label.set_size(13.5)
    axes.yaxis.label.set_size(13.5)

    # Bỏ viền xung quanh
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Kích thước mỗi bar
    change_width(ax, 0.7)

    # Chú thích cho từng cột
    total = len(df[column])
    for p in ax.patches:
        percentage = '{:.1f}%'.format(100 * p.get_height() / total)
        x = p.get_x() + p.get_width() / 2 - 0.33
        y = p.get_y() + p.get_height() + 0.5
        _ = ax.annotate(percentage, (x, y), size=13.5)

    # Xoay x ticks
    __ = ax.set_xticklabels(ax.get_xticklabels(), rotation=20)

    # Tiêu đề
    plt.title(f'{column}', fontsize=13.5)

    plt.tight_layout()
    # plt.show()
    plt.savefig(f'EDA/plots results/categorical/bar_plot/{column}.png', bbox_inches='tight', dpi=250)
    plt.clf()
    # break

# %%

# Distribution
# Biến liên tục
for column in quanti_cols:
    # if column == 'used_price':
    #     continue
    plt.figure(figsize=(5, 5))
    ax = sns.distplot(x=df[column])

    # Bỏ viền xung quanh
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    __ = plt.xlabel(column)

    # Size của x y ticks
    plt.xticks(fontsize=15.65)
    plt.yticks(fontsize=15.65)
    # Size của x y labels
    axes = plt.gca()
    axes.xaxis.label.set_size(15.65)
    axes.yaxis.label.set_size(15.65)

    # Tiêu đề
    plt.title(f'{column}', fontsize=15.65)

    plt.tight_layout()
    # plt.show()
    plt.savefig(f'EDA/plots results/continuous/distribution_plot/{column}.png', bbox_inches='tight', dpi=250)
    plt.clf()

# %%
# Pie chart
for column in quali_df:
    plt.figure()
    fig, ax = plt.subplots(figsize=(4, 4))
    labels = df[column].value_counts().keys()
    _ = plt.pie(x=df[column].value_counts(), autopct="%.1f%%", explode=[0.02] * len(df[column].value_counts()),
                labels=labels, pctdistance=0.75, textprops={'fontsize': 15})
    _ = plt.title(column, fontsize=15)

    plt.tight_layout()
    # plt.show()
    plt.savefig(f'EDA/plots results/categorical/pie_chart/{column}.png', bbox_inches='tight', dpi=250)
    plt.clf()

# %% md
# TƯƠNG QUAN (ĐƠN BIẾN)

# %% Box plot (Biến rời rạc)

cate_p_value = pd.DataFrame({'feature': [], 'p_value': []})

for column in quali_cols:
    plt.figure()
    factor = df[column].nunique()
    plt.figure(figsize=(1.5 + factor * 0.35, 4.5))

    selected_columns = ['brand', 'max_cpu_speed', 'ram']
    if column not in selected_columns:
        continue

    # Tạo group rồi sort theo median trước khi vẽ
    grouped = df[[column, 'used_price']].groupby([column])
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
    __ = ax.set_xticklabels(ax.get_xticklabels(), rotation=20)
    # Custom ticks của trục y
    labels = [str(int(item / 1e6)) + ' tr' for item in ax.get_yticks()]
    __ = ax.set_yticklabels(labels)

    # Tính ANOVA nhằm kiểm tra xem có sự khác nhau giữa các nhóm hay không
    model = ols(f'used_price ~ {column}', data=df).fit()
    aov = sm.stats.anova_lm(model, typ=2)
    p_value = aov['PR(>F)'][f'{column}']
    cate_p_value = cate_p_value.append({'feature': column, 'p_value': p_value}, ignore_index=True)

    # Tiêu đề
    ax = plt.title(f'used_price vs {column}\n(p_value: {p_value:.2e})', fontsize=15.65)

    plt.tight_layout()
    # plt.show()
    # break
    plt.savefig(f'EDA/plots results/categorical/box_plot/{column}.png', bbox_inches='tight', dpi=250)
    plt.clf()

# %% one-way ANOVA

# def do_anova_on(df):
#     """
#     :param df:
#     :return: Pandas series of p_values for categorical features versus dependent feature
#     """
#
#     quali_cols = df.select_dtypes(include='object').columns
#     p_values = {}
#     for index, feature in enumerate(quali_cols):
#         grouped = df.groupby(quali_cols[index])
#         keys = list(grouped.groups.keys())
#         anova_result = f_oneway(*[grouped.get_group(key)["used_price"] for key in keys])
#         p_values[feature] = anova_result.pvalue
#     return pd.Series(do_anova_on(df))
#
#
# p_values_series = do_anova_on(df)
# lowest_p_values_columns = p_values_series[p_values_series < 0.0000000001].index
# p_values_series.apply(lambda x: "{:.3f}".format(float(x))).sort_values()