import pandas as pd
import json
import sys
import csv
sys.path.append("../../../../")
from src.feature_extractors.hashed_imports_info_extractor import HashedImportsInfoExtractor
from collections import OrderedDict

training_csv_filepath = "../../../../data/EMBER_2017/training.csv"
testing_csv_filepath = "../../../../data/EMBER_2017/testing.csv"

testing_jsonl_filepaths = [
    "../../../../data/EMBER_2017/test_features.jsonl"
]

training_jsonl_filepaths = [
    "../../../../data/EMBER_2017/train_features_0.jsonl",
    "../../../../data/EMBER_2017/train_features_1.jsonl",
    "../../../../data/EMBER_2017/train_features_2.jsonl",
    "../../../../data/EMBER_2017/train_features_3.jsonl",
    "../../../../data/EMBER_2017/train_features_4.jsonl",
    "../../../../data/EMBER_2017/train_features_5.jsonl"
]

if __name__ == "__main__":
    df_train = pd.read_csv(training_csv_filepath)
    df_test = pd.read_csv(testing_csv_filepath)


    feature_extractor = HashedImportsInfoExtractor()

    features_dict = OrderedDict({"sha256": None})
    features_dict.update(OrderedDict({"f_{}".format(i): 0.0 for i in range(feature_extractor.dim)}))
    features_dict.update(OrderedDict({"label": None}))
    
    # Training data
    i = 0
    for training_json_filepath in training_jsonl_filepaths:
        # Get name without .jsonl
        output_filename = training_json_filepath.split("/")[-1][:-6]+"_2017.csv"
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
                    print(i, data["sha256"], int(label))
                    for k, feature_value in enumerate(normalized_features):
                        features_dict["f_{}".format(k)] = feature_value

                    features_dict["sha256"] = data["sha256"]
                    features_dict["label"] = int(label)
                    writer.writerow(features_dict)
                    i += 1
        break   # 手动break

    features_dict = OrderedDict({"sha256": None})
    features_dict.update(OrderedDict({"f_{}".format(i): 0.0 for i in range(feature_extractor.dim)}))
    features_dict.update(OrderedDict({"label": None}))

    i = 0
    for testing_json_filepath in testing_jsonl_filepaths:
        # Get name without .jsonl
        output_filename = testing_json_filepath.split("/")[-1][:-6]+"_2017.csv"
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
                    print(i, data["sha256"], int(label))

                    for k, feature_value in enumerate(normalized_features):
                        features_dict["f_{}".format(k)] = feature_value

                    features_dict["sha256"] = data["sha256"]
                    features_dict["label"] = int(label)
                    writer.writerow(features_dict)
                    i += 1
        # break




