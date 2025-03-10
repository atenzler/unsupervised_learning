from Unsupervised_learning.generate_scenario import device
from artist.scenario import Scenario
from artist.field.receiver import Receiver
from artist.field.receiver_field import ReceiverField
from artist.scene.light_source import LightSource
from artist.scene.light_source_array import LightSourceArray
from artist.field.heliostat import Heliostat
from artist.field.heliostat_field import HeliostatField

from artist.util.configuration_classes import (
    ActuatorConfig,
    ActuatorPrototypeConfig,
    HeliostatConfig,
    HeliostatListConfig,
    KinematicPrototypeConfig,
    LightSourceConfig,
    LightSourceListConfig,
    PowerPlantConfig,
    PrototypeConfig,
    ReceiverConfig,
    ReceiverListConfig,
    SurfacePrototypeConfig,
    SurfaceConfig, FacetConfig, KinematicLoadConfig, KinematicDeviations
)
from artist.util import config_dictionary

from artist.raytracing.heliostat_tracing import HeliostatRayTracer

import matplotlib.pyplot as plt
import torch
from matplotlib.pyplot import tight_layout

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Include the receiver configuration.
receiver1 = Receiver(
    receiver_type=config_dictionary.receiver_type_planar,
    position_center=torch.tensor([0.0, -50.0, 0.0, 1.0], device=device),
    normal_vector=torch.tensor([0.0, 1.0, 0.0, 0.0], device=device),
    plane_e=8.629666667,
    plane_u=7.0,
    resolution_e=256,
    resolution_u=256,
)

# Create list of receiver configs - in this case only one.
receiver_list = [receiver1]



# Include the light source configuration.
light_source1 = LightSource(
    number_of_rays=200
)

# Create a list of light source configs - in this case only one.
light_source_list = [light_source1]

# Define the incident ray direction for when the sun is in the south.
sun_position = torch.tensor([0.0, -1.0, 0.0, 0.0], device=device)

control_points = torch.zeros((1,4,8,8))
degree_e = 3
degree_n = 3
number_eval_points_e = 100
number_eval_points_n = 100
translation_vector = torch.tensor([0.0, 0.0, 0.0, 0.0])
canting_e = torch.tensor([0.0, 0.0, 0.0, 0.0])
canting_n = torch.tensor([0.0, 0.0, 0.0, 0.0])


facets_list = [FacetConfig(
    facet_key = "1",
    control_points = control_points,
    degree_e = degree_e,
    degree_n = degree_n,
    number_eval_points_e = number_eval_points_e,
    number_eval_points_n = number_eval_points_n,
    translation_vector = translation_vector,
    canting_e = canting_e,
    canting_n = canting_n
),
    FacetConfig(
        facet_key="2",
        control_points=control_points,
        degree_e=degree_e,
        degree_n=degree_n,
        number_eval_points_e=number_eval_points_e,
        number_eval_points_n=number_eval_points_n,
        translation_vector=translation_vector,
        canting_e=canting_e,
        canting_n=canting_n
    ),

    FacetConfig(
        facet_key="3",
        control_points=control_points,
        degree_e=degree_e,
        degree_n=degree_n,
        number_eval_points_e=number_eval_points_e,
        number_eval_points_n=number_eval_points_n,
        translation_vector=translation_vector,
        canting_e=canting_e,
        canting_n=canting_n
    ),

    FacetConfig(
        facet_key="4",
        control_points=control_points,
        degree_e=degree_e,
        degree_n=degree_n,
        number_eval_points_e=number_eval_points_e,
        number_eval_points_n=number_eval_points_n,
        translation_vector=translation_vector,
        canting_e=canting_e,
        canting_n=canting_n
    )
]

print(facets_list)
surface_config = SurfaceConfig(facets_list=facets_list)

# Generate the surface prototype configuration.
surface_prototype_config = SurfacePrototypeConfig(facets_list=facets_list)

# Note that we do not include kinematic deviations in this scenario!
# Include the kinematic prototype configuration.
kinematic_prototype_config = KinematicPrototypeConfig(
    type=config_dictionary.rigid_body_key,
    initial_orientation=torch.tensor([0.0, 0.0, 1.0, 0.0], device=device),
)

# Include an ideal actuator.
actuator1_prototype = ActuatorConfig(
    key="actuator1",
    type=config_dictionary.ideal_actuator_key,
    clockwise_axis_movement=False,
)

# Include a second ideal actuator.
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
    actuator_prototype=actuator_prototype_config,
)

kinematic_deviations = KinematicDeviations()

# Was soll hier eingegeben werden? Aktuell geraten...
kinematic_load_config = KinematicLoadConfig(
    type= "rigid_body",
    initial_orientation= torch.tensor([0.0, 0.0, 1.0, 0.0], device=device),
    deviations=kinematic_deviations
)

# Include the configuration for a heliostat.
heliostat1 = Heliostat(
    heliostat_id = 1,
    position=torch.tensor([0.0, 5.0, 0.0, 1.0], device=device),
    aim_point=torch.tensor([0.0, -50.0, 0.0, 1.0], device=device),
    surface_config=surface_config,
    kinematic_config=kinematic_load_config,
    actuator_config=actuator_prototype_config,
    control_points_available=True,
    device = device
)



# Create a list of all the heliostats - in this case, only one.
heliostat_list = [heliostat1]


power_plant_position=torch.tensor([0.0, 0.0, 0.0], device=device)
receivers = ReceiverField(receiver_list=receiver_list)
print(receivers)
light_sources = LightSourceArray(light_source_list=light_source_list)
print(light_sources)
heliostat_field = HeliostatField(heliostat_list=heliostat_list)
print(heliostat_field)

scenario_test = Scenario(power_plant_position=power_plant_position,
                         receivers=receivers,
                         light_sources=light_sources,
                         heliostat_field=heliostat_field
                         )

# necessity for condition
# heliostat1.set_aligned_surface_with_incident_ray_direction(incident_ray_direction=sun_position)


# Define the raytracer.
raytracer = HeliostatRayTracer(scenario=scenario_test, batch_size=100, control_points_available=True)


# Perform heliostat-based raytracing.

image = raytracer.trace_rays(
    incident_ray_direction=sun_position, device=device
)
image = raytracer.normalize_bitmap(image)

# Plot the result.
fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(image.T.cpu().detach().numpy(), cmap="inferno")
tight_layout()
plt.show()





