import pathlib
import json
import torch


from artist.util import config_dictionary
from artist.util.configuration_classes import (
    ActuatorConfig,
    ActuatorPrototypeConfig,
    HeliostatConfig,
    HeliostatListConfig,
    # KinematicOffsets,
    KinematicPrototypeConfig,
    LightSourceConfig,
    LightSourceListConfig,
    PowerPlantConfig,
    PrototypeConfig,
    #ReceiverConfig,
    #ReceiverListConfig,
    SurfacePrototypeConfig,
    FacetConfig, KinematicDeviations
)
from artist.util.scenario_generator import ScenarioGenerator


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def generate_scenario(file_path_scenario, Heliostat_path, heliostat_position, heliostat_aim_point):



    # This checks to make sure the path you defined is valid and a scenario HDF5 can be saved there.
    if not pathlib.Path(file_path_scenario).parent.is_dir():
        raise FileNotFoundError(
            f"The folder ``{pathlib.Path(file_path_scenario).parent}`` selected to save the scenario does not exist. "
            "Please create the folder or adjust the file path before running again!"
        )

    # Include the power plant configuration.
    power_plant_config = PowerPlantConfig(
        power_plant_position=torch.tensor([0.0, 0.0, 0.0], device=device)
    )

    # Include the receiver configuration.
    receiver1_config = ReceiverConfig(
        receiver_key="receiver1",
        receiver_type=config_dictionary.receiver_type_planar,
        position_center=torch.tensor([0.0, -50.0, 0.0, 1.0], device=device),
        normal_vector=torch.tensor([0.0, 1.0, 0.0, 0.0], device=device),
        plane_e=8.629666667,
        plane_u=7.0,
        resolution_e=256,
        resolution_u=256,
    )

    # Create list of receiver configs - in this case only one.
    receiver_list = [receiver1_config]

    # Include the configuration for the list of receivers.
    receiver_list_config = ReceiverListConfig(receiver_list=receiver_list)

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

    # Load the JSON file
    json_file_path = Heliostat_path
    with open(json_file_path, "r") as file:
        facets_data = json.load(file)

    # Create the facet_prototype_list
    facet_prototype_list = []

    for facet_key, facet in facets_data.items():
        facet_config = FacetConfig(
            facet_key=facet_key,  # Use the key directly
            control_points=torch.tensor(facet["control_points"], dtype=torch.float32),
            degree_e=facet["degree_e"],
            degree_n=facet["degree_n"],
            number_eval_points_e=facet["number_eval_points_e"],
            number_eval_points_n=facet["number_eval_points_n"],
            #width=facet["width"],
            #height=facet["height"],
            translation_vector=torch.tensor(facet["translation_vector"], dtype=torch.float32),
            canting_e=torch.tensor(facet["canting_e"], dtype=torch.float32),
            canting_n=torch.tensor(facet["canting_n"], dtype=torch.float32),
        )
        facet_prototype_list.append(facet_config)

    # Generate the surface prototype configuration.
    surface_prototype_config = SurfacePrototypeConfig(facets_list=facet_prototype_list)

    # Note that we do not include kinematic deviations in this scenario!

    # Include the initial orientation offsets for the kinematic.
    kinematic_prototype_offsets = KinematicDeviations() # war vorher doppelter tensor, why??

     #Include the kinematic prototype configuration.
    kinematic_prototype_config = KinematicPrototypeConfig(
        type=config_dictionary.rigid_body_key,
        initial_orientation=torch.tensor([0.0, 0.0, 1.0, 0.0], device = device),
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

    # Note, we do not include individual heliostat parameters in this scenario.

    # Include the configuration for a heliostat.
    heliostat1 = HeliostatConfig(
        heliostat_key="heliostat1",
        heliostat_id=1,
        heliostat_position=heliostat_position,
        heliostat_aim_point=heliostat_aim_point,
    )

    # Create a list of all the heliostats - in this case, only one.
    heliostat_list = [heliostat1]

    # Create the configuration for all heliostats.
    heliostats_list_config = HeliostatListConfig(heliostat_list=heliostat_list)

    # Create a scenario object.
    scenario_object = ScenarioGenerator(
        file_path=file_path_scenario,
        power_plant_config=power_plant_config,
        receiver_list_config=receiver_list_config,
        light_source_list_config=light_source_list_config,
        prototype_config=prototype_config,
        heliostat_list_config=heliostats_list_config,
    )

    # Generate the scenario.
    scenario_object.generate_scenario()

    return