import math
from typing import Optional, Union
import json
import h5py
import matplotlib.pyplot as plt
import torch
from matplotlib.pyplot import tight_layout


from artist.util.utils import convert_wgs84_coordinates_to_local_enu
from artist.util.utils import convert_3d_point_to_4d_format
from artist.raytracing.heliostat_tracing import HeliostatRayTracer
from artist.scenario import Scenario
from artist.util.configuration_classes import SurfaceConfig
from artist.field.heliostat import Heliostat


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
norm = torch.linalg.norm(sunPos_LD)
sunPos_LD = sunPos_LD/norm
sun_position = sunPos_LD

power_plant_position=torch.tensor([50.91342112259258, 6.387824755874856, 87.0], device=device) #nicht als enu gespeichert weil das der referenz punkt ist.
power_plant_position_enu=convert_wgs84_coordinates_to_local_enu(power_plant_position, power_plant_position, device)

heliostat_list = ["AA23", "AA39"]
image_list = []
aim_point_area = "solar_tower_juelich_upper"

# Load a scenario.
with h5py.File(scenario_name, "r") as f:
    example_scenario = Scenario.load_scenario_from_hdf5(scenario_file=f, device=device)

light_source = example_scenario.light_sources.light_source_list[0]
light_source.number_of_rays = 200
example_scenario.light_sources.light_source_list[0] = light_source

target_area = example_scenario.target_areas.target_area_list[0]
target_area.plane_e = 8.629666667
target_area.plane_u = 7.0

single_heliostat = example_scenario.heliostats.heliostat_list[0]

aim_point_upper_target = [50.91339203684, 6.38782456351324, 130.097666666667]
aim_point_lower_target = [50.91339203684, 6.38782456351324, 122.8815]
aim_point_multifocus = [50.913396450887, 6.38757443672805, 138.97975]

"""solar_tower_juelich_upper centre coordinates aus PAINT genommen"""
heliostat_aim_point = torch.tensor(aim_point_upper_target, device=device)
heliostat_aim_point_enu = convert_wgs84_coordinates_to_local_enu(heliostat_aim_point, power_plant_position, device)
heliostat_aim_point_enu = convert_3d_point_to_4d_format(heliostat_aim_point_enu, device = device)

target_area.position_center = heliostat_aim_point_enu
example_scenario.target_areas.target_area_list[0] = target_area

for helio_name in heliostat_list:

    # Load the JSON file of properties for heliostat position
    file_path = (fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio_name}\Properties\{helio_name}-heliostat-properties.json")

    with open(file_path, "r") as file:
        data = json.load(file)
    # Extract data into variables
    heliostat_position = torch.tensor(data["heliostat_position"])
    heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
    heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device = device)
    #height = data["height"]
    #width = data["width"]

    # kinematic properties sowie facet properties sind im eingeladnen Scenario nicht angegeben, koennen also spater einfach definiert werden
    #kinematic_properties = data["kinematic_properties"]
    #facet_properties = data["facet_properties"]

    single_heliostat.position = heliostat_position_enu
    single_heliostat.kinematic.position = heliostat_position_enu  #--> kinematic properties have to be overwritten, eigentlich muessten die anderen kinematischen Parameter gleich bleiben
    single_heliostat.aim_point = heliostat_aim_point_enu
    single_heliostat.kinematic.aim_point = heliostat_aim_point_enu
    #single_heliostat.height = height
    #single_heliostat.width = width
    #single_heliostat.kinematic_properties = kinematic_properties
    #single_heliostat.facet_properties = facet_properties

    # Load the NURBS JSON file
    file_path_nurbs = fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\nurbs_files\share\PAINT\{helio_name}\Deflectometry\{helio_name}_nurbs.json"
    with open(file_path_nurbs, "r") as file:
        nurbs = json.load(file)

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

    # Update control points and canting
    for i, facet in enumerate(single_heliostat.surface.facets):
        control_points = torch.tensor(facets[i]["control_points"], device=device)
        single_heliostat.surface.facets[i].control_points = control_points

        translation_vector = torch.tensor(facets[i]["translation_vector"], device=device)
        single_heliostat.surface.facets[i].translation_vector = translation_vector

        canting_e = torch.tensor(facets[i]["canting_e"], device=device)
        single_heliostat.surface.facets[i].canting_e = canting_e
        canting_n = torch.tensor(facets[i]["canting_n"], device=device)
        single_heliostat.surface.facets[i].canting_n = canting_n

    example_scenario.heliostats.heliostat_list[0] = single_heliostat

    print("test")
    facet_num = [0, 1, 2, 3]
    for i in facet_num:
        print(single_heliostat.surface.facets[i].canting_e)
        print(single_heliostat.surface.facets[i].canting_n)
        print(single_heliostat.surface.facets[i].translation_vector)
        print(single_heliostat.surface.facets[i].control_points)
        print(single_heliostat.surface.facets[i].control_points.shape)

    # Align the heliostat.
    single_heliostat.set_aligned_surface_with_incident_ray_direction(
        incident_ray_direction=sun_position, device=device
    )

    # Define the raytracer.
    raytracer = HeliostatRayTracer(
        scenario=example_scenario,
        batch_size=100,
        aim_point_area = aim_point_area
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



