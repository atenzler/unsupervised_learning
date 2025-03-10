import math
import subprocess
from typing import Optional, Union
import json
import os

import h5py
import matplotlib.pyplot as plt
import torch
from matplotlib.pyplot import tight_layout

#from Unsupervised_learning.test_scenario_loading import translation_vector
from artist.util import config_dictionary
from artist.util.utils import convert_wgs84_coordinates_to_local_enu
from artist.util.utils import convert_3d_point_to_4d_format, convert_3d_direction_to_4d_format
from artist.util.configuration_classes import SurfaceConfig
from artist.raytracing.heliostat_tracing import HeliostatRayTracer
from artist.scenario import Scenario
from artist.field.heliostat import Heliostat
from artist.util.configuration_classes import HeliostatConfig
from artist.util.configuration_classes import ActuatorConfig, ActuatorPrototypeConfig

def compare_tensors(tensor1, tensor2):
    """
    Compare two tensors for equality.

    Args:
        tensor1 (torch.Tensor): First tensor to compare.
        tensor2 (torch.Tensor): Second tensor to compare.

    Returns:
        bool: True if the tensors are the same, False otherwise.
    """
    # Check if the shapes are the same
    if tensor1.shape != tensor2.shape:
        print("Tensors have different shapes.")
        return False

    # Check if all elements are the same
    are_equal = torch.equal(tensor1, tensor2)
    if are_equal:
        print("Tensors are the same.")
    else:
        print("Tensors are different.")
    return are_equal


def calculate_mae(tensor1, tensor2):
    """
    Calculate the Mean Absolute Error (MAE) between two tensors.

    Args:
        tensor1 (torch.Tensor): First tensor.
        tensor2 (torch.Tensor): Second tensor.

    Returns:
        float: The MAE between the two tensors.
    """
    # Ensure the tensors have the same shape
    if tensor1.shape != tensor2.shape:
        raise ValueError("Tensors must have the same shape to calculate MAE.")

    # Compute the MAE
    mae = torch.mean(torch.abs(tensor1 - tensor2))
    return mae.item()  # Convert to a Python float for easy readability


scenario_name = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\AA39\Scenario_upper_centre_1_cov.h5"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the incident ray direction

sunPos_LD = torch.tensor([0.0, 0.46, 0.89, 0], device=device) #muesste schon in enu sein
#sunPos_LD = convert_3d_point_to_4d_format(sunPos_LD, device = device)
#print(sunPos_LD)
norm = torch.linalg.norm(sunPos_LD)
sunPos_LD = sunPos_LD/norm
sun_position = sunPos_LD

power_plant_position=torch.tensor([50.91342112259258, 6.387824755874856, 87.0], device=device) #nicht als enu gespeichert weil das der referenz punkt ist.
power_plant_position_enu=convert_wgs84_coordinates_to_local_enu(power_plant_position, power_plant_position, device)



heliostat_list = ["AA39", "AA23"]
image_list = []
aim_point_area = "solar_tower_juelich_upper"

# Load a scenario.
with h5py.File(scenario_name, "r") as f:
    example_scenario = Scenario.load_scenario_from_hdf5(scenario_file=f, device=device)

print("canting_n")
print(example_scenario.heliostats.heliostat_list[0].surface.facets[0].canting_n)


#power_plant_position_scenario = convert_3d_point_to_4d_format(power_plant_position_enu, device = device)
#print(power_plant_position_scenario)
#example_scenario.power_plant_position = power_plant_position_scenario

# Inspect the scenario.
print(example_scenario)

single_heliostat = example_scenario.heliostats.heliostat_list[0]
print(single_heliostat.position)
print(single_heliostat.kinematic.position)
print(single_heliostat.aim_point)
print(single_heliostat.kinematic.aim_point)
#single_heliostat_1.aim_point =
#single_heliostat_1.id =
#single_heliostat_1.position =
#single_heliostat_1.kinematic.position=


light_source = example_scenario.light_sources.light_source_list[0]
#light_source.type =
light_source.number_of_rays = 200
light_source.covariance = 10*4.3681e-06
example_scenario.light_sources.light_source_list[0] = light_source

#Actuator? Im scenario werden zwei ideal Actuators genommen, aber wo kann ich das im example_scneario sehen?


target_area = example_scenario.target_areas.target_area_list[0]
target_area.plane_e = 8.629666667
target_area.plane_u = 7.0
#receiver.position_center =
#receiver.resolution_e =
#receiver.resolution_u =
#receiver.type =

print(target_area.geometry)
print(target_area.center)
print(target_area.normal_vector)
print(target_area.curvature_e)
print(target_area.curvature_u)




#receiver_centre = torch.tensor([50.91341660151, 6.387825304776098, 142.22674999999998], device = device) --> egal, weil aim point mit receiver gleichgesetzt
#receiver_centre_enu = convert_wgs84_coordinates_to_local_enu(receiver_centre, power_plant_position, device)
#receiver_centre_enu = convert_3d_point_to_4d_format(receiver_centre_enu, device = device)
#print("receiver centre in enu")
#print(receiver_centre_enu)
#receiver.position_center = receiver_centre_enu

#example_scenario.receivers.receiver_list[0] = receiver




"""solar_tower_juelich_upper centre coordinates aus PAINT genommen"""
heliostat_aim_point = torch.tensor([50.91339203683997, 6.387824563513243, 130.09766666666667], device=device)
heliostat_aim_point_enu = convert_wgs84_coordinates_to_local_enu(heliostat_aim_point, power_plant_position, device)
heliostat_aim_point_enu = convert_3d_point_to_4d_format(heliostat_aim_point_enu, device = device)
print(heliostat_aim_point_enu)

target_area.position_center = heliostat_aim_point_enu
example_scenario.target_areas.target_area_list[0] = target_area
print()

for helio_name in heliostat_list:

    # Load the JSON file of properties for heliostat position
    file_path = (fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio_name}\Properties\{helio_name}-heliostat-properties.json")

    with open(file_path, "r") as file:
        data = json.load(file)

    print(data)

    # Extract data into variables
    heliostat_position = torch.tensor(data["heliostat_position"])
    heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
    heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device = device)
    print("heliostat_position_enu")
    print(heliostat_position_enu)
    height = data["height"]
    width = data["width"]

    # kinematic properties sowie facet properties sind im eingeladnen Scenario nicht angegeben, koennen also spater einfach definiert werden
    kinematic_properties = data["kinematic_properties"]
    facet_properties = data["facet_properties"]
    print(kinematic_properties)
    print(facet_properties)
    print(facet_properties["facets"][0]["translation_vector"])

    single_heliostat.position = heliostat_position_enu
    single_heliostat.kinematic.position = heliostat_position_enu  #--> kinematic properties have to be overwritten, eigentlich muessten die anderen kinematischen Parameter gleich bleiben
    single_heliostat.aim_point = heliostat_aim_point_enu
    single_heliostat.kinematic.aim_point = heliostat_aim_point_enu
    print(single_heliostat.position)
    print(single_heliostat.kinematic.position)
    print(single_heliostat.aim_point)
    print(single_heliostat.kinematic.aim_point)
    single_heliostat.height = height
    single_heliostat.width = width

    single_heliostat.kinematic_properties = kinematic_properties
    single_heliostat.facet_properties = facet_properties



    # Load the NURBS JSON file
    file_path_nurbs = fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\nurbs_files\share\PAINT\{helio_name}\Deflectometry\{helio_name}_nurbs.json"
    with open(file_path_nurbs, "r") as file:
        nurbs = json.load(file)

    print(nurbs)
    print(f"nurbs (type: {type(nurbs)}): {nurbs}")

    # Define facet details
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

    print("canting list")
    print(facet_properties["facets"])
    #print(facets[0]["canting_e"])
    #print(single_heliostat.facet_properties["facets"][0]["control_points"]) geht nicht weil control points so nicht existiert in diesem Dic
    #print(single_heliostat.facet_properties["facets"][0]["canting_e"])
    print(single_heliostat.surface.facets[0].canting_e) #control points nicht hier, sondern in surface!!!!!!!!!!!!!



    # Update control points and canting
    for i, facet in enumerate(single_heliostat.surface.facets):
        print(facet.control_points)    # Writing it this way could also work, but does it change anything?                               #facet_properties["facets"]
        control_points = torch.tensor(facets[i]["control_points"], device=device)
        control_points[:, :, 2] = 0
        print("0?")
        single_heliostat.surface.facets[i].control_points = control_points
        print(single_heliostat.surface.facets[i].control_points)
        print(single_heliostat.surface.facets[i].control_points.shape)
        print("ENDE")

        translation_vector = torch.tensor(facets[i]["translation_vector"], device=device)
        print(single_heliostat.surface.facets[i].translation_vector)
        single_heliostat.surface.facets[i].translation_vector = translation_vector
        print(single_heliostat.surface.facets[i].translation_vector)

        canting_e = torch.tensor(facets[i]["canting_e"], device=device)
        #canting_e = torch.tensor([0.0, 0.0, 1.0, 0.0], device=device)
        print(single_heliostat.surface.facets[i].canting_e)                   # single_heliostat.facet_properties["facets"][i]["canting_e"]
        print(len(single_heliostat.surface.facets[i].canting_e))
        single_heliostat.surface.facets[i].canting_e = canting_e
        print(single_heliostat.surface.facets[i].canting_e)                   # single_heliostat.facet_properties["facets"][i]["canting_e"]
        print(len(single_heliostat.surface.facets[i].canting_e))
        canting_n = torch.tensor(facets[i]["canting_n"], device=device)
        #canting_n = torch.tensor([0.0, 0.0, 1.0, 0.0], device=device)
        single_heliostat.surface.facets[i].canting_n = canting_n


    #print("single_heliostat.facet_properties")
    #print(single_heliostat.facet_properties["facets"][0]["control_points"])
    #print(single_heliostat.facet_properties["facets"][0]["canting_e"])


    example_scenario.heliostats.heliostat_list[0] = single_heliostat
    #print("example_scenario.heliostats.heliostat_list[0]")
    #print(example_scenario.heliostats.heliostat_list[0].position)

    print("test")
    facet_num = [0, 1, 2, 3]
    for i in facet_num:
        print(single_heliostat.surface.facets[i].canting_e)
        print(single_heliostat.surface.facets[i].canting_n)
        print(single_heliostat.surface.facets[i].translation_vector)
        print(single_heliostat.surface.facets[i].control_points)
        print(single_heliostat.surface.facets[i].control_points.shape)

    single_heliostat.surface_points, single_heliostat.surface_normals = (
        single_heliostat.surface.get_surface_points_and_normals(device=device))


    # Align the heliostat.
    single_heliostat.set_aligned_surface_with_incident_ray_direction(
        incident_ray_direction=sun_position, device=device
    )

    # Define the raytracer.
    raytracer = HeliostatRayTracer(
        scenario=example_scenario,
        batch_size=100,
        aim_point_area=aim_point_area,
        heliostat_index=0
    )


    # Perform heliostat-based raytracing.
    image = raytracer.trace_rays(
        incident_ray_direction=sun_position, device=device
    )
    image= raytracer.normalize_bitmap(image)

    # Plot the result.
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image.T.cpu().detach().numpy(), cmap="inferno")
    tight_layout()
    plt.show()

    image_list.append(image)

    print(f"Raytracer Inputs for {helio_name}:")
    print(f"Heliostat Position: {single_heliostat.position}")
    print(f"Heliostat Aligned Surface Points: {single_heliostat.current_aligned_surface_points}")

#print(image_list[0]), print(image_list[1])
#compare_tensors(image_list[0], image_list[1])
#compare_tensors(image_list[0], image_list[2])

# Calculate the MAE
#mae = calculate_mae(image_list[0], image_list[1])
#print(f"The Mean Absolute Error (MAE) between the tensors is: {mae}")

# Define helper functions to enable us to repeat the process!
def align_and_trace_rays(
    light_direction: torch.Tensor, device: Union[torch.device, str] = "cuda"
) -> torch.Tensor:
    """
    Align the heliostat and perform heliostat raytracing.

    Parameters
    ----------
    light_direction : torch.Tensor
        The direction of the incoming light on the heliostat.
    device : Union[torch.device, str]
        The device on which to initialize tensors (default: cuda).

    Returns
    -------
    torch.Tensor
        A tensor containing the distribution strengths used to generate the image on the receiver.
    """
    single_heliostat.set_aligned_surface_with_incident_ray_direction(
        incident_ray_direction=light_direction, device=device
    )
    return raytracer.normalize_bitmap(
        raytracer.trace_rays(incident_ray_direction=light_direction, device=device)
    )


def plot_multiple_images(
    *image_tensors: torch.Tensor, names: Optional[list[str]] = None
) -> None:
    """
    Plot multiple receiver raytracing images in a grid.

    This function is flexible and able to plot an arbitrary number of images depending on the number of image tensors
    provided. Note that the list of names must be the same length as the number of provided images, otherwise the images
    will be untitled.

    Parameters
    ----------
    image_tensors : torch.Tensor
        An arbitrary number of image tensors to be plotted.
    names : list[str], optional
        The names of the images to be plotted.
    """
    # Calculate the number of images and determine the size of the grid based on the number of images.
    n = len(image_tensors)
    grid_size = math.ceil(math.sqrt(n))

    # Create a subplot with the appropriate size.
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(10, 10))

    # Flatten axes array for easy iteration if it's more than 1D.
    if grid_size > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    # Plot each tensor.
    for i, image in enumerate(image_tensors):
        ax = axes[i]
        ax.imshow(image.T.cpu().detach().numpy(), cmap="inferno")
        if names is not None and i < len(names):
            ax.set_title(names[i])
        else:
            ax.set_title(f"Untitled Image {i+1}")

    # Hide unused subplots.
    for j in range(i + 1, grid_size * grid_size):
        axes[j].axis("off")

    plt.tight_layout()
    plt.show()


"""# Consider multiple incident ray directions and plot the result.
# Define light directions.
incident_ray_direction_east = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device)
incident_ray_direction_west = torch.tensor([-1.0, 0.0, 0.0, 0.0], device=device)
incident_ray_direction_above = torch.tensor([0.0, 0.0, 1.0, 0.0], device=device)

# Perform alignment and raytracing to generate flux density images.
image_east = align_and_trace_rays(
    light_direction=incident_ray_direction_east, device=device
)
image_west = align_and_trace_rays(
    light_direction=incident_ray_direction_west, device=device
)
image_above = align_and_trace_rays(
    light_direction=incident_ray_direction_above, device=device
)

# Plot the resulting images.
plot_multiple_images(
    image_south,
    image_east,
    image_west,
    image_above,
    names=["South", "East", "West", "Above"],
)
"""


