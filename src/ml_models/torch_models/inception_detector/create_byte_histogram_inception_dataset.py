import pandas as pd
import numpy as np
from numpy import savez_compressed
import os
"""读取csv文件"""
# training_ember_2017_filepath = "/home/kaito/postdoc_projects/CeADAR/appending_bytes_to_bypass_ML_detectors/src/byte_histogram/data/csv/shuffled_train_features_2017.csv"
# testing_ember_2017_filepath = "/home/kaito/postdoc_projects/CeADAR/appending_bytes_to_bypass_ML_detectors/src/byte_histogram/data/csv/shuffled_test_features_2017.csv"
training_ember_2017_filepath="../../lightgbm_models/byte_histogram_detector/train_features_0_2017.csv"# 这里传入csv文件，应该是注释文件
testing_ember_2017_filepath='../../lightgbm_models/byte_histogram_detector/test_features_2017.csv'

"""保存文件"""
# training_numpy_2017_filepath = "/mnt/hdd2/inception/byte_histogram/2017/training/"
# testing_numpy_2017_filepath = "/mnt/hdd2/inception/byte_histogram/2017/testing/"
training_numpy_2017_filepath='./data/2017/training/'
testing_numpy_2017_filepath='./data/2017/testing/'


# training_ember_2018_filepath = "/home/kaito/postdoc_projects/CeADAR/appending_bytes_to_bypass_ML_detectors/src/byte_histogram/data/csv/shuffled_train_features_2018.csv"
# testing_ember_2018_filepath = "/home/kaito/postdoc_projects/CeADAR/appending_bytes_to_bypass_ML_detectors/src/byte_histogram/data/csv/shuffled_test_features_2018.csv"
training_ember_2018_filepath="../../lightgbm_models/byte_histogram_detector/train_features_0_2018.csv"# 这里传入csv文件，应该是注释文件
testing_ember_2018_filepath='../../lightgbm_models/byte_histogram_detector/test_features_2018.csv'

# training_numpy_2018_filepath = "/mnt/hdd2/inception/byte_histogram/2018/training/"
# testing_numpy_2018_filepath = "/mnt/hdd2/inception/byte_histogram/2018/testing/"
training_numpy_2018_filepath='./data/2018/training/'
testing_numpy_2018_filepath='./data/2018/testing/'


df = pd.read_csv(training_ember_2017_filepath)
print(f'now is processing:{training_ember_2017_filepath}')
for index, row in df.iterrows():
    print(index)
    row = list(row)
    sha256 = row[0]
    X = np.array(row[1:])
    savez_compressed(os.path.join(training_numpy_2017_filepath, '{}.npz'.format(sha256)),
                     X)

df = pd.read_csv(testing_ember_2017_filepath)
print(f'now is processing:{testing_ember_2017_filepath}')
for index, row in df.iterrows():
    print(index)
    row = list(row)
    sha256 = row[0]
    X = np.array(row[1:])
    savez_compressed(os.path.join(testing_numpy_2017_filepath, '{}.npz'.format(sha256)),
                     X)

df = pd.read_csv(training_ember_2018_filepath)
print(f'now is processing:{training_ember_2018_filepath}')
for index, row in df.iterrows():
    print(index)
    row = list(row)
    sha256 = row[0]
    X = np.array(row[1:])
    savez_compressed(os.path.join(training_numpy_2018_filepath, '{}.npz'.format(sha256)),
                     X)

df = pd.read_csv(testing_ember_2018_filepath)
print(f'now is processing:{testing_ember_2018_filepath}')
for index, row in df.iterrows():
    print(index)
    row = list(row)
    sha256 = row[0]
    X = np.array(row[1:])
    savez_compressed(os.path.join(testing_numpy_2018_filepath, '{}.npz'.format(sha256)),
                     X)

