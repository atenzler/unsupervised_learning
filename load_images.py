import math
import subprocess
from typing import Optional, Union
import json
import os

import h5py
import matplotlib.pyplot as plt
import torch
from matplotlib.pyplot import tight_layout

from artist.raytracing.heliostat_tracing import HeliostatRayTracer
from artist.scenario import Scenario

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



scenario_name = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\Scenario.h5"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the incident ray direction
sun_position = torch.tensor([0.8, 0.0, 0.5, 0.0], device=device)


heliostat_list = ["BE41","AA26"]
image_list = []

# Load a scenario.
with h5py.File(scenario_name, "r") as f:
    example_scenario = Scenario.load_scenario_from_hdf5(scenario_file=f, device=device)


# Inspect the scenario.
print(example_scenario)
print(f"The light source is a {example_scenario.light_sources.light_source_list[0]}")
print(
    f"The receiver type is {example_scenario.receivers.receiver_list[0].receiver_type}"
)
single_heliostat = example_scenario.heliostats.heliostat_list[0]
print(single_heliostat)
print(f"The heliostat position is: {single_heliostat.position}")
print(f"The heliostat is aiming at: {single_heliostat.aim_point}")


for helio_name in heliostat_list:

    # Load the JSON file of properties for heliostat position
    file_path = (fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio_name}\Properties\{helio_name}-heliostat-properties.json")

    with open(file_path, "r") as file:
        data = json.load(file)

    print(data)

    # Extract data into variables
    heliostat_position = torch.tensor(data["heliostat_position"])
    height = data["height"]
    width = data["width"]

    kinematic_properties = data["kinematic_properties"]
    facet_properties = data["facet_properties"]

    single_heliostat.position = heliostat_position
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
        print(facet)
        #translation_vector = nurbs[facet]["translation_vector"]
        #canting_e = nurbs[facet]["canting_e"]
        #canting_n = nurbs[facet]["canting_n"]
        control_points = nurbs[facet]["control_points"]
        facets.append({
            #"translation_vector": translation_vector,
            #"canting_e": canting_e,
            #"canting_n": canting_n,
            "control_points": control_points
        })

    print(facets[0]["control_points"])

    # Update control points (assuming they're stored in "control_points" under "facet_properties")
    for i, facet in enumerate(facet_properties["facets"]):
        control_points = facets[i]["control_points"]
        single_heliostat.facet_properties["facets"][i]["control_points"] = control_points

    example_scenario.heliostats.heliostat_list[0] = single_heliostat

    # Save original surface points.
    #original_surface_points, _ = single_heliostat.surface.get_surface_points_and_normals(
    #    device=device
    #)

    # Align the heliostat.
    single_heliostat.set_aligned_surface_with_incident_ray_direction(
        incident_ray_direction=sun_position, device=device
    )

    # Define the raytracer.
    raytracer = HeliostatRayTracer(scenario=example_scenario, batch_size=100)

    # Perform heliostat-based raytracing.
    image = raytracer.trace_rays(
        incident_ray_direction=sun_position, device=device
    )
    image= raytracer.normalize_bitmap(image)

    # Plot the result.
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image.T.cpu().detach().numpy(), cmap="inferno")
    tight_layout()
    #plt.show()

    # Consider multiple incident ray directions and plot the result.
    # Define light directions.
    incident_ray_direction_1 = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device)
    incident_ray_direction_2 = torch.tensor([-1.0, 0.0, 0.0, 0.0], device=device)
    incident_ray_direction_3 = torch.tensor([0.0, 0.0, 1.0, 0.0], device=device)
    incident_ray_direction_4 = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device)
    incident_ray_direction_5 = torch.tensor([-1.0, 0.0, 0.0, 0.0], device=device)
    incident_ray_direction_6 = torch.tensor([0.0, 0.0, 1.0, 0.0], device=device)
    incident_ray_direction_7 = torch.tensor([1.0, 0.0, 0.0, 0.0], device=device)
    incident_ray_direction_8 = torch.tensor([-1.0, 0.0, 0.0, 0.0], device=device)

    # Perform alignment and raytracing to generate flux density images.
    image_1 = align_and_trace_rays(
        light_direction=incident_ray_direction_1, device=device
    )
    image_2 = align_and_trace_rays(
        light_direction=incident_ray_direction_2, device=device
    )
    image_3 = align_and_trace_rays(
        light_direction=incident_ray_direction_3, device=device
    )
    image_4 = align_and_trace_rays(
        light_direction=incident_ray_direction_4, device=device
    )
    image_5 = align_and_trace_rays(
        light_direction=incident_ray_direction_5, device=device
    )
    image_6 = align_and_trace_rays(
        light_direction=incident_ray_direction_6, device=device
    )
    image_7 = align_and_trace_rays(
        light_direction=incident_ray_direction_7, device=device
    )
    image_8 = align_and_trace_rays(
        light_direction=incident_ray_direction_8, device=device
    )

    # Plot the resulting images.
    plot_multiple_images(
        image_1,
        image_2,
        image_3,
        image_4,
        image_5,
        image_6,
        image_7,
        image_8,
        names=["1", "2", "3", "4", "5", "6", "7", "8"],
    )

    # function to save images somewhere!





