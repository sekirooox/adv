import numpy as np
import copy
import subprocess
import csv
import os

"""计算字节分布图,不需要对原先字节序列进行裁剪"""
def calculate_histogram(sequence:list):
    histogram = np.array([0 for i in range(256)])
    for x in sequence:
        histogram[x] += 1
    return histogram


def calculate_normalized_histogram(sequence:list):
    histogram = np.array([0 for i in range(256)])
    for x in sequence:
        histogram[x] += 1
    return histogram / len(sequence)

# 给定字节分布:追加字符串，注意在末尾添加
def append_bytes_given_target_histogram(byte_sequence, original_histogram, target_histogram):
    target_byte_sequence = copy.deepcopy(byte_sequence)
    for i in range(original_histogram.shape[0]):# 256 不需要调整sequence大小
        diff = int(target_histogram[i] - original_histogram[i])
        for j in range(diff):
            target_byte_sequence.append(i)
    return target_byte_sequence

# 给定追加的字节及数量
def append_bytes_given_target_bytes(original_byte_sequence: list, bytes_to_append: tuple):
    target_byte_sequence = copy.deepcopy(original_byte_sequence)
    for tup in bytes_to_append:
        for j in range(tup[1]):
            target_byte_sequence.append(tup[0])
    return target_byte_sequence

def heuristic_approach(original_byte_sequence, original_normalized_histogram, target_normalized_histogram):
    original_histogram = calculate_histogram(original_byte_sequence)
    target_length = int(max([original_histogram[i]/target_normalized_histogram[i] for i in range(original_histogram.shape[0])]))
    resulting_histogram = np.array([int(target_length*target_normalized_histogram[i])  for i in range(original_histogram.shape[0])])
    return resulting_histogram, resulting_histogram / target_length


"""保存文件"""
def create_byte_sizes_file(byte_histogram: np.array, output_filepath: str):
    with open(output_filepath, "w") as output_file:
        for i, value in enumerate(byte_histogram.tolist()):
            output_file.write("{} {}\n".format(i, value))

def create_ratios_file(normalized_byte_histogram: np.array, output_filepath: str):
    with open(output_filepath, "w") as output_file:
        for i, value in enumerate(normalized_byte_histogram.tolist()):
            output_file.write("{} {}\n".format(i, value))


"""求解器求解问题"""
def run_solver(gap=0.001):
    print("Gap: ", gap)
    if gap == 0.01:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.01.sh"
            ]
        )
    if gap == 0.008:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.008.sh"
            ]
        )
    if gap == 0.005:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.005.sh"
            ]
        )
    if gap == 0.003:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.003.sh"
            ]
        )
    if gap == 0.001:
        print("Entering here!")
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.001.sh"
            ]
        )
    if gap == 0.0008:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.0008.sh"
            ]
        )
    if gap == 0.0005:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.0005.sh"
            ]
        )
    if gap == 0.0003:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.0003.sh"
            ]
        )
    if gap == 0.0001:
        result = subprocess.run(
            [
                "sh",
                "run-solver-gap0.0001.sh"
            ]
        )
    print(result.returncode)



def read_solution(solution_filepath: str):
    solution = []
    with open(solution_filepath, "r") as solution_file:
        reader = csv.reader(solution_file, delimiter='\t')
        for row in reader:
            print((int(row[0].split("#")[-1]), int(float(row[1]))))
            solution.append((int(row[0].split("#")[-1]), int(float(row[1]))))
    return solution

# 不需要获得bytesizes.txt的文件！！！
# def read_bytesizes(filepath:str):
#     # 这里不是二进制文件，而是txt文件
#     target_byte_histogram=np.zeros(256)
#     # print(target_byte_histogram.shape)
#     with open(filepath, "r") as f:
#         lines=f.readlines()
#         for i,line in enumerate(lines):
#             index,str_num=line.split(' ')
#             target_byte_histogram[i]=int(str_num)
#     # 返回ndarray
#     return target_byte_histogram
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

if __name__ == "__main__":
    binary_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious'
    ratios_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious_ratio_txt'
    output_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious_modified'
    save_modified_binary_file_in_directory(binary_dir, ratios_dir, output_dir)
    # # 获得原有二进制文件的字节序列sequence
    # filepath='00dbb9e1c09dbdafb360f3163ba5a3de_0'
    # ratios_filepath='examples/ratios.txt'
    # output_filepath=f'{filepath+"_modified"}'
    # with open(filepath, "rb") as input:
    #     sequence=list(input.read())
    # # 不需要调整sequence大小
    # print(len(sequence))
    # # print(sequence)
    #
    #
    # histogram=calculate_histogram(sequence)
    # normalized_histogram=calculate_normalized_histogram(sequence)
    # # print(f'original histogram:{list(histogram)[:256]}')
    #
    # target_normalized_histogram=read_ratios(ratios_filepath)
    # # print(f'target_norm_histogram:{list(target_normalized_histogram)}')
    #
    # resulting_histogram,resulting_norm_histogram=heuristic_approach(sequence, normalized_histogram, target_normalized_histogram)
    #
    # target_byte_sequence=append_bytes_given_target_histogram(sequence, histogram,resulting_histogram)
    #
    # print(len(target_byte_sequence))
    #
    # save_modified_binary_file(output_filepath, target_byte_sequence)

