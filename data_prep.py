from Unsupervised_learning.sun_positions import random_sun_positions
from Unsupervised_learning.heliostat_positions import give_defl_list
import random
import torch
import pathlib
from cfg import _C


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Prepare data
#Heliostat Position (sind schon ENU)
helios_with_defl_dict= give_defl_list()
print("helios_with_defl_dict")
print(helios_with_defl_dict)
print(len(helios_with_defl_dict))


# Sun - get 8 random positions for each heliostat position above 30 degrees
# Sind Einheitsvektoren, deswegen ENU passt
num_positions = 8
sun_vecs_list, extras_list = random_sun_positions(num_positions, device)
print("sun_vecs_list")
print(sun_vecs_list)
print("extras_list")
print(extras_list)
