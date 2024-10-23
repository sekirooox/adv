import pandas as pd
import os
import shutil


def extract_npz_files(annotation_filepath, npz_dir, output_dir):
    """
    根据注释文件从原始 npz 目录中提取对应的 npz 文件并保存到指定的输出目录。

    :param annotation_filepath: 注释文件路径
    :param npz_dir: 原始未分割的 npz 文件目录
    :param output_dir: 输出文件夹，用于保存提取的 npz 文件
    """
    # 读取注释文件
    annotations_df = pd.read_csv(annotation_filepath)

    # 检查注释文件是否为空
    if annotations_df.empty:
        print(f"注释文件 {annotation_filepath} 为空，请检查文件内容。")
        return

    # 获取所有 npz 文件名 (sha256)
    file_names = annotations_df['sha256'].tolist()  # 假设列名为 'sha256'

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 复制对应的 npz 文件到输出目录
    for file_name in file_names:
        source_path = os.path.join(npz_dir, f"{file_name}.npz")
        destination_path = os.path.join(output_dir, f"{file_name}.npz")

        if os.path.exists(source_path):
            shutil.copyfile(source_path, destination_path)
        else:
            print(f"文件未找到: {source_path}")

    print(f"文件已提取并保存至 {output_dir}。")

if __name__ == "__main__":
    """
    需要执行四次
    """
    # 示例调用
    # 修改以下路径为实际的注释文件路径和 npz 文件夹路径
    train_annotation_filepath = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\annotations\all_features\data\BODMAS_benign_train_None.csv'  # 训练集注释文件路径
    val_annotation_filepath = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\annotations\all_features\data\BODMAS_benign_test_None.csv' # 验证集注释文件路径
    test_annotation_filepath = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\annotations\all_features\data\BODMAS_benign_validation_None.csv'  # 测试集注释文件路径

    npz_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\ember_features\2018\benign' # 原始 npz 文件目录

    # 输出文件夹
    output_train_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\ember_features\2018\benign_augmented\train'
    output_val_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\ember_features\2018\benign_augmented\test'
    output_test_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\ember_features\2018\benign_augmented\val'

    # 分别提取训练、验证和测试集的 npz 文件
    extract_npz_files(train_annotation_filepath, npz_dir, output_train_dir)
    extract_npz_files(val_annotation_filepath, npz_dir, output_val_dir)
    extract_npz_files(test_annotation_filepath, npz_dir, output_test_dir)
