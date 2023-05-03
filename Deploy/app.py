# set FLASK_APP=app.py
# set FLASK_ENV=development
# flask run
import json
import math
import re

from flask import Flask, render_template, request
import joblib
import numpy as np

with open('input_columns_for_model.txt', encoding='utf8') as f:
    COLUMNS = json.load(f)
STANDARD_SCALER = joblib.load('std_scaler.bin')
MODEL = joblib.load('model.sav')


def make_poly_features_from(features_dict, max_poly_degree):
    separate_poly_features = {}

    # Make separate poly features i.e: x^2, x^3
    for feature in features_dict.keys():
        for degree in range(1, max_poly_degree + 1):
            if degree == 1:
                separate_poly_features[feature] = features_dict[feature]
            else:
                separate_poly_features[f'{feature}^{degree}'] = features_dict[feature] ** degree

    # Make combined poly features i.e: x^2 y, x^3 y^4
    all_poly_features = {}
    for feature in separate_poly_features.keys():
        for inner_feature in separate_poly_features.keys():
            all_poly_features[f'{feature} {inner_feature}'] = separate_poly_features[feature] * separate_poly_features[
                inner_feature]

    all_poly_features.update(separate_poly_features)
    return all_poly_features


def make_ppi(screen_size, resolution):
    length_width = re.findall("\\d*\\.?,?\\d+", resolution)
    ppi = math.sqrt(pow(int(length_width[0]), 2) + pow(int(length_width[1]), 2)) / float(screen_size)
    return ppi


def preprocess_continous(input_data):
    weight = float(input_data.pop('weight'))
    # make ppi
    screen_size = input_data.pop('screen_size')
    resolution = input_data.pop('resolution')
    ppi = make_ppi(screen_size, resolution)

    # scale values
    scaled_values = STANDARD_SCALER.transform(np.array([float(weight), float(ppi)]).reshape(1, -1))[0]
    scaled_weight = scaled_values[0]
    scaled_ppi = scaled_values[1]

    # make interaction between weight vs ppi
    all_poly_features = make_poly_features_from({'weight': scaled_weight, 'ppi': scaled_ppi}, max_poly_degree=5)
    return all_poly_features


def preprocess_categorical(input_data):
    # make interaction between brand vs material
    brand = input_data.pop('brand')
    material = input_data.pop('material')
    combined_dummies_column = [f'brand_material_{brand}_{material}']

    single_dummies_columns = ['_'.join([key, value]) for key, value in input_data.items()]

    dummies_columns = single_dummies_columns + combined_dummies_column

    return dummies_columns


def convert_json_to_model_input(input_data):
    """
    The model expects input in the form ...,"weight^2 ppi", "has_touchscreen_1", "has_touchscreen_0",
    "brand_material_Dell_Nhựa", "brand_material_MSI_Kim loại",...
    so we have to preprocess data MANUALLY before putting into the model
    """

    all_poly_features = preprocess_continous(input_data)
    dummies_columns = preprocess_categorical(input_data)

    row = []
    for column in COLUMNS:
        # insert value for non-dummies columns
        if column in all_poly_features.keys():
            row.append(all_poly_features[column])

        # insert value for dummies columns
        elif column in dummies_columns:
            row.append(1)
        else:
            row.append(0)
    return np.asarray(row, dtype=np.float64).reshape(1, -1)


# %%
app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template("home.html")


@app.route('/', methods=['POST'])
def predict():
    data = dict(request.form)
    # Process input data
    preprocessed_data = convert_json_to_model_input(data)
    # Predict
    result = MODEL.predict(preprocessed_data)
    formatted_result = f'Giá dự đoán: {int(result[0]):,} VNĐ'
    return formatted_result


if __name__ == '__main__':
    app.run(debug=True)
