import sys
sys.path.append("/home/nfs/atenzler")  # Add the parent directory of 'util'

from util.surface_converter import SurfaceConverter
from util import config_dictionary, set_logger_config

from joblib import Parallel, delayed
from pathlib import Path
import glob
import os
import json
import torch
import fcntl
import logging

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

# Path to the single JSON file
final_save_path = Path("/home/nfs/atenzler/all_heliostat_surfaces.json")

# Function to safely append to JSON
def append_to_json(heliostat_name, heliostat_data):
    """Append heliostat data to the main JSON file in a safe way."""
    try:
        # Ensure file exists before reading
        if not final_save_path.exists():
            with open(final_save_path, "w") as f:
                json.dump({}, f)  # Create an empty dictionary

        # Lock file for safe writing
        with open(final_save_path, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # Lock file
            existing_data = json.load(f)  # Read current data
            existing_data[heliostat_name] = heliostat_data  # Append new data

            # Write updated data back
            f.seek(0)
            json.dump(existing_data, f, indent=4)
            f.truncate()  # Remove any extra content
            fcntl.flock(f, fcntl.LOCK_UN)  # Unlock file

    except Exception as e:
        logger.error(f"Failed to append data for {heliostat_name}: {e}")



def process_heliostat(heliostat_name):
    """Function to process a single heliostat."""
    try:
        write_log(f"Processing heliostat: {heliostat_name}")

        deflectometry_folder = Path(f"/home/nfs/atenzler/streamlined_defl_data/{heliostat_name}")
        deflectometry_file_pattern = os.path.join(deflectometry_folder, "*filled*-*deflectometry*")
        deflectometry_files = glob.glob(deflectometry_file_pattern)

        if not deflectometry_files:
            print(f"No deflectometry file found for {heliostat_name}")
            return None

        deflectometry_file_path = Path(deflectometry_files[0])
        heliostat_file_path = Path(
            f"/home/nfs/atenzler/streamlined_defl_data/{heliostat_name}/{heliostat_name}-heliostat-properties.json")

        # Generate surface configuration
        surface_converter = SurfaceConverter(
            number_eval_points_e=100, number_eval_points_n=100,
            conversion_method=config_dictionary.convert_nurbs_from_normals,
            number_control_points_e=8, number_control_points_n=8,
            degree_e=3, degree_n=3, tolerance=3e-5, max_epoch=1000,
            initial_learning_rate=1e-3, step_size=100,
            optimize_only_z_cntrl_points=True
        )

        facet_list = surface_converter.generate_surface_config_from_paint(
            deflectometry_file_path=deflectometry_file_path,
            heliostat_file_path=heliostat_file_path,
            device=device
        )

        # Prepare output data
        combined_data = {
            f"facet_{i + 1}": {
                "facet_key": facet.facet_key,
                "control_points": facet.control_points.tolist(),
                "degree_e": facet.degree_e,
                "degree_n": facet.degree_n,
                "number_eval_points_e": facet.number_eval_points_e,
                "number_eval_points_n": facet.number_eval_points_n,
                "translation_vector": facet.translation_vector.tolist(),
                "canting_e": facet.canting_e.tolist(),
                "canting_n": facet.canting_n.tolist(),
            } for i, facet in enumerate(facet_list)
        }

        # Append to the JSON file immediately
        append_to_json(heliostat_name, combined_data)

        return {heliostat_name: combined_data}

    except Exception as e:
        print(f"Error processing {heliostat_name}: {e}")
        return None


# Read heliostat names from the file
with open("/home/nfs/atenzler/defl_list.txt", "r") as file:
    heliostat_names = [line.strip() for line in file]

# Run multiple heliostats in parallel
num_cores = min(8, os.cpu_count())  # Use 8 cores, or max available
heliostat_data_list = Parallel(n_jobs=num_cores)(delayed(process_heliostat)(h) for h in heliostat_names)

