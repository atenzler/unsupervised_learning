import sys
sys.path.append("/home/nfs/atenzler")  # Add the parent directory of 'util'

from util.surface_converter import SurfaceConverter
from util import config_dictionary, set_logger_config

from pathlib import Path
import torch
import glob
import os
import json
import logging
#import matplotlib.pyplot as plt

# List of heliostat names with deflectometry data

# Set up logger.
set_logger_config()

# Configure logger to output to a file and to console
logger = logging.getLogger(__name__)

# Define the log file path
log_file_path = Path("/home/nfs/atenzler/heliostat_processing_log.txt")

open(log_file_path, "w").close()  # This clears the content without writing anything
# Function to write messages to the log file
def write_log(message):
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")


# Dictionary to store all heliostat data
all_heliostat_data = {}

with open("/home/nfs/atenzler/defl_list.txt", "r") as file:
    defl_list = [line.strip() for line in file]  # Convert each line to float
    #defl_list = defl_list[:3]

heliostat_names = defl_list
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

plot_loss = False

# Write a starting log message
write_log("Started processing heliostats")

#save surfaces in JSON file:
# Define save file path
save_path = Path("/home/nfs/atenzler/all_heliostat_surfaces.json")

# Try to load existing data if available
if save_path.exists():
    with open(save_path, "r") as json_file:
        try:
            all_heliostat_data = json.load(json_file)
        except json.JSONDecodeError:
            all_heliostat_data = {}  # Start fresh if the file is corrupted
else:
    all_heliostat_data = {}  # Start fresh if no file exists

for heliostat_name in heliostat_names:
    # Skip if this heliostat was already processed
    if heliostat_name in all_heliostat_data:
        continue

    # Log the heliostat being worked on
    write_log(f"Processing heliostat: {heliostat_name}")

    # Folder path where the deflectometry files are stored
    deflectometry_folder = Path(f"/home/nfs/atenzler/streamlined_defl_data/{heliostat_name}")

    # Use glob to match files containing both 'filled' and 'deflectometry' in the filename
    deflectometry_file_pattern = os.path.join(
        deflectometry_folder, "*filled*-*deflectometry*"
    )

    # Use glob to match files (brauchte ich weil die Dateien immer anders heißen wegen Datum etc.)
    deflectometry_files = glob.glob(deflectometry_file_pattern)


    # Take the first matched file (assuming only one match per heliostat)
    deflectometry_file_path = Path(deflectometry_files[0])
    heliostat_file_path = Path(f"/home/nfs/atenzler/streamlined_defl_data/{heliostat_name}/{heliostat_name}-heliostat-properties.json")

    # Generate surface configuration from PAINT data.

    surface_converter = SurfaceConverter(number_eval_points_e=100,
        number_eval_points_n=100,
        conversion_method=config_dictionary.convert_nurbs_from_normals,
        number_control_points_e=8,
        number_control_points_n=8,
        degree_e=3,
        degree_n=3,
        tolerance=3e-5,
        max_epoch=1000,
        initial_learning_rate=1e-3,
        step_size=100,
        optimize_only_z_cntrl_points = True
    )

    facet_list = surface_converter.generate_surface_config_from_paint(
        deflectometry_file_path=deflectometry_file_path,
        heliostat_file_path=heliostat_file_path,
        device=device
    )

    #attributes = dir(facet_list[0])

    combined_data = {}
    for i, facet in enumerate(facet_list):
        combined_data[f"facet_{i + 1}"] = {
            "facet_key": facet.facet_key,
            "control_points": facet.control_points.tolist(),  # Convert Tensor to list
            "degree_e": facet.degree_e,
            "degree_n": facet.degree_n,
            "number_eval_points_e": facet.number_eval_points_e,
            "number_eval_points_n": facet.number_eval_points_n,
            #"width": facet.width,
            #"height": facet.height,
            "translation_vector": facet.translation_vector.tolist(),  # Convert Tensor to list
            "canting_e": facet.canting_e.tolist(),  # Convert Tensor to list
            "canting_n": facet.canting_n.tolist(),  # Convert Tensor to list
        }


    all_heliostat_data[heliostat_name] = combined_data  # Store in the main dictionary

    # **Save after each heliostat to avoid losing progress**
    with open(save_path, "w") as json_file:
        json.dump(all_heliostat_data, json_file, indent=4)

    write_log(f"Finished processing {heliostat_name}")


