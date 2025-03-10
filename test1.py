import numpy as np
import os

loaded_data = np.load("Data\Heliostat_Positions\heliostat_position_dictionary.npy", allow_pickle=True).item()
print(loaded_data.keys())
print(len(loaded_data))
print(loaded_data["AA23"])

def list_folders_in_directory(directory_path: str) -> list:
    # List all entries in the directory and filter to only include folders
    folder_list = [entry for entry in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, entry))]
    return folder_list




hellist = list_folders_in_directory(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\streamlined_defl_data")

with open(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\defl_list.txt", "w") as f:
    for item in hellist:
        f.write(f"{item}\n")  # Writes each item on a new line
