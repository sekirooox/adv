import pandas as pd

"""全部改为2018"""
training_csv_filepaths = [
    "../../../../data/EMBER_2017/train_features_0_2018.csv",
    "../../../../data/EMBER_2017/train_features_1_2018.csv",
    "../../../../data/EMBER_2017/train_features_2_2018.csv",
    "../../../../data/EMBER_2017/train_features_3_2018.csv",
    "../../../../data/EMBER_2017/train_features_4_2018.csv",
    "../../../../data/EMBER_2017/train_features_5_2018.csv"
]

if __name__ == "__main__":
    df_train_0 = pd.read_csv(training_csv_filepaths[0])
    df_train_1 = pd.read_csv(training_csv_filepaths[1])
    df_train_2 = pd.read_csv(training_csv_filepaths[2])
    df_train_3 = pd.read_csv(training_csv_filepaths[3])
    df_train_4 = pd.read_csv(training_csv_filepaths[4])
    df_train_5 = pd.read_csv(training_csv_filepaths[5])

    df_train = pd.concat([df_train_0, df_train_1, df_train_2, df_train_3, df_train_4, df_train_5], axis=0, ignore_index=True)
    df_train.to_csv("data/csv/train_features_2017.csv", index=False)