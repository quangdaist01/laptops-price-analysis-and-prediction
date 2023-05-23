import jsonlines
import pandas as pd


# %%
def read_results(path):
    data = []
    with jsonlines.open(path, "r") as f:
        for line in f:
            data.append(line)
    return data


# %%
def get_spec_fields(data):
    max_num_specs = 0
    specifications = []
    for line in data:
        if max_num_specs < len(line.keys()):
            max_num_specs = len(line.keys())
            specifications = list(line.keys())
    return specifications


# %%

def make_frame(raw_data, columns):
    df = pd.DataFrame(columns=columns)
    for line in raw_data:
        line_filtered = {}
        for spec in columns:
            if spec not in line.keys():
                line_filtered[spec] = None
            else:
                line_filtered[spec] = line[spec]
        df = df.append(line_filtered, ignore_index=True)
    return df
