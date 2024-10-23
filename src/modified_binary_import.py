import os
import numpy as np
from pe_modifier import PEModifier
import json
def modify_binary_files(input_dir,original_vector_dir, feature_vector_dir, output_dir, inverse_vocabulary_mapping):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录中的所有文件
    for file_name in os.listdir(input_dir):
        input_filepath = os.path.join(input_dir, file_name)

        # 对应的特征向量文件路径
        feature_vector_filename = file_name+'.npz'
        feature_vector_filepath = os.path.join(feature_vector_dir, feature_vector_filename)

        original_vector_filename = file_name + '.npz'
        original_vector_filepath = os.path.join(original_vector_dir, original_vector_filename)

        # 检查特征向量文件是否存在
        if os.path.exists(feature_vector_filepath):
            print(f"Processing: {file_name}")
        #
            # 初始化PEModifier类，读取二进制文件
            pe_modifier = PEModifier(input_filepath)
        #
            # 加载生成的特征向量
            feature_vector = np.load(feature_vector_filepath)['generated_features'].flatten()
            feature_vector=(feature_vector>=0.5).astype(int)

            original_features = np.load(original_vector_filepath)['arr_0'].flatten().astype(int)

            print(feature_vector.shape,feature_vector.dtype,list(feature_vector)[:64])
            print(original_features.shape,original_features.dtype,list(original_features)[:64])

            # 论文中是OR操作，实际操作中只需要注入原文件没有的特征，所以代码中使用XOR
            xor_features = np.bitwise_xor(feature_vector, original_features)
            print(f'the number of imported function:  {(xor_features==1).astype(int).sum()}')

                # 调用add_imports()方法，添加API库和函数
            pe_modifier.add_imports(xor_features, inverse_vocabulary_mapping)
        #
        #     # 保存修改后的文件
            output_filepath = os.path.join(output_dir, file_name)
            modified_bytez, _, _ = pe_modifier._binary_to_bytez(pe_modifier.lief_binary)
            with open(output_filepath, 'wb') as output_file:
                output_file.write(modified_bytez)

            print(f"Modified binary saved to {output_filepath}")
        else:
            print(f"Feature vector not found for {file_name}")

        break

if __name__=='__main__':
    # 假设以下是输入目录、特征向量目录和输出目录
    input_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious'
    original_vector_dir=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\imports_features\baseline\malicious'
    feature_vector_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\imports_features\baseline\malicious_target'
    output_dir = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\malicious_import'
    inverse_vocabulary_path=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\src\feature_extractors\imports_vocabulary\baseline\vocabulary\inverse_vocabulary_mapping_test.json'
    # 逆映射字典
    with open(inverse_vocabulary_path,'r',encoding='utf-8') as f:
        inverse_vocabulary_mapping = json.load(f)
    print(inverse_vocabulary_mapping)

    # 调用函数，批量修改二进制文件
    modify_binary_files(input_dir, original_vector_dir,feature_vector_dir, output_dir, inverse_vocabulary_mapping)
