import pandas as pd
import numpy as np
import os
# dir1=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious' # 生成的byte特征向量
# dir2=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\histogram_features\malicious_target'

# dir1=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\malicious' # 原始string特征向量
# dir2=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\benign'
# dir1=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\malicious' # 原始string特征向量
# dir2=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\malicious_target'
dir1=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\imports_features\baseline\malicious'# 原始mport特征向量
dir2=r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\imports_features\baseline\malicious_target'

max_shape=0

for filename1,filename2 in zip(os.listdir(dir1),os.listdir(dir2)):
    if filename1.endswith('.npz'):
        file_path = os.path.join(dir1, filename1)
        data = np.load(file_path)
        # print(f"File1: {filename1}")
        for key in data.keys():
            print(f" file1 {key}: {data[key].shape}")
            print(list(data[key])[:16])
    if filename2.endswith('.npz'):
        file_path = os.path.join(dir2, filename2)
        data = np.load(file_path)
        # print(f"File2: {filename2}")
        for key in data.keys():
            print(f" file2 {key}: {data[key].shape}\n")
            print(list(data[key])[:16])
            if data[key].shape[0] > max_shape:
                max_shape = data[key].shape[0]
    break
    # break
print(F'max_shape is {max_shape}')
# for filename in os.listdir(dir1):
#     if filename.endswith('.npz'):
#         file_path = os.path.join(dir1, filename)
#         data = np.load(file_path)
#         print(f"File: {filename}")
#         for key in data.keys():
#             print(f"  {key}: {data[key].shape}")
#
# for filename in os.listdir(dir2):
#     if filename.endswith('.npz'):
#         file_path = os.path.join(dir2, filename)
#         data = np.load(file_path)
#         print(f"File: {filename}")
#         for key in data.keys():
#             print(f"  {key}: {data[key].shape}")
