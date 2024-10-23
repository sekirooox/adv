import os
import numpy as np

def convert_npz_directory_to_ratios(npz_directory, output_directory):
    # 确保输出目录存在，如果不存在则创建
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 遍历npz文件目录下的所有文件
    for file_name in os.listdir(npz_directory):
        if file_name.endswith('.npz'):
            npz_filepath = os.path.join(npz_directory, file_name)
            file_base_name = os.path.splitext(file_name)[0]  # 获取不带后缀的文件名
            output_filepath = os.path.join(output_directory, f"{file_base_name}.txt")

            # 读取npz文件
            data = np.load(npz_filepath)
            features = data['generated_features']  # 获取特征向量

            # 确保形状为 (1, 256)，提取 (256,) 的一维向量
            if features.shape == (1, 256):
                features = features.flatten()

            # 将特征向量保存为ratios.txt文件
            with open(output_filepath, 'w') as f:
                for i in range(features.shape[0]):
                    f.write(f"{i} {features[i]}\n")
            print(f"Ratios saved to {output_filepath}")

# 示例使用
if __name__ == '__main__':
    npz_directory =r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious_target'  # npz文件存储目录
    output_directory = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious_ratio_txt'  # 输出txt文件的目录

    convert_npz_directory_to_ratios(npz_directory, output_directory)
