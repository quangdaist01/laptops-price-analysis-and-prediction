#!/usr/bin/env python
# coding: utf-8

# # Import modules

# In[28]:


import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import joblib
import warnings

warnings.filterwarnings("ignore")
pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


# # Các hàm hỗ trợ

# In[29]:


def make_key_from(combination, poly_degree):
    """ Tạo các khóa để lưu trữ mô hình"""
    combination_with_poly_degree = [str(poly_degree)] + combination
    key = "|".join(combination_with_poly_degree)
    return key


def create_model_from_pipeline_and_fit(x, y):
    """ Tạo mô hình """
    lm = Ridge()
    lm.fit(x, y)
    return lm


def select_best_from(models, model_results):
    """ Trả về mô hình có r2 trên test cao nhất """

    r2_test = pd.Series({k: v["r2 test"] for k, v in model_results.items()})

    best_model_key = r2_test.idxmax()
    best_score = r2_test.max()

    poly_degree, key = best_model_key.split('|')[0], best_model_key.split('|')[1:]
    formatted_key = ', '.join(key)
    print(f'The best_model is the model with polynomial degree of {poly_degree}\n'
          f'from features: {formatted_key}\n'
          f'with r2 test of {best_score}')

    return models[best_model_key]


def prepare_data_for_model(x, y, poly_degree=1):
    """ Tiền xử lý dữ liệu """

    # Lấy các thuộc tính
    features = list(x.columns)

    quanti_cols_origin = ['weight', 'thickness', 'width', 'length', 'ppi']
    quanti_cols = list(set(features) & set(quanti_cols_origin))
    quali_cols = list(set(features) - set(quanti_cols))

    # Chuyển các biến định tính về kiểu Object
    for col in quali_cols:
        x[col] = x[col].astype('O')

    # Chuyển các biến định tính về dạng dummy
    if len(quali_cols) > 0:
        x = pd.get_dummies(x)

    # Chia tập train, test
    X_train, X_test, y_train, y_test = train_test_split(x, y, train_size=0.8, random_state=7)

    # Lấy ra các thuộc tính định tính ở tập train và test
    quali_X_train = np.array(X_train[list(set(X_train.columns) - set(quanti_cols))])
    quali_X_test = np.array(X_test[list(set(X_test.columns) - set(quanti_cols))])

    if len(quanti_cols) > 0:
        # Scale các biến liên tục
        scaler = StandardScaler()
        quanti_X_train = scaler.fit_transform(X_train[quanti_cols])
        quanti_X_test = scaler.transform(X_test[quanti_cols])
        # Polynomial Features
        poly = PolynomialFeatures(degree=poly_degree, include_bias=False)
        quanti_X_train = poly.fit_transform(quanti_X_train)
        quanti_X_test = poly.transform(quanti_X_test)

    if len(quanti_cols) > 0 and len(quali_cols) > 0:
        # Merge
        np_X_train = np.concatenate([quanti_X_train, quali_X_train], axis=1)
        np_X_test = np.concatenate([quanti_X_test, quali_X_test], axis=1)
    elif len(quali_cols) > 0:
        np_X_train = quali_X_train
        np_X_test = quali_X_test
    else:
        np_X_train = quanti_X_train
        np_X_test = quanti_X_test

    return np_X_train, np_X_test, y_train, y_test


# # Xây dựng mô hình

# In[30]:


# Đọc dữ liệu
df = pd.read_csv("4_combined_column.csv")
# Các thuộc tính dùng để xây dựng mô hình
features = ['brand_material', 'cpu_type', 'gpu_type', 'has_touchscreen', 'weight', 'ram', 'ppi']

# In[33]:


# Train + Evaluate
MAX_POLY_DEGREE = 10

models = {}
results_models = {}
for degree in range(1, MAX_POLY_DEGREE + 1):
    key = make_key_from(features, degree)
    # Preprocessing Data
    X_train, X_test, y_train, y_test = prepare_data_for_model(df[features], df['used_price'], poly_degree=degree)
    # Train
    model = create_model_from_pipeline_and_fit(X_train, y_train)
    models[key] = model
    # Evaluate
    r2_train = model.score(X_train, y_train)
    r2_test = model.score(X_test, y_test)

    y_pred = model.predict(X_test)
    rmse_test = mean_squared_error(y_test, y_pred, squared=False)

    results_models[key] = {"r2 train": r2_train, "r2 test": r2_test, "rmse test": rmse_test}

# In[34]:


# Chọn ra mô hình tốt nhất
best_model = select_best_from(models, results_models)

# In[ ]:


# Dự đoán y_pred
X_train, X_test, y_train, y_test = prepare_data_for_model(df[features], df['used_price'], poly_degree=5)
y_pred = best_model.predict(X_test)

# In[42]:


# Vẽ distribution plot

# Bỏ viền xung quanh
ax = plt.subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
# Size của plot

fig = plt.gcf()
fig.set_size_inches(5, 7)

# Size của legend
plt.legend(fontsize=17)

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
axes = plt.gca()
_ = sns.distplot(y_test, hist=False, color="r", label='Actual values')
labels = [str(int(item / 1e6)) + ' tr' for item in _.get_xticks()]
__ = _.set_xticklabels(labels)
dist1 = sns.distplot(y_pred, hist=False, color="b", label="Fitted values")
plt.title('Used price\'s Distributions')
plt.grid(axis='x')
plt.legend()
plt.rcParams["font.family"] = "Times New Roman"

# In[44]:


# Vẽ residual plot

# Bỏ viền xung quanh
ax = plt.subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
# Size của plot

fig = plt.gcf()
fig.set_size_inches(5, 7)

plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
axes = plt.gca()
_ = sns.residplot(y_pred - y_test, y_pred)
xlabels = [str(int(item / 1e6)) + ' tr' for item in _.get_xticks()]
__ = _.set_xticklabels(xlabels)
ylabels = [str(int(item / 1e6)) + ' tr' for item in _.get_yticks()]
__ = _.set_yticklabels(ylabels)
plt.title('Residual plot')
plt.rcParams["font.family"] = "Times New Roman"

# In[ ]:


# Lưu mô hình tốt nhất
filename = 'model.sav'
joblib.dump(best_model, filename)
