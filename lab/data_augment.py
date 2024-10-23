import os
import shutil
import random
import string


def random_string(length=8):
    """生成一个随机字符串，防止文件名冲突"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def augment_files(src_dir, dst_dir, copies=30):
    """将源文件夹中的所有文件复制指定次数到目标文件夹"""
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    for filename in os.listdir(src_dir):
        # 检查是否为文件（避免处理子目录）
        src_file_path = os.path.join(src_dir, filename)
        if os.path.isfile(src_file_path):
            name, ext = os.path.splitext(filename)
            for i in range(copies):
                new_filename = f"{name}_{i}{ext}"
                dst_file_path = os.path.join(dst_dir, new_filename)

                # 如果文件已存在，随机生成一个文件名
                while os.path.exists(dst_file_path):
                    new_filename = f"{name}_{random_string()}{ext}"
                    dst_file_path = os.path.join(dst_dir, new_filename)

                # 复制文件到目标目录
                shutil.copy(src_file_path, dst_file_path)
                print(f"Copied {src_file_path} to {dst_file_path}")


if __name__ == "__main__":
    # 替换为你自己的源文件夹和目标文件夹路径
    src_directory = r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\benign"  # 源文件夹路径
    dst_directory = r"C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\raw\BODMAS\benign_augmented"  # 目标文件夹路径

    augment_files(src_directory, dst_directory, copies=30)
