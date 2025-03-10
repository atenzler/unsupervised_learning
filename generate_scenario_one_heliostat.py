# alt

import json
import math
from pathlib import Path
import os

import torch
import glob

from artist import ARTIST_ROOT
from artist.util import config_dictionary, set_logger_config
from artist.util.utils import convert_3d_point_to_4d_format, convert_3d_direction_to_4d_format, convert_wgs84_coordinates_to_local_enu
from artist.util.configuration_classes import (
    ActuatorConfig,
    ActuatorPrototypeConfig,
    HeliostatConfig,
    SurfaceConfig,
    FacetConfig,
    HeliostatListConfig,
    KinematicPrototypeConfig,
    LightSourceConfig,
    LightSourceListConfig,
    PrototypeConfig,
    TargetAreaConfig,
    TargetAreaListConfig,
    PowerPlantConfig,
    SurfacePrototypeConfig, KinematicDeviations,
)
from artist.util.scenario_generator import ScenarioGenerator
from artist.util.surface_converter import SurfaceConverter


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Set up logger.
set_logger_config()

#Define heliostat

helio = "AA39"
aim_point_area = "solar_tower_juelich_upper"


# The following parameter is the name of the scenario.
file_path_scenario = Path(fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\{helio}\Scenario_upper_centre_1_cov")

# Create the parent directory if it does not exist
file_path_scenario.parent.mkdir(parents=True, exist_ok=True)

if not Path(file_path_scenario).parent.is_dir():
    raise FileNotFoundError(
        f"The folder ``{Path(file_path_scenario).parent}`` selected to save the scenario does not exist."
        "Please create the folder or adjust the file path before running again!"
    )

heliostat_file_path=Path(fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio}\Properties\{helio}-heliostat-properties.json")
#deflectometry_file_path=Path(fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio}\Deflectometry\BA70-filled-2023-02-07Z09-53-24Z-deflectometry.h5")

# Folder path where the deflectometry files are stored
deflectometry_folder = Path(
    rf"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio}\Deflectometry")

# Use glob to match files containing both 'filled' and 'deflectometry' in the filename
deflectometry_file_pattern = os.path.join(
    deflectometry_folder, "*filled*-*deflectometry*"
)

# Use glob to match files (brauchte ich weil die Dateien immer anders heißen wegen Datum etc.)
deflectometry_files = glob.glob(deflectometry_file_pattern)

# Take the first matched file (assuming only one match per heliostat)
deflectometry_file_path = Path(deflectometry_files[0])

# Generate surface configuration from PAINT data.
surface_converter = SurfaceConverter(
    step_size=100,
    max_epoch=400,
    number_control_points_e = 8,
    number_control_points_n = 8
)

facet_prototype_list = surface_converter.generate_surface_config_from_paint(
    heliostat_file_path=heliostat_file_path,
    deflectometry_file_path=deflectometry_file_path,
    device=device
)


# Generate the surface prototype configuration.
surface_prototype_config = SurfacePrototypeConfig(facet_list=facet_prototype_list)

power_plant_position=torch.tensor([50.91342112259258, 6.387824755874856, 87.0], device=device)





with open(heliostat_file_path, "r") as file:
    data = json.load(file)

heliostat_position = torch.tensor(data["heliostat_position"])
heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device = device)


aim_point_upper_target = [50.91339203684, 6.38782456351324, 130.097666666667]
aim_point_lower_target = [50.91339203684, 6.38782456351324, 122.8815]
aim_point_multifocus = [50.913396450887, 6.38757443672805, 138.97975]

heliostat_aim_point = torch.tensor(aim_point_upper_target, device=device)
heliostat_aim_point_enu = convert_wgs84_coordinates_to_local_enu(heliostat_aim_point, power_plant_position, device)
heliostat_aim_point_enu = convert_3d_point_to_4d_format(heliostat_aim_point_enu, device = device)


power_plant_position_enu = convert_wgs84_coordinates_to_local_enu(power_plant_position, power_plant_position, device)
print(power_plant_position_enu)

power_plant_config = PowerPlantConfig(
    power_plant_position=power_plant_position_enu
)


heliostat1 = HeliostatConfig(
    name="heliostat1",
    id=1,
    position=heliostat_position_enu,
    aim_point=heliostat_aim_point_enu,
)

# Create a list of all the heliostats - in this case, only one.
heliostat_list = [heliostat1]

# Create the configuration for all heliostats.
heliostats_list_config = HeliostatListConfig(heliostat_list=heliostat_list)

# Include the receiver configuration.
TargetArea1_config = TargetAreaConfig(
    target_area_key=aim_point_area,
    geometry=config_dictionary.target_area_type_planar,
    center=heliostat_aim_point_enu,
    normal_vector=torch.tensor([0.0, 1.0, 0.0, 0.0], device=device),
    plane_e=8.629666667,
    plane_u=7.0,
    curvature_e=0,
    curvature_u=0,
)

# Create list of receiver configs - in this case only one.
target_area_list = [TargetArea1_config]

# Include the configuration for the list of receivers.
target_area_list_config = TargetAreaListConfig(target_area_list=target_area_list)

# Include the light source configuration.
light_source1_config = LightSourceConfig(
    light_source_key="sun1",
    light_source_type=config_dictionary.sun_key,
    number_of_rays=200,
    distribution_type=config_dictionary.light_source_distribution_is_normal,
    mean=0.0,
    covariance=4.3681e-06,
)

# Create a list of light source configs - in this case only one.
light_source_list = [light_source1_config]

# Include the configuration for the list of light sources.
light_source_list_config = LightSourceListConfig(light_source_list=light_source_list)

# Include the kinematic prototype configuration.
kinematic_prototype_config = KinematicPrototypeConfig(
    type=config_dictionary.rigid_body_key,
    initial_orientation=torch.tensor([0.0, 0.0, 1.0, 0.0], device = device)
)

# Include an ideal actuator.
actuator1_prototype = ActuatorConfig(
    key="actuator1",
    type=config_dictionary.ideal_actuator_key,
    clockwise_axis_movement=False,
)

# Include a linear actuator.
actuator2_prototype = ActuatorConfig(
    key="actuator2",
    type=config_dictionary.ideal_actuator_key,
    clockwise_axis_movement=True,
)

# Create a list of actuators.
actuator_prototype_list = [actuator1_prototype, actuator2_prototype]

# Include the actuator prototype config.
actuator_prototype_config = ActuatorPrototypeConfig(
    actuator_list=actuator_prototype_list
)

# Include the final prototype config.
prototype_config = PrototypeConfig(
    surface_prototype=surface_prototype_config,
    kinematic_prototype=kinematic_prototype_config,
    actuators_prototype=actuator_prototype_config,
)

if __name__ == "__main__":
    """Generate the scenario given the defined parameters."""
    # Create a scenario object.
    scenario_object = ScenarioGenerator(
        file_path=file_path_scenario,
        target_area_list_config=target_area_list_config,
        light_source_list_config=light_source_list_config,
        prototype_config=prototype_config,
        heliostat_list_config=heliostats_list_config,
        power_plant_config=power_plant_config
    )

    # Generate the scenario.
    scenario_object.generate_scenario()


"""# Define facet details
facets = []
for facet in nurbs:
    translation_vector = nurbs[facet]["translation_vector"]
    canting_e = nurbs[facet]["canting_e"]
    canting_n = nurbs[facet]["canting_n"]
    control_points = nurbs[facet]["control_points"]
    facets.append({
        "translation_vector": translation_vector,
        "canting_e": canting_e,
        "canting_n": canting_n,
        "control_points": control_points
    })


# Print to verify
print("Heliostat Position:", heliostat_position)
print("Height:", height)
print("Width:", width)
print("Kinematic Properties:", kinematic_properties)
print("Number of Facets:", facet_properties["number_of_facets"])
print("Facets:", facets)
print("Renovation Date:", renovation_date)


facets_data = data["facet_properties"]["facets"]

# Create a list of FacetConfig objects
facet_config_list = []
"""


"""for i, facet in enumerate(facets):
    facet_config = FacetConfig(
        facet_key=f"facet_{i + 1}",  # Unique key for each facet
        control_points=torch.tensor(facets[i]["control_points"], device=device),
        degree_e=3,  # Replace with actual value if available
        degree_n=3,  # Replace with actual value if available
        number_eval_points_e=200,  # Replace with actual value if needed
        number_eval_points_n=200,  # Replace with actual value if needed
        #width=data["width"],
        #height=data["height"],
        translation_vector=torch.tensor(facets[i]["translation_vector"], device=device),
        canting_e=torch.tensor(facets[i]["canting_e"], device=device),
        canting_n=torch.tensor(facets[i]["canting_n"], device=device),
    )
    facet_config_list.append(facet_config)"""

# Create the SurfaceConfig object
#surface_config = SurfaceConfig(facets_list=facet_config_list)

# Generate the surface configuration dictionary
#surface_dict = surface_config.create_surface_dict()

# Print for verification
#print("Surface Configuration Dictionary:")
#print(surface_dict)


# Load the JSON file
#file_path = Path(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\AY39\Properties\AY39-heliostat-properties.json")
#with open(file_path, "r") as file:
#    data = json.load(file)

# Extract data into variables
#heliostat_position = torch.tensor(data["heliostat_position"])
#height = data["height"]
#width = data["width"]

##kinematic_properties = data["kinematic_properties"]
#facet_properties = data["facet_properties"]
#renovation_date = data["renovation"]

#file_path_nurbs = Path(fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\nurbs_files\share\PAINT\AY39\Deflectometry\AY39_nurbs.json")
#with open(file_path_nurbs, "r") as file:
#    nurbs = json.load(file)