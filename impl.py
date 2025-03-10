"""
Created on Wed Jan 10 09:00:32 2024

@author: Jing Sun & Lu Li & Tiexing Wang & Liang Zhang

"""
import h5py
import numpy as np
import json
import os
import re
# import rioxarray as rxr
import math
import torch
import torch.nn as nn
import logging
import torch.optim.lr_scheduler as lr_scheduler
import torchvision.transforms as transforms
from torch.utils.data import TensorDataset, DataLoader

from pathlib import Path
from Unsupervised_learning.generate_scenario import generate_scenario
from Unsupervised_learning.generate_graph import generate_graph
from Unsupervised_learning.integrate_raytracer_test import get_position_and_canting, overwrite_scenario, \
    raytracing_from_nn
from artist.util.configuration_classes import SurfaceConfig
from artist.util.utils import convert_wgs84_coordinates_to_local_enu, convert_3d_point_to_4d_format
from artist.scenario import Scenario


# A simple early stopping function, you may want to change it.
def early_stopping(valid_losses, patience_epochs, patience_loss):
    if len(valid_losses) < patience_epochs:
        return False
    recent_losses = valid_losses[-patience_epochs:]

    if all(x >= recent_losses[0] for x in recent_losses):
        return True

    if max(recent_losses) - min(recent_losses) < patience_loss:
        return True
    return False

def manage_saved_models(directory):
    pattern = re.compile(r'epoch_(\d+)\.pth')
    epoch_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            match = pattern.match(file)
            if match:
                epoch_num = int(match.group(1))
                file_path = os.path.join(root, file)
                epoch_files.append((file_path, epoch_num))

    # Check if there are more than 5 files
    if len(epoch_files) > 5:
        epoch_files.sort(key=lambda x: x[1])
        files_to_delete = len(epoch_files) - 5

        for i in range(files_to_delete):
            os.remove(epoch_files[i][0])
            print(f"Deleted: {epoch_files[i][0]}")

def clear_logging_handlers():
    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

def create_loss(criterion_type):
    if criterion_type == 'MAE':
        return nn.L1Loss()
    elif criterion_type == 'MSE':
        return nn.MSELoss()
    else:
        raise ValueError("Undefined criterion type. Update your code.")

def train_dnn(train_set, #valid_set,
                device, model, criterion, batch_size,
                optimizer_type, learning_rate, weight_decay, dirs,
                max_epochs, patience_epochs, patience_loss,
                heliostat_aim_point, aim_point_area, new_scenario, power_plant_position, ideal_grid):

    # Create logger object
    logging.basicConfig(level=logging.INFO, filename=dirs + '/loss_record.log', filemode='a',
                        format='%(asctime)s   %(levelname)s   %(message)s')

    model.to(device)

    #train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=True)
    #valid_loader = DataLoader(valid_set, batch_size=batch_size, shuffle=False, num_workers=0, drop_last=True)

    criterion = create_loss(criterion)

    if optimizer_type == 'Adam':
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    elif optimizer_type == 'SGD':
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=weight_decay)
    else:
        raise ValueError("Undefined optimizer type. Update your code.")

    scheduler = lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.8)

    logging.info('Training starts!')

    train_losses = []
    valid_losses = []
    best_valid_loss = np.inf
    best_model_state = None

    print("start loader")

    train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=0)

    torch.autograd.set_detect_anomaly(True)

    # Check a batch
    for batch in train_loader:
        (sun_pos, flux_img, heliostat_pos), z_points = batch
        print(f"Sun Positions Shape: {sun_pos.shape}")  # (batch_size, 8, 4)
        print(f"Flux Images Shape: {flux_img.shape}")  # (batch_size, 8, C, H, W)
        print(f"Heliostat Positions Shape: {heliostat_pos.shape}")  # (batch_size, 4)
        print(f"Z Control Points Shape: {z_points.shape}")  # (batch_size, 8, 8)
        break

    print("start epochs")
    for epoch in range(max_epochs):
        # Train the model
        model.train()
        running_train_loss = 0.0
        for i, ((sun_pos, flux_img, heliostat_pos), z_points) in enumerate(train_loader, 0):
            model.zero_grad()
            optimizer.zero_grad()
            print(flux_img)
            print(flux_img.shape)
            print(sun_pos)
            print(heliostat_pos)
            print("test")

            targetID = None

            sun_pos, flux_img, heliostat_pos, z_points = sun_pos.to(device), flux_img.to(device), heliostat_pos.to(device), z_points.to(device)
            z_cntrl_points = model(flux_img, sun_pos, heliostat_pos, targetID)
            print(z_cntrl_points)
            print("z_cntrl_points:", type(z_cntrl_points))  # Check if it's a tuple
            print("Number of elements in z_cntrl_points:", len(z_cntrl_points))  # See how many elements are inside

            for i, out in enumerate(z_cntrl_points):
                if isinstance(out, torch.Tensor):  # Only print shape for tensors
                    print(f"Shape of z_cntrl_points[{i}]:", out.shape)
                else:
                    print(f"z_cntrl_points[{i}] is of type {type(out)}")

            for i in range(sun_pos.shape[0]):  # Iterate over each sample in the batch

                heliostat_position = heliostat_pos[0]
                print("heliostat position")
                print(heliostat_position)
                heliostat_position_enu = convert_wgs84_coordinates_to_local_enu(heliostat_position, power_plant_position, device)
                heliostat_position_enu = convert_3d_point_to_4d_format(heliostat_position_enu, device=device)


                z_cntrl_points_batch = z_cntrl_points[0][i]
                print("z_cntrl_points_batch")
                print(z_cntrl_points_batch.shape)

                ideal_grid[:, :, :, 2] = z_cntrl_points_batch
                control_points = ideal_grid
                print("control_points")
                print(control_points)
                print(control_points.shape)

                scenario = overwrite_scenario(heliostat_aim_point, heliostat_position_enu, control_points, new_scenario)
                old_heliostat = scenario.heliostats.heliostat_list[0]
                print("check1")
                old_heliostat.surface_points, old_heliostat.surface_normals = (old_heliostat.surface.get_surface_points_and_normals(device=device))
                print("check2")

                total_loss = torch.zeros(1, device=device, requires_grad=True)

                for j in range(sun_pos.shape[1]):  # Iterate over the 8 sun positions
                    sunPos_LD = sun_pos[i, j] / torch.linalg.norm(sun_pos[i, j])  # Normalize sun position for the j-th sun position
                    sun_position_4d = convert_3d_point_to_4d_format(sunPos_LD, device=device)
                    print("sun_position_4d")
                    print(sun_position_4d)

                    image = raytracing_from_nn(scenario, sun_position_4d, aim_point_area, show_image=False, device=device)
                    # Add a channel dimension (assuming it's grayscale, so 1 channel)
                    image = image.unsqueeze(0).unsqueeze(0)  # Shape: [1, 1, 256, 256]
                    resize = transforms.Resize((64, 64))
                    image_resized = resize(image.clone())
                    print("shapes")
                    print(image.shape)
                    print(flux_img.shape)
                    # Compute the loss for the current sun position
                    loss = criterion(image_resized, flux_img[i, j])  # Use flux image for the j-th sun position
                    print("loss")
                    print(loss)

                    # Accumulate the loss for this data point
                    total_loss = total_loss + loss
                    logging.info(f"Epoch {epoch + 1}, Batch {i + 1}, Sample {j + 1}: Loss = {loss.item():.6f}")

            total_loss.backward(retain_graph=True)
            running_train_loss += total_loss
            optimizer.step()

        epoch_train_loss = running_train_loss/len(train_loader)
        train_losses.append(epoch_train_loss)

        logging.info(f"Epoch {epoch + 1} completed. Average Training Loss: {epoch_train_loss:.6f}")

        # Evaluate the model on validation data
        model.eval()
        running_valid_loss = 0.0
        with (torch.no_grad()):
            for i, (magins, kernels) in enumerate(valid_loader,0):
                magins, kernels = magins.to(device), kernels.to(device)
                outputs  = model(magins)
                img_size = outputs.shape[-1]
                upwarded_outputs = torch.zeros_like(outputs)
                for n in range(outputs.size(0)):
                    kernel = kernels[n].view(img_size * img_size, img_size * img_size)
                    output = outputs[n].view(img_size, img_size)
                    upwarded_output = upward_continuation(output, kernel, device)
                    upwarded_output = upwarded_output.view(-1, 1, img_size, img_size)
                    upwarded_outputs[n] = upwarded_output

                btch_valid_loss = criterion(upwarded_outputs, magins)
                running_valid_loss += btch_valid_loss.item()

            epoch_valid_loss = running_valid_loss/len(valid_loader)
            valid_losses.append(epoch_valid_loss)

        if epoch_valid_loss < best_valid_loss:
            best_valid_loss = epoch_valid_loss
            best_model_state = model.state_dict()
            torch.save(best_model_state, f'{dirs}/epoch_{epoch + 1}.pth')
        manage_saved_models(dirs)

        logging.info(
            f"\n"
            f"Epoch:[{epoch+1}]\t Train loss={epoch_train_loss:.12f}.\n"
            f"Epoch:[{epoch+1}]\t Valid loss={epoch_valid_loss:.12f}.\n"
        )

        if early_stopping(valid_losses, patience_epochs, patience_loss):
            logging.info(f"Early stopping at epoch {epoch+1}")
            break

        scheduler.step()

    logging.info("Training is done!")
    # Clear logging handlers to close the log file properly
    clear_logging_handlers()

    # Restore the best model state
    if best_model_state:
        model.load_state_dict(best_model_state)

    return train_losses, valid_losses, model

def predict_dnn(test_input, device, model, batch_size):
    reshaped_test_input = test_input.reshape(test_input.shape[0], 1, *test_input.shape[1:])

    num_samples = reshaped_test_input.shape[0]
    num_batches = (num_samples + batch_size - 1) // batch_size

    test_in = torch.from_numpy(reshaped_test_input).float()
    test_in = test_in.to(device)

    model = model.to(device)
    model.eval();
    
    output_signal = []
    with torch.no_grad():
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, num_samples)
            batch_in = test_in[start_idx:end_idx]
            batch_out = model(batch_in)
            output_signal.append(batch_out[:, 0, :, :])
    output_signal = torch.cat(output_signal, dim=0)

    return output_signal

def save_model(model, dirs):
    torch.save({
                'model_state_dict': model.state_dict(),
                }, dirs + "/model.pt")
    print('Model saved!')
    return

def load_model(model, dirs):
    checkpoint = torch.load(dirs + '/model.pt')
    model.load_state_dict(checkpoint['model_state_dict'])
    print('Model loaded!')
    return model



