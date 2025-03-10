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
from artist.util.utils import convert_3d_point_to_4d_format

from artist.raytracing.heliostat_tracing import HeliostatRayTracer
from artist.scenario import Scenario
from artist.util.configuration_classes import HeliostatConfig
from artist.util.configuration_classes import ActuatorConfig, ActuatorPrototypeConfig

from pathlib import Path


from Unsupervised_learning.generate_scenario import generate_scenario
from Unsupervised_learning.generate_graph import generate_graph


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

power_plant_position=torch.tensor([50.91342112259258, 6.387824755874856, 87.0], device=device)

file_path_scenario = Path(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\Scenario_BE41")
Heliostat_path = Path(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\nurbs_files\share\PAINT\BE41\Deflectometry\BE41_nurbs.json")
heliostat_position = torch.tensor([50.915305447019854, 6.388130154616028, 88.77428], device = device)
heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device = device)

heliostat_aim_point = torch.tensor([50.91339203683997, 6.387824563513243, 130.09766666666667], device=device)
heliostat_aim_point_enu = convert_wgs84_coordinates_to_local_enu(heliostat_aim_point, power_plant_position, device)
heliostat_aim_point_enu = convert_3d_point_to_4d_format(heliostat_aim_point_enu, device = device)

save_path_scenario = Path(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\Scenario_BE41.h5")
save_image_path =  Path(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\test_images")

sunPos_LD = torch.tensor([0.0, 0.46, 0.89, 0], device=device)
norm = torch.linalg.norm(sunPos_LD)
sunPos_LD = sunPos_LD/norm #normalisierung egal, gleiches bild
sun_position = sunPos_LD


generate_scenario(file_path_scenario, Heliostat_path, heliostat_position_enu, heliostat_aim_point_enu)
generate_graph(save_path_scenario, save_image_path, sun_position)