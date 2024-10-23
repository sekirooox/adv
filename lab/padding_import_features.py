import os
import numpy as np

# Define directories for benign and malicious features
dir1 = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\benign'
dir2 = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\malicious'

# Define output directories
output_dir1 = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\padding\benign'
output_dir2 = r'C:\Users\ASUS\PycharmProjects\pythonProject\adv_mlw_examples_generation_with_gans-main\npz\BODMAS\strings_features\padding\malicious'

# Create output directories if they don't exist
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)


# Function to load, modify, and save npz files
def modify_and_save_npz(directory, output_directory,target_len):
    for filename in os.listdir(directory):
        if filename.endswith('.npz'):
            file_path = os.path.join(directory, filename)
            data = np.load(file_path)
            modified_data = {}

            for key in data.keys():
                array = data[key]
                # Adjust the dimension to 18820
                if array.shape[0] < target_len:
                    # Pad with zeros if the array is shorter
                    padding = np.zeros(target_len - array.shape[0])
                    modified_array = np.concatenate((array, padding))
                else:
                    # Trim if the array is longer
                    modified_array = array[:target_len]

                modified_data[key] = modified_array

            # Save the modified data to the new directory
            np.savez_compressed(os.path.join(output_directory, filename), **modified_data)

target_len=26825
# Modify and save npz files for benign features
modify_and_save_npz(dir1, output_dir1,target_len)

# Modify and save npz files for malicious features
modify_and_save_npz(dir2, output_dir2,target_len)

print("Modification complete. Files saved in the specified output directories.")
