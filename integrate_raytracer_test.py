import json
import torch
import h5py
import matplotlib.pyplot as plt
from matplotlib.pyplot import tight_layout
from sympy.polys.polyclasses import init_normal_ANP

from artist.raytracing.heliostat_tracing import HeliostatRayTracer
from artist.util.configuration_classes import SurfaceConfig, KinematicConfig, ActuatorConfig
from artist.util.utils import convert_wgs84_coordinates_to_local_enu, convert_3d_point_to_4d_format, \
    convert_3d_direction_to_4d_format
from artist.scenario import Scenario
from artist.field.heliostat import Heliostat

def get_position_and_canting(helio_list, power_plant_position, dic):
      # Dictionary to store all heliostat data
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    for helio_name in helio_list:
        file_path = (
            fr"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten\{helio_name}\Properties\{helio_name}-heliostat-properties.json")
        with open(file_path, "r") as file:
            data = json.load(file)

        # Extract data into variables
        heliostat_position = torch.tensor(data["heliostat_position"])
        heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device=device)
        heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device=device)

        print(data)

        # Define facet details
        facets = []
        for facet in data["facet_properties"]["facets"]:
            print(facet)
            translation_vector = facet["translation_vector"]
            canting_e = facet["canting_e"]
            canting_n = facet["canting_n"]
            facets.append({
                "translation_vector": translation_vector,
                "canting_e": canting_e,
                "canting_n": canting_n,
            })
        print(facets)

        dic[helio_name] = {
            "heliostat_position_enu": heliostat_position_enu,  # Convert tensor to list for easier handling
            "facets": facets
    }

    return dic


def overwrite_scenario(aim_point, heliostat_position, z_cntrl_points, new_scenario):

    single_heliostat = new_scenario.heliostats.heliostat_list[0]

    single_heliostat.position = heliostat_position
    single_heliostat.kinematic.position = heliostat_position
    single_heliostat.aim_point = aim_point
    single_heliostat.kinematic.aim_point = aim_point

    #light_source = new_scenario.light_sources.light_source_list[0]
    #light_source.number_of_rays = 200
    #new_scenario.light_sources.light_source_list[0] = light_source

    target_area = new_scenario.target_areas.target_area_list[0]
    target_area.position_center = aim_point
    new_scenario.target_areas.target_area_list[0] = target_area

    # Update control points and canting
    for i, facet in enumerate(single_heliostat.surface.facets):
    #    canting und translation vectors erstmal egal
    #    translation_vector = torch.tensor(dic[heliostat]["facets"][i]["translation_vector"], device=device)
    #    translation_vector_enu = convert_3d_direction_to_4d_format(translation_vector, device=device)
    #    single_heliostat.surface.facets[i].translation_vector = translation_vector_enu
    #    print("tvector")
    #    print(single_heliostat.surface.facets[i].translation_vector)

    #    canting_e = torch.tensor(dic[heliostat]["facets"][i]["canting_e"], device=device)
    #    single_heliostat.surface.facets[i].canting_e = canting_e
    #    canting_n = torch.tensor(dic[heliostat]["facets"][i]["canting_n"], device=device)
    #    single_heliostat.surface.facets[i].canting_n = canting_n



        control_points = z_cntrl_points[i]
        single_heliostat.surface.facets[i].control_points = control_points
        #print("check for 3d or 4d")
        #print(single_heliostat.surface.facets[i].control_points)

    new_scenario.heliostats.heliostat_list[0] = single_heliostat

    #print("test")
    #facet_num = [0, 1, 2, 3]
    #for i in facet_num:
        #print(single_heliostat.surface.facets[i].canting_e)
        #print(single_heliostat.surface.facets[i].canting_n)
        #print(single_heliostat.surface.facets[i].translation_vector)
        #print(single_heliostat.surface.facets[i].control_points)
        #print(single_heliostat.surface.facets[i].control_points.shape)

    return new_scenario


def raytracing_from_nn(scenario, sun_position, aim_point_area, show_image, device):
    # Align the heliostat.

    single_heliostat = scenario.heliostats.heliostat_list[0]
    print("testing")
    print(single_heliostat.surface.facets[0].control_points)

    single_heliostat.set_aligned_surface_with_incident_ray_direction(
        incident_ray_direction=sun_position, device=device
    )

    # Define the raytracer.
    raytracer = HeliostatRayTracer(
        scenario=scenario,
        batch_size=100,
        aim_point_area=aim_point_area
    )

    # Perform heliostat-based raytracing.
    image = raytracer.trace_rays(
        incident_ray_direction=sun_position, device=device
    )
    image = raytracer.normalize_bitmap(image)

    if show_image == True:
        # Plot the result.
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(image.T.cpu().detach().numpy(), cmap="inferno")
        tight_layout()
        plt.show()

    return image

if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    helio_list = ["AA39", "BA70"]  # needs to be iterated for
    power_plant_position = torch.tensor([50.91342112259258, 6.387824755874856, 87.0], device=device)

    # Define the incident ray direction
    sunPos_LD = torch.tensor([0.0, 0.46, 0.89, 0], device=device)  # muesste schon in enu sein
    norm = torch.linalg.norm(sunPos_LD)
    sunPos_LD = sunPos_LD / norm
    sun_position = sunPos_LD

    dic = {}
    position_dic = get_position_and_canting(helio_list, power_plant_position, dic)

    aim_point_upper_target = [50.91339203684, 6.38782456351324, 130.097666666667]
    aim_point_lower_target = [50.91339203684, 6.38782456351324, 122.8815]
    aim_point_multifocus = [50.913396450887, 6.38757443672805, 138.97975]

    aim_point_area = "solar_tower_juelich_upper"

    heliostat_aim_point = torch.tensor(aim_point_upper_target, device=device)
    heliostat_aim_point_enu = convert_wgs84_coordinates_to_local_enu(heliostat_aim_point, power_plant_position, device=device)
    heliostat_aim_point_enu = convert_3d_point_to_4d_format(heliostat_aim_point_enu, device=device)

    output_nn = [torch.zeros((8, 8, 3)), torch.zeros((8, 8, 3)), torch.zeros((8, 8, 3)), torch.zeros((8, 8, 3))] #per facet

    # Scenario nur einmal einlesen
    scenario_name = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\AA39\Scenario_upper_centre_1_cov.h5"

    # Load a scenario.
    with h5py.File(scenario_name, "r") as f:
        new_scenario = Scenario.load_scenario_from_hdf5(scenario_file=f, device=device)

    print("loading from scenario done")

    heliostat_position = torch.tensor([50.913644729255935, 6.387991189938079, 88.795], device=device)
    heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
    heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device=device)


    scenario = overwrite_scenario(heliostat_aim_point_enu, heliostat_position_enu, output_nn, new_scenario)
    old_heliostat = scenario.heliostats.heliostat_list[0]
    new_surface_config = SurfaceConfig(facet_list=old_heliostat.surface.facets)

    old_heliostat.surface_points, old_heliostat.surface_normals = (
        old_heliostat.surface.get_surface_points_and_normals(device=device))

    image = raytracing_from_nn(scenario, sun_position, aim_point_area, show_image=True, device=device)


