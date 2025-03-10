import numpy as np
import matplotlib.pyplot as plt
import torch as th
import os
from test1 import list_folders_in_directory

def give_helPos_on_field_list(cfg, cluster, real=True, nhelpos=6):
    helPos_list = []

    if cluster:
        posdir = cfg.DIRECTORIES.JUWELS.POSDIR
    else:
        posdir = r'C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Heliostat_Positions\heliostat_position_dictionary.npy'

    helPos_dic = np.load(posdir, allow_pickle=True).item()
    validlist = cfg.DEEPLARTS.VALID.TESTSET

    if not cluster: helPos_list = give_defl_list()


    #validpos = []
    #deflpos = []
    #for key in helPos_dic:
    #    if key in validlist:
    #        validpos.append(helPos_dic[key])

    #    if not cluster:
    #        if key in defllist and not key in validlist:
    #            deflpos.append(helPos_dic[key])



    helpos_art = give_helPos_larger_grid(nhelpos, device='cpu')

    plotting = True
    if plotting and not cluster:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))

        ax.scatter(
            helpos_art[:, 0],
            helpos_art[:, 1],
            c='black',  # Marker color
            s=15,  # Marker size
            alpha=0.7,  # Transparency for better clarity with overlapping points
            edgecolors='k',
            label="train"  # Black edge around markers for better contrast
        )


        # ax.scatter(np.array(helPos_list)[:,0], np.array(helPos_list)[:,1], alpha=0.5, label='field')
        # ax.scatter(np.array(deflpos)[:,0], np.array(deflpos)[:,1], color='red', marker='x', label='defl')
        # ax.scatter(np.array(validpos)[:,0], np.array(validpos)[:,1], color='black', marker='x', label='simreal')
        ax.legend(loc="best")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_title("Position of Train and Test Heliostats", fontsize=16, fontweight='bold')
        ax.set_xlabel("Position East / m", fontsize=14)
        ax.set_ylabel("Position North / m", fontsize=14)
        ax.set_aspect('equal')
        ax.tick_params(axis='both', which='major', labelsize=12)
        fig.tight_layout()

    #    fig, ax = plt.subplots(1, 1)
    #ax.scatter((helpos_art)[:, 1], (helpos_art)[:, 2])
    #ax.scatter(np.array(helPos_list)[:, 1], np.array(helPos_list)[:, 2])
    #ax.scatter(np.array(deflpos)[:, 1], np.array(deflpos)[:, 2], color='red', marker='x')
    #ax.scatter(np.array(validpos)[:, 1], np.array(validpos)[:, 2], color='black', marker='x')

    #ax.grid()

    #fig, ax = plt.subplots(1, 1)
    #ax.hist(np.array(helPos_list)[:, 2])
    plt.show()


    if real == False:
        helPos_list = helpos_art.tolist()


    return helPos_list



def give_helPos_larger_grid(nhels, device):
    helpos = []
    # min_distance = 10

    # halbkreis vom Turm weg
    for distance in range(5, 400, 5):
        zs = (th.rand(nhels, device=device) / 1.8 + 1.5).unsqueeze(0)

        phi_max = th.pi / 6
        phis = th.linspace(-phi_max, phi_max, nhels, device=device)
        rs = distance
        xs = rs * th.cos(phis).unsqueeze(0)
        ys = rs * th.sin(phis).unsqueeze(0)

        helPositions = th.cat((ys, xs - 100, zs), dim=0)
        helpos.append(helPositions)

    # zusätzliche weit vorne, da schwierigere Muster
    # for distance in range(min_distance-2, 75, 1):
    #     y = th.linspace(-50, 50, nhels, device=device).unsqueeze(0)
    #     x = th.ones_like(y)*distance
    #     zs = (th.rand(nhels, device=device)/1.8+1.5).unsqueeze(0)

    #     helPositions = th.cat((y, x, zs), dim=0)

    #     helpos.append(helPositions)

    helpos = th.cat(helpos, dim=1)
    print(f"Your helPos dataset has {helpos.size()} entries")

    mask = (helpos[1, :] > 10)
    helpos = helpos[:, mask]

    mask = (helpos[0, :] > -150)
    helpos = helpos[:, mask]

    mask = (helpos[0, :] < 150)
    helpos = helpos[:, mask]

    return helpos.swapaxes(0, 1)

"""# die valid Heliostatpositionen
    nhels_valid = 10
    helPos_valid = []
    for distance in range(5, 375, 20):
        zs = (th.rand(nhels_valid, device=device) / 1.8 + 1.5).unsqueeze(0)

        phi_max = th.pi / 6
        phis = th.linspace(-phi_max, phi_max, nhels_valid, device=device)
        rs = distance
        xs = rs * th.cos(phis).unsqueeze(0)
        ys = rs * th.sin(phis).unsqueeze(0)

        helPositions = th.cat((ys, xs - 75, zs), dim=0)
        helPos_valid.append(helPositions)

    helPos_valid = th.cat(helPos_valid, dim=1)

    mask = (helPos_valid[1, :] > 10)
    helPos_valid = helPos_valid[:, mask]

    mask = (helPos_valid[0, :] > -150)
    helPos_valid = helPos_valid[:, mask]

    mask = (helPos_valid[0, :] < 150)
    helPos_valid = helPos_valid[:, mask]
    
    return helPos_valid.swapaxes(0, 1)
    
    ax.scatter(
            np.array(helPos_valid)[:, 0],
            np.array(helPos_valid)[:, 1],
            c='red',  # Marker color
            s=30,  # Marker size
            alpha=0.7,  # Transparency for better clarity with overlapping points
            edgecolors='k',
            label="valid/test"  # Black edge around markers for better contrast
        )
        
        Ursprünglichen Code am besten nochmal aus mail holen wenn nötig"""




def give_defl_list():

    hellist = list_folders_in_directory(r"C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Deflectometry_Daten")
    hellist = hellist[:-1]
    #print("hellist")
    #print(hellist)
    #print(len(hellist))

    posdir = r'C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\Heliostat_Positions\heliostat_position_dictionary.npy'

    helPos_dic = np.load(posdir, allow_pickle=True).item()

    helios_with_defl_dict = {}

    for hel_name in hellist:
        if hel_name in helPos_dic:
            # Assign the position from helPos_dic to the corresponding heliostat in the dictionary
            helios_with_defl_dict[hel_name] = helPos_dic[hel_name]

    # Extract East (x) and North (y) coordinates
    east_coords = []
    north_coords = []

    # Loop through the dictionary and extract the first two dimensions (East and North)
    for hel_name, position in helios_with_defl_dict.items():
        east_coords.append(position[0])  # Assuming East is the first element in the position
        north_coords.append(position[1])  # Assuming North is the second element in the position

    # Create the scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter(east_coords, north_coords, c='blue', edgecolors='black', alpha=0.7, label="Heliostats")

    # Label the axes and add a title
    plt.xlabel("East / m", fontsize=14)
    plt.ylabel("North / m", fontsize=14)
    plt.title("Heliostat Positions (East vs North)", fontsize=16, fontweight='bold')

    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc="best")

    # Display the plot
    plt.show()

    return helios_with_defl_dict

#Was content of give_defl_list
"""    if cluster:

        defldir = cfg.DIRECTORIES.JUWELS.DEFLFILLED

    else:

        defldir = cfg.DIRECTORIES.LOCAL.DEFLFILLED

    defllist = os.listdir(defldir)

    skiplist = cfg.DEEPLARTS.TRAIN.SKIPLIST

    bad_defl_list = cfg.DEEPLARTS.TRAIN.PICEOFFACETMISSINGLIST

    hellist = []

    for defl in defllist:

        tags = defl.split("_")

        sessionstring = tags[1] + "_" + tags[-1].split(".")[0]

        if sessionstring in skiplist:
            continue

        if sessionstring in bad_defl_list:
            continue

        helname = tags[1]

        hellist.append(helname)"""




