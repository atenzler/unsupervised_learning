from pathlib import Path
import os
import glob
import shutil


with open(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\defl_list.txt", "r") as file:
    defl_list = [line.strip() for line in file]  # Convert each line to float
    #defl_list = defl_list[:3]

heliostat_names = defl_list
error_list = []

for heliostat_name in heliostat_names:


    # Folder path where the property files are stored
    property_folder = Path(rf"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{heliostat_name}\Properties")

    # Use glob to match files containing both 'filled' and 'deflectometry' in the filename
    property_file_pattern = os.path.join(
        property_folder, "*properties*"
    )

    # Use glob to match files (brauchte ich weil die Dateien immer anders heißen wegen Datum etc.)
    property_files = glob.glob(property_file_pattern)

    # Ensure we found the correct files
    if not property_files:
        print(f"No property file found for {heliostat_name}")
        error_list.append(heliostat_name)
        continue

    # Take the first matched file (assuming only one match per heliostat)
    property_file_path = Path(property_files[0])

    new_folder_path = Path(fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\streamlined_defl_data\{heliostat_name}")
    # Create the folder
    #os.makedirs(new_folder_path)
    #print(f"Folder created at {new_folder_path}")

    # Define the full destination file path (file will have the same name in the destination directory)
    destination_file_path = new_folder_path / property_file_path.name

    shutil.copy(property_file_path, new_folder_path)

print(len(error_list))

# Define the directory to check
directory_path = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\streamlined_defl_data"

# Define the list of folder names to check
folders_to_delete = error_list

# Get all folder names in the directory
existing_folders = [f for f in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, f))]

# Iterate through the list and delete matching folders
for folder in folders_to_delete:
    folder_path = os.path.join(directory_path, folder)
    if folder in existing_folders:
        shutil.rmtree(folder_path)  # Deletes the folder and its contents
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder not found: {folder}")

"""for heliostat_name in heliostat_names:


    # Folder path where the deflectometry files are stored
    deflectometry_folder = Path(rf"Unsupervised_learning\Data\Deflectometry_Daten\{heliostat_name}\Deflectometry")

    # Use glob to match files containing both 'filled' and 'deflectometry' in the filename
    deflectometry_file_pattern = os.path.join(
        deflectometry_folder, "*filled*-*deflectometry*"
    )

    # Use glob to match files (brauchte ich weil die Dateien immer anders heißen wegen Datum etc.)
    deflectometry_files = glob.glob(deflectometry_file_pattern)

    # Ensure we found the correct files
    if not deflectometry_files:
        print(f"No deflectometry file found for {heliostat_name}")
        continue

    # Take the first matched file (assuming only one match per heliostat)
    deflectometry_file_path = Path(deflectometry_files[0])

    new_folder_path = Path(fr"C:Unsupervised_learning\Data\streamlined_defl_data\{heliostat_name}")
    # Create the folder
    os.makedirs(new_folder_path)
    print(f"Folder created at {new_folder_path}")

    # Define the full destination file path (file will have the same name in the destination directory)
    destination_file_path = new_folder_path / deflectometry_file_path.name

    shutil.copy(deflectometry_file_path, new_folder_path)"""
