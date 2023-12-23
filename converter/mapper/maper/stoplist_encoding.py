import pandas as pd


def stoplist_encoding(csv_file):
    df = pd.read_csv(csv_file, encoding="windows-1251")
    data_list = df.values.tolist()
    return data_list
