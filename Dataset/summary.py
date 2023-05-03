import pandas as pd
from os import listdir

FOLDER_PATH = ["Dataset/Tidy", "Dataset/Raw"]
onlyfiles = [f for path in FOLDER_PATH for f in listdir(path)]

# %%
for filename in onlyfiles:
    try:
        df = pd.read_csv("Dataset/Tidy/" + filename)
    except:
        df = pd.read_csv("Dataset/Raw/" + filename)

    print("Dataset: ", filename)
    # print(f"Số dòng: {len(df)}, Số cột: {len(df.columns)}")
    print(f"{len(df)} dòng, {len(df.COLUMNS)} cột")

# 