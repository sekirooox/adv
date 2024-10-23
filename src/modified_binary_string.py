import os
import numpy as np
from pe_modifier import PEModifier
import random
# 加载section_names.txt
from src.feature_extractors import strings_extractor
from src.feature_extractors.strings_extractor import StringsExtractor
import json

# 功能函数：处理一个文件
def process_file(npz_file_path, binary_file_path, original_vector_file_path,output_file_path,vocabulary_dict,inverse_vocabulary_dict):
    # 读取生成的特征向量
    generated_data = np.load(npz_file_path)
    original_data = np.load(original_vector_file_path)

    # 获取新的生成特征向量和原始特征向量,注意数据类型为float32,要修改为int类型
    generated_features = generated_data['generated_features']
    original_features = original_data['arr_0']

    generated_features=(generated_features>=0.5).astype(int)
    original_features=original_features.astype(int)

    # 将生成器生成的 (1, 15888) 转换为 (15888,)
    generated_features = np.squeeze(generated_features)



    # print(f"Original features: {list(original_features)[:16]}")
    # print(f"Generated features: {list(generated_features)[:16]}")
    # print(f"Generated features shape: {generated_features.shape}")
    # print(f"Original features shape: {original_features.shape}")

    # print(original_features.dtype)
    # print(generated_features.dtype)
    # 初始化PEModifier对象
    pe_modifier = PEModifier(binary_file_path)

    # 参照论文3.22节的方式处理，使用strings_extractor反索引注入字符串!!!

    strings_extractor=StringsExtractor(vocabulary_mapping=vocabulary_dict,inverse_vocabulary_mapping=inverse_vocabulary_dict)

    corresponding_strings_to_inject = strings_extractor.retrieve_strings_to_inject(original_features,generated_features,inverse_vocabulary_dict)
    print(f'strings_to_inject:  {corresponding_strings_to_inject}')

    section_content = pe_modifier.strings_to_content(corresponding_strings_to_inject)# 这里是注入内容，已经变成ASCII的形式


    # 注入操作
    if section_content is not None:
        # 为注入的section随机选择一个名称
        section_name = random.choice(COMMON_SECTION_NAMES)[:7]
        pe_modifier.create_new_section(section_content, section_name=section_name)

        # 保存修改后的PE文件
        with open(output_file_path, "wb") as f:
            f.write(pe_modifier.bytez)
    print(f'save to {output_file_path}')

# 主函数：遍历所有npz文件并处理
def modify_binaries(feature_vector_path, original_vector_path, binary_path, output_path,vocabulary_dict,inverse_vocabulary_dic):
    # 遍历feature vector目录中的所有npz文件
    for filename in os.listdir(feature_vector_path):
        if filename.endswith(".npz"):
            # 获取对应的原始二进制文件、原始特征向量文件和输出文件的路径
            binary_file = os.path.join(binary_path, filename.replace(".npz", ""))
            npz_file = os.path.join(feature_vector_path, filename)
            original_vector_file = os.path.join(original_vector_path, filename)
            output_file = os.path.join(output_path, filename.replace(".npz", ""))# exe文件
            # print(binary_file)
            # print(npz_file)
            # print(original_vector_file)
            # print(output_file)

            # 确保原始二进制文件和原始特征向量文件存在
            if os.path.exists(binary_file) and os.path.exists(original_vector_file):
                print(f"Processing: {filename}")
                process_file(npz_file, binary_file, original_vector_file, output_file,vocabulary_dict,inverse_vocabulary_dict)
            else:
                print(f"Binary file or original vector not found for {filename}")
        break


if __name__=='__main__':
    original_vector_path = r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\malicious"
    feature_vector_path = r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\malicious_target"  # 替换为实际路径
    binary_path = r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious"  # 替换为实际路径
    output_path = r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious_string"  # 替换为实际输出路径

    vocabulary_mapping_path = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\feature_extractors\strings_vocabulary\vocabulary\vocabulary_mapping_top20000_test.json'
    inverse_vocabulary_mapping_path = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\feature_extractors\strings_vocabulary\vocabulary\inverse_vocabulary_mapping_top20000_test.json'

    section_path = 'section_names.txt'
    # json->dict
    with open(vocabulary_mapping_path, 'r', encoding='utf-8') as file:
        vocabulary_dict = json.load(file)  #
    with open(inverse_vocabulary_mapping_path, 'r', encoding='utf-8') as file:
        inverse_vocabulary_dict = json.load(file)



    with open(section_path, 'r') as f:
        COMMON_SECTION_NAMES = f.read().rstrip().split('\n')

    modify_binaries(feature_vector_path, original_vector_path, binary_path, output_path,vocabulary_dict,inverse_vocabulary_dict)
