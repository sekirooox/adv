import lightgbm as lgb
import argparse
import pandas as pd
import json
""" 一些库的说明：
sys：系统文件
sys.args：表示获得命令行参数，第一行默认为文件名

argparse：分为位置参数和可选参数
可选参数：有--开头，可以不填写，defalut和help
位置参数：没有--开头，必须填写，help
python xxx --help：打印日志

argparse.xxx：从传入参数中获取对应值，比直接索引更好
"""



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LightGBM Model Training Script')

    parser.add_argument("--training_filepath",# 参数名称，类型，默认
                        type=str,
                        help="Training CSV file",
                        default="C:\\Users\\ASUS\\PycharmProjects\\pythonProject\\adv_mlw_examples_generation_with_gans-main\\data\\ember2018\\train_metadata.csv"
                        )
    parser.add_argument("--validation_filepath",
                        type=str,
                        help="Validation CSV file",
                        default=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\data\ember2018\test_metadata.csv'
                        )
    parser.add_argument("--hyperparameters_filepath",
                        type=str,
                        help="Hyperparameters filepath",
                        default=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\ml_models\lightgbm_models\package.json'
                        )
    parser.add_argument("--output_filepath",
                        type=str,
                        help="Resulting LightGBM model",
                        default=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\ml_models\lightgbm_models'
                        )
    args = parser.parse_args()

    train_data = pd.read_csv(args.training_filepath)
    val_data = pd.read_csv(args.validation_filepath)

    # Shuffle the dataframe
    train_data = train_data.sample(frac=1)
    val_data = val_data.sample(frac=1)

    # Get labels and hashes
    train_labels = train_data["label"]
    train_sha256 = train_data["sha256"]
    val_labels = val_data["label"]
    val_sha256 = val_data["sha256"]


    train_data = train_data.drop(labels=["sha256", "label"], axis=1)
    val_data = val_data.drop(labels=["sha256", "label"], axis=1)

    print(f'train_data.info:\n{train_data.info}')

    # for col in train_data.columns:
    #    print(col)

    train_data = lgb.Dataset(train_data, label=train_labels)
    print(f'train_data:\n{train_data}')

    val_data = lgb.Dataset(val_data, label=val_labels, reference=train_data)
    print(f'val_data:\n{val_data}')

    with open(args.hyperparameters_filepath, "r") as hyperparameters_file:
        params = json.load(hyperparameters_file)

    num_rounds = 1000
    early_stopping_rounds =5
    bst = lgb.train(params, train_data, num_rounds, valid_sets=[val_data])# early_stopping_rounds=5

    bst.save_model(args.output_filepath, num_iteration=bst.best_iteration)

