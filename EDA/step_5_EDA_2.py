import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.factorplots import interaction_plot
import statsmodels.api as sm
from statsmodels.formula.api import ols
import warnings

plt.rcParams["font.family"] = "Times New Roman"

from Preprocessing.utils import correct_dtypes

# In[2]:


warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)
pd.options.display.max_rows

# In[3]:
df = pd.read_csv('Dataset/Tidy/3_dataset_reprocessed.csv')
df = correct_dtypes(df)

quanti_cols = df.select_dtypes(include='number').columns
quali_df = df.select_dtypes(include='object')
quali_cols = quali_df.columns

# %% TƯƠNG QUAN (ĐA BIẾN)
# %% Interaction plot
p_values = {}
for i in range(len(quali_cols)):
    for j in range(len(quali_cols)):
        num_groups = df.groupby([quali_cols[i], quali_cols[j]]).ngroups
        if i == j or num_groups < 5:
            continue

        # convert all values to string to fix x_tick not recognize
        df_temp = quali_df.dropna(subset=[quali_cols[i], quali_cols[j]])

        df_temp[quali_cols[i]] = df_temp[quali_cols[i]].apply(lambda x: str(x))

        # Tính p-value cho tương tác của 2 biến. p < 0.05 => có ý nghĩa thống kê => có tương tác giữa 2 biến
        model = ols(f'used_price ~ {quali_cols[i]} + {quali_cols[j]} + {quali_cols[i]}:{quali_cols[j]}',
                    data=df).fit()
        aov = sm.stats.anova_lm(model, typ=2)
        p_value = aov['PR(>F)'][f'{quali_cols[i]}:{quali_cols[j]}']

        if p_value > 0.05:
            continue

        plt.figure(figsize=(5, 7))
        # Vẽ interaction plot
        interaction_plot(x=df_temp[quali_cols[i]], trace=df_temp[quali_cols[j]], response=df['used_price'],
                         plottype='both', ms=17)

        # Size của plot

        fig = plt.gcf()
        fig.set_size_inches(5, 7)

        # Size của legend
        plt.legend(fontsize=17)

        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        axes = plt.gca()

        # Size của x y labels
        axes.xaxis.label.set_size(20)
        axes.yaxis.label.set_size(20)

        # Bỏ viền xung quanh
        ax = plt.subplot(111)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Vẽ ticks của trục x
        __ = ax.set_xticklabels(ax.get_xticklabels(), rotation=60)
        labels = [str(int(item / 1e6)) + ' tr' for item in ax.get_yticks()]
        # Custom ticks của trục y
        __ = ax.set_yticklabels(labels)

        ___ = plt.title(f'used_price vs {quali_cols[i]}:{quali_cols[j]}\n(p_value: {p_value:.2e})',
                        fontdict={'size': 20})
        p_values[f'{quali_cols[i]}|{quali_cols[j]}'] = p_value
        plt.tight_layout()
        plt.show()
        # break
        # plt.savefig(
        #     f'EDA/plots results/categorical/interation between important features/{quali_cols[i]} vs '
        #     f'{quali_cols[j]}.png',
        #     bbox_inches='tight', dpi=250)
        plt.clf()
    # break
