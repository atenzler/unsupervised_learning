from typing import Any

import yacs
from yacs.config import CfgNode as CN
import os

_C = CN()
# UNIQUE EXPERIMENT IDENTIFIER
_C.DIRECTORIES = CN()
_C.DIRECTORIES.LOCAL = CN()
_C.DIRECTORIES.LOCAL.HOMEDIR = r'C:\Users\anton\Desktop\Masterarbeit\Masterthesis\Unsupervised_learning'
_C.DIRECTORIES.LOCAL.MODELDIR = r'C:\Users\anton\Old_Desktop\Masterthesis\Unsupervised_learning\Data\model'


_C.DEEPLARTS = CN()
_C.DEEPLARTS.TRAIN = CN()
_C.DEEPLARTS.TRAIN.TARGET_IMAGE_SIZE = 64
_C.DEEPLARTS.TRAIN.SURFACE_MIN = -0.004
_C.DEEPLARTS.TRAIN.SURFACE_MAX = 0.004
_C.DEEPLARTS.TRAIN.NSUNPOS = 8