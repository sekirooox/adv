import numpy as np
import copy
import subprocess
import csv
import os
from src.gan_implementations.solver.utils import calculate_histogram,calculate_normalized_histogram,\
    append_bytes_given_target_histogram,append_bytes_given_target_bytes,heuristic_approach,\
    create_byte_sizes_file,create_ratios_file
def read_ratios(filepath):
    ratios = np.zeros(256)
    with open(filepath, 'r') as f:
        for line in f:
            byte_val, ratio = line.split()
            ratios[int(byte_val)] = float(ratio)
    return ratios
def save_modified_binary_file(output_filepath, byte_sequence):
    with open(output_filepath, 'wb') as output_file:
        byte_array = bytearray(byte_sequence)
        output_file.write(byte_array)
    print(f"Modified binary file has been saved to {output_filepath}.")


def save_modified_binary_file_in_directory(binary_dir, ratios_dir, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历二进制文件目录
    for binary_file_name in os.listdir(binary_dir):
        binary_filepath = os.path.join(binary_dir, binary_file_name)
        base_name = os.path.splitext(binary_file_name)[0]  # 获取不带扩展名的文件名

        # 找到对应的 ratios.txt 文件
        ratios_filepath = os.path.join(ratios_dir, f'{base_name}.txt')
        if not os.path.exists(ratios_filepath):
            print(f"Warning: {ratios_filepath} does not exist, skipping.")
            continue

        # 读取二进制文件的字节序列
        with open(binary_filepath, "rb") as input_file:
            sequence = list(input_file.read())
        print(f"Processing {binary_file_name}, length: {len(sequence)}")

        # 计算原始字节分布
        histogram = calculate_histogram(sequence)
        normalized_histogram = calculate_normalized_histogram(sequence)

        # 读取目标归一化字节分布
        target_normalized_histogram = read_ratios(ratios_filepath)

        # 使用启发式方法调整字节分布
        resulting_histogram, resulting_norm_histogram = heuristic_approach(
            sequence, normalized_histogram, target_normalized_histogram
        )

        # 生成新的字节序列
        target_byte_sequence = append_bytes_given_target_histogram(sequence, histogram, resulting_histogram)

        # 保存修改后的文件到输出目录
        output_filepath = os.path.join(output_dir, f'{base_name}_modified')
        save_modified_binary_file(output_filepath, target_byte_sequence)
        break

if __name__ == "__main__":
    binary_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious'
    ratios_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious_ratio_txt'
    output_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious_byte'
    save_modified_binary_file_in_directory(binary_dir, ratios_dir, output_dir)


