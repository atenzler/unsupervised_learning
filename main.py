#Check whether or not Delfectometry and Property Data is available
import os
import shutil


def check_and_copy_folders(source_dir, destination_dir, exclude_folders=None):
    # Ensure the destination directory exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # List all folders in the source directory
    all_folders = [f for f in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, f))]

    # Exclude certain folders (if any are specified)
    if exclude_folders:
        all_folders = [folder for folder in all_folders if folder not in exclude_folders]

    # Loop through each folder and check for the required subdirectories
    for folder_name in all_folders:
        # Define the full path to the folder
        folder_path = os.path.join(source_dir, folder_name)

        # Check for the existence of 'Properties' and 'Deflectometry' subdirectories
        deflectometry_path = os.path.join(folder_path, 'Deflectometry')

        # If both subdirectories exist, copy the entire folder
        if os.path.isdir(deflectometry_path):
            print(f"Found valid folder: {folder_name}. Copying...")

            # Define the new path in the destination directory
            destination_folder = os.path.join(destination_dir, folder_name)

            # Copy the folder to the new location
            shutil.copytree(folder_path, destination_folder)
        else:
            print(f"Skipping {folder_name}: 'Deflectometry' is missing.")


# Define the source and destination directories
source_dir = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Heliostats_all"  # Replace with the source directory path
destination_dir = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten"  # Replace with the destination directory path

# Define the list of folders to exclude from the process (optional)
exclude_folders = []  # Add any folders to exclude from processing

# Call the function to check and copy the folders
check_and_copy_folders(source_dir, destination_dir, exclude_folders)