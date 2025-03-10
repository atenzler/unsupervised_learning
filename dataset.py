import torch
from torch.utils.data import Dataset

class HeliostatDataset(Dataset):
    def __init__(self, sun_positions, flux_images, heliostat_position, z_control_points):
        self.sun_positions = sun_positions
        self.flux_images = flux_images
        self.heliostat_position = heliostat_position
        self.z_control_points = z_control_points

    def __len__(self):
        return len(self.sun_positions)  # The number of samples, which is 8 in this case

    def __getitem__(self, idx):
        # Get the sun positions (8, 3) for the current batch
        sun_pos = self.sun_positions

        # Get the flux images (8, C, H, W) for the current batch
        flux_img = self.flux_images

        # Expand the heliostat position to match the number of sun positions
        heliostat_pos = self.heliostat_position      #.unsqueeze(0).expand(sun_pos.shape[0], -1)  # (8, 4)

        # Get the corresponding z control points (8, 8) for the current batch
        z_points = self.z_control_points

        return (sun_pos, flux_img, heliostat_pos), z_points
