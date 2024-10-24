"""
这个文件的功能是从原始的 JSONL 文件中提取特征，
并将这些特征转换成 CSV 格式用于训练和测试。
它主要针对特征提取和数据格式转换任务，并结合了外部特征提取器（ByteHistogramExtractor）来生成特征向量
"""
import pandas as pd
import json
import sys
import csv
sys.path.append("../../../../")
from src.feature_extractors.bytes_histogram_extractor import ByteHistogramExtractor
from collections import OrderedDict

training_csv_filepath = "../../../../data/EMBER_2018/training.csv"# ../../../../data/EMBER_2018/training.csv
testing_csv_filepath = "../../../../data/EMBER_2018/testing.csv"# ../../../../data/EMBER_2018/testing.csv

testing_jsonl_filepaths = [
    "../../../../data/EMBER_2018/test_features.jsonl"
]

training_jsonl_filepaths = [
    "../../../../data/EMBER_2018/train_features_0.jsonl",
    "../../../../data/EMBER_2018/train_features_1.jsonl",
    "../../../../data/EMBER_2018/train_features_2.jsonl",
    "../../../../data/EMBER_2018/train_features_3.jsonl",
    "../../../../data/EMBER_2018/train_features_4.jsonl",
    "../../../../data/EMBER_2018/train_features_5.jsonl"
]
if __name__ == "__main__":
    df_train = pd.read_csv(training_csv_filepath)
    df_test = pd.read_csv(testing_csv_filepath)

    feature_extractor = ByteHistogramExtractor()

    features_dict = OrderedDict({"sha256": None})
    features_dict.update(OrderedDict({"f_{}".format(i): 0.0 for i in range(feature_extractor.dim)}))
    features_dict.update(OrderedDict({"label": None}))

    # Training data
    """这里加了break"""
    i = 0
    for training_json_filepath in training_jsonl_filepaths:
        # Get name without .jsonl
        output_filename = training_json_filepath.split("/")[-1][:-6] + "_2018.csv"
        with open(output_filename, "w") as output_file:
            fieldnames = features_dict.keys()
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            with open(training_json_filepath, "r") as input_file:
                for line in input_file:
                    features_dict = OrderedDict({"sha256": None})
                    features_dict.update(OrderedDict({"f_{}".format(i): 0.0 for i in range(feature_extractor.dim)}))
                    features_dict.update(OrderedDict({"label": None}))

                    data = json.loads(line)
                    normalized_features = feature_extractor.process_raw_features(data)
                    label = df_train.loc[df_train["sha256"] == data["sha256"]]["label"]
                    if i%100==0:
                        print(i, data["sha256"], int(label))
                    for k, feature_value in enumerate(normalized_features):
                        features_dict["f_{}".format(k)] = feature_value

                    features_dict["sha256"] = data["sha256"]
                    features_dict["label"] = int(label)
                    writer.writerow(features_dict)
                    i += 1
        print(f'{output_filename}成功读写！')
        break



    features_dict = OrderedDict({"sha256": None})
    features_dict.update(OrderedDict({"f_{}".format(i): 0.0 for i in range(feature_extractor.dim)}))
    features_dict.update(OrderedDict({"label": None}))

    i = 0
    for testing_json_filepath in testing_jsonl_filepaths:
        # Get name without .jsonl
        output_filename = testing_json_filepath.split("/")[-1][:-6] + "_2018.csv"
        with open(output_filename, "w") as output_file:
            fieldnames = features_dict.keys()
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            with open(testing_json_filepath, "r") as input_file:
                for line in input_file:
                    features_dict = OrderedDict({"sha256": None})
                    features_dict.update(OrderedDict({"f_{}".format(i): 0.0 for i in range(feature_extractor.dim)}))
                    features_dict.update(OrderedDict({"label": None}))

                    data = json.loads(line)
                    normalized_features = feature_extractor.process_raw_features(data)
                    label = df_test.loc[df_test["sha256"] == data["sha256"]]["label"]
                    if i%100==0:
                        print(i, data["sha256"], int(label))

                    for k, feature_value in enumerate(normalized_features):
                        features_dict["f_{}".format(k)] = feature_value

                    features_dict["sha256"] = data["sha256"]
                    features_dict["label"] = int(label)
                    writer.writerow(features_dict)
                    i += 1
