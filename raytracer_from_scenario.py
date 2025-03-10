import math
import subprocess
from typing import Optional, Union

import h5py
import matplotlib.pyplot as plt
import torch
from matplotlib.pyplot import tight_layout

from artist.raytracing.heliostat_tracing import HeliostatRayTracer
from artist.scenario import Scenario

# If you have already generated the tutorial scenario yourself, you can leave this boolean as False. If not, set it to
# true and a pre-generated scenario file will be downloaded for this tutorial!

helio="AA39"
aim_point_area = "solar_tower_juelich_upper"

scenario_name = fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\{helio}\Scenario_upper_centre_2_cov.h5"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the scenario.
with h5py.File(scenario_name, "r") as f:
    example_scenario = Scenario.load_scenario_from_hdf5(scenario_file=f, device=device)

# Inspect the scenario.
print(example_scenario)
print(f"The light source is a {example_scenario.light_sources.light_source_list[0]}")
print(
    f"The target area type is {example_scenario.target_areas.target_area_list[0]}"
)
single_heliostat = example_scenario.heliostats.heliostat_list[0]
print(f"The heliostat position is: {single_heliostat.position}")
print(f"The heliostat is aiming at: {single_heliostat.aim_point}")


facet_num = [0,1,2,3]
for i in facet_num:
    print(single_heliostat.surface.facets[i].canting_e)
    print(single_heliostat.surface.facets[i].canting_n)
    print(single_heliostat.surface.facets[i].translation_vector)
    print(single_heliostat.surface.facets[i].control_points)
    print(single_heliostat.surface.facets[i].control_points.shape)

# Define the incident ray direction for when the sun is in the south.
sunPos_LD = torch.tensor([0.0, 0.46, 0.89, 0], device=device) #muesste schon in enu sein   #0.0 ,0.46, 0.89, 0.0 -> funktioniert gerade irgendwie nur als Vektor...
#sunPos_LD = convert_3d_point_to_4d_format(sunPos_LD, device = device)
#print(sunPos_LD)
norm = torch.linalg.norm(sunPos_LD)
sunPos_LD = sunPos_LD/norm
incident_ray_direction_south = sunPos_LD


# Save original surface points.
original_surface_points, _ = single_heliostat.surface.get_surface_points_and_normals(
    device=device
)

# Align the heliostat.
single_heliostat.set_aligned_surface_with_incident_ray_direction(
    incident_ray_direction=incident_ray_direction_south, device=device
)

# Define the raytracer.
raytracer = HeliostatRayTracer(
    scenario=example_scenario,
    aim_point_area=aim_point_area,
    batch_size=100
)

# Perform heliostat-based raytracing.
image_south = raytracer.trace_rays(
    incident_ray_direction=incident_ray_direction_south, device=device
)
image_south = raytracer.normalize_bitmap(image_south)

# Plot the result.
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(image_south.T.cpu().detach().numpy(), cmap="inferno")
tight_layout()
plt.show()

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
)"""
