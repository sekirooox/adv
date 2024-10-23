import sys
import os
sys.path.append("../../../")
from src.pe_modifier import PEModifier
import pandas as pd
import argparse
import numpy as np
"""
从.npz的良性可执行文件中提取特征，转换为csv
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract features to train Byte Histogram GAN')

    parser.add_argument("--raw_npz_filepath",
                        type=str,
                        help="Filepath where the benign executables are stored in .npz format",
                        default=r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\data\BODMAS")# ../../../npz/BODMAS/raw_npz/benign/
    parser.add_argument("--annotations_filepath",
                        type=str,
                        help="Filepath where the annotations will be stored",
                        default=r"histogram_feature_vector.csv")# data/BODMAS_benign.csv
    parser.add_argument("--ytrue",
                        type=int,
                        help="Y true",
                        default=0)
    args = parser.parse_args()


    annotations_df = pd.DataFrame()
    hashes = []
    labels = []

    filenames = os.listdir(args.raw_npz_filepath)
    for i, filename in enumerate(filenames):
        try:
            print(i, os.path.join(args.raw_npz_filepath, filename))
            raw_npz = np.load(os.path.join(args.raw_npz_filepath, filename), allow_pickle=True)['arr_0']# "arr_0"
            print("Shape: {}".format(raw_npz.shape))
            if raw_npz.shape[0] < 1048576:
                hashes.append(filename.replace(".npz", ""))
                labels.append(args.ytrue)
        except Exception as e:
            print(e)

    annotations_df["sha256"] = hashes
    annotations_df["label"] = labels
    annotations_df.to_csv(args.annotations_filepath, index=False)