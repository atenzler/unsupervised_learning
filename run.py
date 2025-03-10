"""
Created on Wed Jan 10 09:03:42 2024

@author: Jing Sun & Tiexing Wang

"""
from unet import *
from ResNet import *
from func import *
from impl import *
import numpy as np
import os
import torch
from PIL import Image
from artist.util.utils import convert_3d_point_to_4d_format, convert_3d_direction_to_4d_format, convert_wgs84_coordinates_to_local_enu
from dataset import HeliostatDataset
from PhysConUL_DownCont.updated_code import my_deepLarts
from PhysConUL_DownCont.updated_code import my_cfg
from my_cfg import _C
from PhysConUL_DownCont.Jan_NN_model.Parameter_Netzwerk import architecture_args, convolution_encoder_args, transformer_fusion_encoder_args, transformer_flux_encoder_args, styleGAN_args, training_args, test_args, data_args

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device == 'cuda':
    torch.backends.cuda.max_split_size = 1024
print(device)

# Scenario nur einmal einlesen
scenario_name = r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Scenarios\AA39\Scenario_upper_centre_1_cov.h5"

# JSON file with constant xy grid
with open(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Surfaces\all_heliostat_surfaces.json", "r") as f:
    data = json.load(f)

ideal_grid = torch.tensor(data["AA23"]["facet_1"]["control_points"], device = device)
print(ideal_grid)
print(ideal_grid.shape)
ideal_grid[:, :, 2] = 0
print(ideal_grid)
print(ideal_grid.shape)
ideal_grid_4f = ideal_grid.unsqueeze(0).repeat(4, 1, 1, 1)
print(ideal_grid_4f)
print(ideal_grid_4f.shape)


# Load a scenario.
with h5py.File(scenario_name, "r") as f:
    new_scenario = Scenario.load_scenario_from_hdf5(scenario_file=f, control_points_available=True, device=device)

print("loading from scenario done")
print(new_scenario.heliostats.heliostat_list[0].surface.facets[0].control_points)


# Create a folder
dirs = create_folder_struct()
my_cfg = _C.clone()

""" dnn settings """
# NOTE: I didn't properly tune the hyperparameters.
# The values were set based on experience for quickly getting some early stage results.
# You should do a proper hyperparameter optimization.
criterion       = 'MAE'
optimizer       = 'Adam'
learning_rate   = 0.0005 #lr_scheduler.StepLR employed
weight_decay    = 0
batch_size      = 8
max_epochs      = 500
patience_epochs = 30
patience_loss   = 0.001
in_channels     = 1
out_channels    = 1
kernel_size     = 3 #the convolution kernel
which_net       = 'DeepLarts'

#heliostat_list = ["AA23"]
# Define the incident ray direction for when the sun is in the south.
sun_positions = [
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
    torch.tensor([0.0, 0.46, 0.89], device=device),
                ]
sun_positions = torch.stack(sun_positions, dim=0)
print("posi")
print(sun_positions)

power_plant_position=torch.tensor([50.91342112259258, 6.387824755874856, 87.0], device=device)

heliostat_position = torch.tensor([50.913644729255935, 6.387991189938079, 88.795], device = device)
heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device = device)

aim_point_upper_target = [50.91339203684, 6.38782456351324, 130.097666666667]
aim_point_lower_target = [50.91339203684, 6.38782456351324, 122.8815]
aim_point_multifocus = [50.913396450887, 6.38757443672805, 138.97975]

aim_point_area = "solar_tower_juelich_upper"

heliostat_aim_point = torch.tensor(aim_point_upper_target, device=device)
heliostat_aim_point_enu = convert_wgs84_coordinates_to_local_enu(heliostat_aim_point, power_plant_position, device)
heliostat_aim_point_enu = convert_3d_point_to_4d_format(heliostat_aim_point_enu, device = device)


if which_net == 'UNet':
    features = [64, 128, 256, 512]
    nbr   = len(features)
    model = UNET(in_channels=in_channels, out_channels=out_channels, filter_size=kernel_size, features=features)
elif which_net == 'ResNet':
    features = 64
    nbr   = 30
    model = ResNetLayer(in_channels, features, features, out_channels, conv=conv3x3, block=ResNetBasicBlock, n=nbr)
elif which_net == 'DeepLarts':
    model = my_deepLarts.init_deepLarts(my_cfg,
                                       new_deepLarts=True,
                                       name_deepLarts="test",
                                       load_from_deepLarts=None,
                                       architecture_args=architecture_args,
                                       convolution_encoder_args=convolution_encoder_args,
                                       transformer_fusion_encoder_args=transformer_fusion_encoder_args,
                                       transformer_flux_encoder_args=transformer_flux_encoder_args,
                                       styleGAN_args=styleGAN_args,
                                       data_args=data_args,
                                       training_args=training_args,
                                       device="cpu",
                                       timestamp="2025_02_20",
                                       cluster=False,
                                       rank=-0)
    features= "not applicable"
    nbr="not applicable"


"""  Training (and validation)  """
pre_dirs = 'None'

# Load PNG image
flux_density_input = Image.open(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Raytracer_results\example_image.png").convert("L")

# Resize to 64x64
flux_density_input = flux_density_input.resize((64, 64), Image.LANCZOS)

# Convert to NumPy array (raw bitmap)
bitmap_input_array = np.array(flux_density_input)
#normalize
bitmap_input_array = torch.tensor(bitmap_input_array, dtype=torch.float32, device="cuda" if torch.cuda.is_available() else "cpu") / 255.0
bitmap_images_list = torch.stack([bitmap_input_array] * 8, dim=0)
print("check channel")
print(bitmap_images_list.shape)
print(bitmap_input_array.shape)  # (height, width) for grayscale, (height, width, 3) for RGB


# NOTE: I didn't do normalization of the data. It's also something you can explore.

# Dataloader and splitting (torch.utils.data.random_split -- you may want to change it!)
#bag = prepare_data(bitmap_images_list, sun_positions, heliostat_position_enu)
#train_set, valid_set = split_dataset(bag, train_percentage=0.80)
#print("trainset")
#print(train_set[0])
#print(train_set[1])
#print(train_set[2])

z_control_points = torch.zeros(4, 8, 8, 3)

dataset = HeliostatDataset(sun_positions, bitmap_images_list, heliostat_position, z_control_points)


# Make a log
self_logging(model, device, pre_dirs, dirs, which_net,
                        len(dataset), #len(valid_set),
                        in_channels, out_channels, kernel_size, features, nbr,
                        criterion, optimizer, learning_rate, weight_decay,
                        batch_size, max_epochs, patience_epochs, patience_loss,
                        sun_positions, heliostat_position_enu,
                        heliostat_aim_point_enu)

# Train the dnn
print("start training")
train_losses, valid_losses, model = train_dnn(dataset, #valid_set,
                                               device, model, criterion, batch_size,
                                               optimizer, learning_rate, weight_decay, dirs,
                                               max_epochs, patience_epochs, patience_loss,
                                               heliostat_aim_point_enu, aim_point_area, new_scenario, power_plant_position, ideal_grid_4f)

write_summary(model, dirs)
plot_loss(train_losses, valid_losses, dirs)

"""  Test  """
# Load data
#test_flux_density = np.load("../data/single/upwarded_mag_h0_rsp4.npy")[ :100, :, :].astype(np.float32)

# Execute
#test_output = predict_dnn(test_flux_density, device, model, batch_size)











