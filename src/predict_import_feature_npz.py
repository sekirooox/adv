import torch
import numpy as np
import os

def load_model(model_path):
    """从给定路径加载训练好的模型"""
    model = torch.load(model_path)
    model.eval()  # 设置模型为评估模式
    return model

def predict_and_save_features(generator_model_path, sample_data_path, output_directory):
    """使用生成器模型生成特征并保存为单个npz文件"""
    # 加载训练好的生成器模型
    generator = load_model(generator_model_path)

    # 获取模型所在的设备
    device = next(generator.parameters()).device

    # 假设您的样本数据为 .npz 格式
    sample_files = os.listdir(sample_data_path)

    for sample_file in sample_files:
        # 加载样本数据
        sample_data = np.load(os.path.join(sample_data_path, sample_file), allow_pickle=True)

        # 打印键以调试
        # print(f"{sample_file} 中的键: {sample_data.keys()}")  # 调试行

        # 使用 'arr_0' 键获取数据
        if 'arr_0' in sample_data:
            g_features = sample_data['arr_0']  # 形状为 (256,)
        else:
            print(f"{sample_file} 中未找到键 'arr_0'。可用的键: {sample_data.keys()}")
            continue  # 如果未找到该键，跳到下一个文件

        # 准备噪声向量
        z_size = 8  # 修改噪声的大小，这个取决于超参数json文件
        noise = torch.randn(1, z_size, device=device)  # 生成一个随机噪声张量，批大小为1，确保在同一设备上

        # 将 g_features 转换为张量并调整维度
        g_features_tensor = torch.tensor(g_features, dtype=torch.float32).view(1, -1).to(device)  # 转换为二维张量，并移动到相同设备

        # 使用生成器生成预测
        with torch.no_grad():  # 禁用梯度计算
            generated_features = generator([g_features_tensor, noise])

        # 将生成的特征转换为 numpy
        generated_features_np = generated_features.cpu().numpy()

        # 保存每个文件生成的特征向量到单独的npz文件
        output_filepath = os.path.join(output_directory, f"{os.path.splitext(sample_file)[0]}.npz")
        np.savez_compressed(output_filepath, generated_features=generated_features_np)
        print(f"保存生成的特征向量到: {output_filepath}")

if __name__ == "__main__":
    # z-size=8
    generator_model_path = 'models/MalGAN_top150_import_features/generator/generator.pt'
    sample_data_path = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\imports_features\baseline\malicious'  # 字节直方图特征的npz文件路径
    output_filepath = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\imports_features\baseline\malicious_target'  # 输出文件路径

    predict_and_save_features(generator_model_path, sample_data_path, output_filepath)
