from typing import Any

import yacs
from yacs.config import CfgNode as CN
import os

_C = CN()
# UNIQUE EXPERIMENT IDENTIFIER

_C.ID = 'NotGiven'
_C.EXPERIMENT_NAME = "NotGiven"
_C.LOGDIR = 'Results'
_C.SEED = 42
_C.USE_FLOAT64 = True
_C.USE_GPU = True
_C.USE_CURL = False
_C.USE_NURBS = True
_C.SAVE_RESULTS = False
_C.CP_PATH = ""
# _C.CP_PATH                              = "C:\\Python\\DiffSTRAL\\diff-stral\\Results\\MoreNURBS\\LongRunMultiSun\\Logfiles\\MultiNURBSHeliostat.pt"
_C.LOAD_OPTIMIZER_STATE = False

# NURBS settings
_C.NURBS = CN()
# Whether to use the available width and height information to set up
# the NURBS surface.
# If setting this to `False`, be aware that the NURBS surface will
# always be evaluated at each surface position independently of the ray
# origins.
_C.NURBS.SET_UP_WITH_KNOWLEDGE = True
# Whether to initialize the control points according to known,
# ideal discretized values.
_C.NURBS.INITIALIZE_WITH_KNOWLEDGE = False
# Only relevant when `INITIALIZE_WITH_KNOWLEDGE`.
# Whether to only change z values in that initialization step.
_C.NURBS.INITIALIZE_Z_ONLY = True
_C.NURBS.FIX_SPLINE_CTRL_WEIGHTS = True
_C.NURBS.FIX_SPLINE_KNOTS = True
_C.NURBS.OPTIMIZE_Z_ONLY = True
_C.NURBS.RECALCULATE_EVAL_POINTS = False
_C.NURBS.SPLINE_DEGREE = 3

# For multi-NURBS heliostat
# Where to place the heliostat. If 'inherit', inherit the position from
# the loaded heliostat.
_C.NURBS.POSITION_ON_FIELD = 'inherit'  # in m
# Where to aim the heliostat. If `None`, automatically aim
# `cfg.AC.RECEIVER.CENTER`. If 'inherit', inherit the aim point from the
# loaded heliostat.
_C.NURBS.AIM_POINT = 'inherit'
# Rotational disturbance angles (x, y and z axes) in degrees. If
# 'inherit', inherit the disturbance angles from the loaded heliostat.
_C.NURBS.DISTURBANCE_ROT_ANGLES = 'inherit'
_C.NURBS.FACETS = CN()
_C.NURBS.FACETS.CANTING = CN()
# To disable canting, set this to 0. Then, the heliostat is left exactly
# as it was loaded in, be it pre-canted or not.
#
# When this is `None`, use the corresponding aim point as the focus
# point.
#
# In practice, only the distance of this point to the heliostat is
# relevant; therefore you may also give the distance of the focus point
# as a scalar instead of a 3-D point.
# In the same vein, you can set this to `float('inf')` to "de-cant" the
# heliostat so it's flat on z = 0.
#
# If 'inherit', use the focus point from the loaded heliostat.
#
# When the canting algorithm is 'active', any value other than 0 is
# ignored and treated as if it was `None`.
_C.NURBS.FACETS.CANTING.FOCUS_POINT = 0
# Canting algorithm can be 'standard', 'active', or 'first_sun'.
# - Standard canting calculates the canting rotation to the focus point
#   once at the beginning. The focus point is assumed to be right above
#   the heliostat center at the distance of the receiver.
# - In active canting, each facet is canted perfectly onto the receiver
#   center for each sun position. This means the focus point is always
#   treated as if it was `None`.
# - First sun specifies a mix of the two. The heliostat is canted
#   perfectly (i.e. actively) for the first sun position. This canting
#   only happens once at the start, not for each alignment.
#
# If 'inherit', use the canting algorithm from the loaded heliostat.
_C.NURBS.FACETS.CANTING.ALGORITHM = 'standard'

# NURBS progressive growing
_C.NURBS.GROWING = CN()
# 0 turns progressive growing off
_C.NURBS.GROWING.INTERVAL = 0
# 0 starts with minimum size
_C.NURBS.GROWING.START_ROWS = 0
_C.NURBS.GROWING.START_COLS = 0
# 0 grows a new index between all old ones
_C.NURBS.GROWING.STEP_SIZE_ROWS = 0
_C.NURBS.GROWING.STEP_SIZE_COLS = 0

# Width of the heliostat in meters. If 'inherit', use the width from the
# loaded heliostat.
_C.NURBS.WIDTH = 'inherit'  # in m
# Height of the heliostat in meters. If 'inherit', use the height from the
# loaded heliostat.
_C.NURBS.HEIGHT = 'inherit'  # in m
# Both of these are used per facet!
_C.NURBS.ROWS = 8
_C.NURBS.COLS = 8

# H = Heliostat
_C.H = CN()
# Parameters to optimize. May be any combinations of:
# - 'surface'
# - 'position'
# - 'facet_positions'
# - 'rotation_x'
# - 'rotation_y'
# - 'rotation_z'
_C.H.TO_OPTIMIZE = [
    'surface',
]

_C.H.SHAPE = "real"  # SWITCH FOR HELIOSTAT MODELS: Ideal, Real, Function, Other, NURBS
_C.H.ROTATION_OFFSET = 0

_C.H.GEOMETRY = CN()
# This values are used as memory for the geometry values of the current heliostat. Its a dirty solution,
# but by this the diff-Raytracer is still similar to Max original Version

_C.H.GEOMETRY.ALPHA = 1.570796326795
_C.H.GEOMETRY.BETA = 1.570796326795
_C.H.GEOMETRY.AXIS1K = 0
_C.H.GEOMETRY.AXIS2K = 1.
_C.H.GEOMETRY.GAMMA = 0.0
_C.H.GEOMETRY.DELTA = 0.0
_C.H.GEOMETRY.AXIS1K = 0
_C.H.GEOMETRY.AXIS2K = 1.
_C.H.GEOMETRY.GAMMA = 0.0
_C.H.GEOMETRY.DELTA = 0.0

# AA44
# _C.H.GEOMETRY.ALPHA                     = 1.5677417495165276
# _C.H.GEOMETRY.BETA                      = 1.579971974709824
# _C.H.GEOMETRY.AXIS1K                    = 0.023067549140176884
# _C.H.GEOMETRY.AXIS2K                    = 0.9443208627940167
# _C.H.GEOMETRY.GAMMA                     = 0.06935209640988184
# _C.H.GEOMETRY.DELTA                     = 0.07576299373651274

_C.H.GEOMETRY.RANDOMIZE_GEOMETRY = False

_C.H.GEOMETRY.RANDOMIZE = CN()
# Diese Werte wurden aus der calibdata.csv ausgelesen:
_C.H.GEOMETRY.RANDOMIZE.ALPHA_PARA = (1.05, 1.85)  # minimum und maximum von alpha
_C.H.GEOMETRY.RANDOMIZE.BETA_PARA = (1.5, 1.75)
_C.H.GEOMETRY.RANDOMIZE.AXIS1K_PARA = (-0.1, 0.2)
_C.H.GEOMETRY.RANDOMIZE.AXIS2K_PARA = (0.6, 1.2)
# Diese Werte wurden angenommen:
_C.H.GEOMETRY.RANDOMIZE.GAMMA_PARA = (-0.000001, 0.000001)
_C.H.GEOMETRY.RANDOMIZE.DELTA_PARA = (-0.0005, 0.0005)
_C.H.GEOMETRY.RANDOMIZE.RANDOMIZE_EVERY_SUNPOS = 0.05

_C.H.IDEAL = CN()
_C.H.IDEAL.POSITION_ON_FIELD = [0, 0, 0]  # in m
_C.H.IDEAL.NORMAL_VECS = [0, 0, 1]
_C.H.IDEAL.WIDTH = 4  # in m
_C.H.IDEAL.HEIGHT = 4  # in m
_C.H.IDEAL.ROWS = 32
_C.H.IDEAL.COLS = 32

# Where to aim the heliostat. If `None`, automatically aim at
# `cfg.AC.RECEIVER.CENTER`.
_C.H.IDEAL.AIM_POINT = None
# Rotational disturbance angles (x, y and z axes) in degrees.
_C.H.IDEAL.DISTURBANCE_ROT_ANGLES = [0.0, 0.0, 0.0]
_C.H.IDEAL.FACETS = CN()
_C.H.IDEAL.FACETS.POSITIONS = [
    [1.0, -1.0, 0.0],
    [-1.0, 1.0, 0.0],
    [1.0, -1.0, 0.0],
    [-1.0, 1.0, 0.0],
]
# Relative to `cfg.H.IDEAL.FACETS.POSITIONS`. These also give half of the
# width and height of the heliostat; see STRAL deflectometry data
# format. If a single value, it will be used for all positions.
# Spans in the north direction.
_C.H.IDEAL.FACETS.SPANS_N = [0.0, 1.0, 0.0]
# Spans in the east direction.
_C.H.IDEAL.FACETS.SPANS_E = [-1.0, 0.0, 0.0]

# See `cfg.NURBS.FACETS.CANTING` for documentation.
_C.H.IDEAL.FACETS.CANTING = CN()
_C.H.IDEAL.FACETS.CANTING.FOCUS_POINT = 0
_C.H.IDEAL.FACETS.CANTING.ALGORITHM = 'standard'

_C.H.FUNCTION = CN()
_C.H.FUNCTION.POSITION_ON_FIELD = [0, 0, 0]  # in m
_C.H.FUNCTION.WIDTH = 4  # in m
_C.H.FUNCTION.HEIGHT = 4  # in m
_C.H.FUNCTION.ROWS = 64
_C.H.FUNCTION.COLS = 64
_C.H.FUNCTION.NAME = "sin"
_C.H.FUNCTION.FREQUENCY = 2
_C.H.FUNCTION.REDUCTION_FACTOR = 1000

# See `cfg.H.IDEAL` for documentation.
_C.H.FUNCTION.AIM_POINT = None
_C.H.FUNCTION.DISTURBANCE_ROT_ANGLES = [0.0, 0.0, 0.0]
_C.H.FUNCTION.FACETS = CN()
_C.H.FUNCTION.FACETS.POSITIONS = _C.H.IDEAL.FACETS.POSITIONS.copy()
_C.H.FUNCTION.FACETS.SPANS_N = _C.H.IDEAL.FACETS.SPANS_N.copy()
_C.H.FUNCTION.FACETS.SPANS_E = _C.H.IDEAL.FACETS.SPANS_E.copy()

_C.H.FUNCTION.FACETS.CANTING = CN()
_C.H.FUNCTION.FACETS.CANTING.FOCUS_POINT = 0
_C.H.FUNCTION.FACETS.CANTING.ALGORITHM = 'standard'

_C.H.DEFLECT_DATA = CN()
# IF `None`, use position from file.
_C.H.DEFLECT_DATA.DIRECTORY = 'MeasurementData'
_C.H.DEFLECT_DATA.POSITION_ON_FIELD = None  # in m
_C.H.DEFLECT_DATA.FILENAME = "Helio_AA39_Rim0_STRAL-Input_211028212814.binp"
_C.H.DEFLECT_DATA.ZS_PATH = "Helio_AA39_Rim0_LocalResults_220303111914.csv"
_C.H.DEFLECT_DATA.VERBOSE = True

_C.H.DEFLECT_DATA.TAKE_N_VECTORS = 8000
_C.H.DEFLECT_DATA.CONCENTRATORHEADER_STRUCT_FMT = '=5f2I2f'
_C.H.DEFLECT_DATA.FACETHEADER_STRUCT_FMT = '=i9fI'
_C.H.DEFLECT_DATA.RAY_STRUCT_FMT = '=7f'

# See `cfg.H.IDEAL` for documentation.
_C.H.DEFLECT_DATA.AIM_POINT = None
_C.H.DEFLECT_DATA.DISTURBANCE_ROT_ANGLES = [0.0, 0.0, 0.0]
_C.H.DEFLECT_DATA.FACETS = CN()
# Positions and spans are read from the data.
_C.H.DEFLECT_DATA.FACETS.CANTING = CN()
_C.H.DEFLECT_DATA.FACETS.CANTING.FOCUS_POINT = 0
_C.H.DEFLECT_DATA.FACETS.CANTING.ALGORITHM = 'standard'
_C.H.DEFLECT_DATA.FACETS.CANTING.TO_RECEIVER = False  # All heliostats have ideal canting vectors for canting on the receiver

_C.H.NURBS = CN()
_C.H.NURBS.MAX_ABS_NOISE = 0.01

_C.H.NURBS.SPLINE_DEGREE = 3
# Position, width, height, rows, cols (discretization dimensions), and
# facet/canting parameters given by `_C.H.IDEAL`.
# These are again the NURBS rows/cols of the control point matrix.
_C.H.NURBS.ROWS = 8
_C.H.NURBS.COLS = 8

_C.H.OTHER = CN()
_C.H.OTHER.FILENAME = 'tinker.obj'
_C.H.OTHER.USE_WEIGHTED_AVG = True

# See `cfg.H.IDEAL` for documentation.
_C.H.OTHER.AIM_POINT = None
_C.H.OTHER.DISTURBANCE_ROT_ANGLES = [0.0, 0.0, 0.0]
_C.H.OTHER.FACETS = CN()
_C.H.OTHER.POSITION_ON_FIELD = [0, 0, 0]  # in m
_C.H.OTHER.FACETS.POSITIONS = [0.0, 0.0, 0.0]
_C.H.OTHER.FACETS.SPANS_N = [0.0, float('inf'), 0.0]
_C.H.OTHER.FACETS.SPANS_E = [-float('inf'), 0.0, 0.0]
_C.H.OTHER.FACETS.CANTING = CN()
_C.H.OTHER.FACETS.CANTING.FOCUS_POINT = 0
_C.H.OTHER.FACETS.CANTING.ALGORITHM = 'standard'

# TODO add heliostat up vec ("rotation")

# AC = Ambiant Conditions
_C.AC = CN()
_C.AC.RECEIVER = CN()
# in m in global coordinates

_C.AC.RECEIVER.CENTER = [0, 0, 55]
_C.AC.RECEIVER.PLANE_NORMAL = [0, 1, 0]  # NWU
_C.AC.RECEIVER.PLANE_X = 4  # in m
_C.AC.RECEIVER.PLANE_Y = 4  # in m
# These X and Y are height and width respectively.
_C.AC.RECEIVER.RESOLUTION_X = 128
_C.AC.RECEIVER.RESOLUTION_Y = 128
_C.AC.RECEIVER.PLANE_NORMAL = [0, 1, 0]  # NWU

_C.AC.FIELD = CN()
_C.AC.FIELD.SIZE_X = [-300, 300]
_C.AC.FIELD.SIZE_Y = [0, 300]
_C.AC.FIELD.SIZE_Z = [0, 4]

# Die Werte für die Targets sind die aus HeliOS. Allerdings musst umgerechnet
# werden zwischen der Definitionen für die mittlere Kante des Targets.
_C.AC.TARGET = CN()
_C.AC.TARGET.TARGET7 = CN()  # target 7 ist das untere Target am STJ
_C.AC.TARGET.TARGET7.CENTER = [0.018, -3.235, 36.075 - 0.375 / 2]
_C.AC.TARGET.TARGET7.PLANE_X = 8.63
_C.AC.TARGET.TARGET7.PLANE_Y = 7.59 - 0.375

_C.AC.TARGET.TARGET6 = CN()  # target 6 ist das obere Target am STJ
_C.AC.TARGET.TARGET6.CENTER = [0.014, -3.237, 42.90875 + 0.375 / 2]
_C.AC.TARGET.TARGET6.PLANE_X = 8.63
_C.AC.TARGET.TARGET6.PLANE_Y = 7.59 - 0.375

_C.AC.TARGET.TARGET3 = CN()  # target 3 ist das MFT Target
_C.AC.TARGET.TARGET3.CENTER = [-17.59, -2.84, 51.98]
_C.AC.TARGET.TARGET3.PLANE_X = 5.412
_C.AC.TARGET.TARGET3.PLANE_Y = 6.388

_C.AC.TARGET.EVALUATION_SIZE = 4

_C.AC.SUN = CN()

_C.AC.SUN.GENERATE_N_RAYS = 400  # self.num_rays per discrete_point
_C.AC.SUN.DISTRIBUTION = "Buie"  # Normal, Buie
_C.AC.SUN.REDRAW_RANDOM_VARIABLES = True  # TODO schauen wo das aufgerufen wird
_C.AC.SUN.NORMAL_DIST = CN()
_C.AC.SUN.NORMAL_DIST.MEAN = [0, 0]
_C.AC.SUN.NORMAL_DIST.COV = [[0.002090 ** 2, 0], [0, 0.002090 ** 2]]  # von Max
# _C.AC.SUN.NORMAL_DIST.COV               = [[0.0026**2, 0], [0, 0.0026**2]]

_C.AC.SUN.BUIE_DIST = CN()
_C.AC.SUN.BUIE_DIST.CSR = 0.05
_C.AC.SUN.BUIE_DIST.THETA_MAX = 20  # maximum sampling interval (mrad)

_C.TRAIN = CN()
_C.TRAIN.IMG_INTERVAL = 50
_C.TRAIN.PRETRAIN_EPOCHS = 0
_C.TRAIN.EPOCHS = 3000
_C.TRAIN.USE_IMAGES = False

_C.TRAIN.IMAGES = CN()
# Remember to set sun directions accordingly!
_C.TRAIN.IMAGES.PATHS = ['Transform.png']

_C.TRAIN.SUN_DIRECTIONS = CN()
_C.TRAIN.SUN_DIRECTIONS.CASE = "random"  # SWITCH FOR SUN_DIRECTIONS DIRECTION VEKTOR GENERATION: vecs, random, grid

_C.TRAIN.SUN_DIRECTIONS.VECS = CN()
_C.TRAIN.SUN_DIRECTIONS.VECS.DIRECTIONS = [[-0.43719268, 0.7004466, 0.564125], ]

_C.TRAIN.SUN_DIRECTIONS.RAND = CN()
_C.TRAIN.SUN_DIRECTIONS.RAND.NUM_SAMPLES = 10
_C.TRAIN.SUN_DIRECTIONS.RAND.LATITUDE = 50.92
_C.TRAIN.SUN_DIRECTIONS.RAND.LONGITUDE = 6.36

_C.TRAIN.SUN_DIRECTIONS.GRID = CN()
_C.TRAIN.SUN_DIRECTIONS.GRID.AZI_RANGE = [-90, 90, 3]  # Start,Stop,Step
_C.TRAIN.SUN_DIRECTIONS.GRID.ELE_RANGE = [20, 80, 3]  # Start,Stop,Step

# These scheduler settings affect all parameter groups.
# Only some PyTorch schedulers support per-parameter-group options and
# even then only for some keywords.
_C.TRAIN.SCHEDULER = CN()
_C.TRAIN.SCHEDULER.NAME = "Exponential"  # SWITCH FOR SCHEDULER: ReduceOnPLateau, Cyclic, OneCycle

_C.TRAIN.SCHEDULER.EXP = CN()
_C.TRAIN.SCHEDULER.EXP.GAMMA = 0.995

_C.TRAIN.SCHEDULER.ROP = CN()
_C.TRAIN.SCHEDULER.ROP.FACTOR = 0.1
_C.TRAIN.SCHEDULER.ROP.MIN_LR = 1e-7
_C.TRAIN.SCHEDULER.ROP.PATIENCE = 20
_C.TRAIN.SCHEDULER.ROP.COOLDOWN = 10
_C.TRAIN.SCHEDULER.ROP.VERBOSE = True

_C.TRAIN.SCHEDULER.CYCLIC = CN()
_C.TRAIN.SCHEDULER.CYCLIC.BASE_LR = 1e-7
_C.TRAIN.SCHEDULER.CYCLIC.MAX_LR = 8e-6
_C.TRAIN.SCHEDULER.CYCLIC.STEP_SIZE_UP = 100
_C.TRAIN.SCHEDULER.CYCLIC.CYCLE_MOMENTUM = False
_C.TRAIN.SCHEDULER.CYCLIC.MODE = "triangular2"

_C.TRAIN.SCHEDULER.ONE_CYCLE = CN()
_C.TRAIN.SCHEDULER.ONE_CYCLE.MAX_LR = 1e-4
_C.TRAIN.SCHEDULER.ONE_CYCLE.START_LR = 1e-10
_C.TRAIN.SCHEDULER.ONE_CYCLE.FINAL_LR = 1e-8
_C.TRAIN.SCHEDULER.ONE_CYCLE.PCT_START = 0.3
_C.TRAIN.SCHEDULER.ONE_CYCLE.THREE_PHASE = True

_C.TRAIN.OPTIMIZER = CN()
# Valid optimizer names:
# - Adam
# - Adamax
# - AdamW
# - LBFGS
# - BasinHopping
_C.TRAIN.OPTIMIZER.NAME = "Adam"
# These values are all for the surface parameters.
# They are also defaults if other parameter groups do not contain have a
# certain config parameter.
_C.TRAIN.OPTIMIZER.LR = 0.00001

_C.TRAIN.OPTIMIZER.BETAS = [0.9, 0.999]
_C.TRAIN.OPTIMIZER.EPS = 1e-8
_C.TRAIN.OPTIMIZER.WEIGHT_DECAY = 0.1

_C.TRAIN.LOSS = CN()
_C.TRAIN.LOSS.FACTOR = 1.0
_C.TRAIN.LOSS.NAME = "L1"  # SWITCH FOR LOSS: L1, MSE
_C.TRAIN.LOSS.MISS = CN()
_C.TRAIN.LOSS.MISS.FACTOR = 1e12
_C.TRAIN.LOSS.MISS.NAME = "L1"
_C.TRAIN.LOSS.ALIGNMENT = CN()
_C.TRAIN.LOSS.ALIGNMENT.FACTOR = 1.0
_C.TRAIN.LOSS.ALIGNMENT.NAME = "L1"
_C.TRAIN.LOSS.USE_L1_WEIGHT_DECAY = True
_C.TRAIN.LOSS.WEIGHT_DECAY_FACTOR = 0.2

_C.TRAIN.LOSS.HAUSDORFF = CN()
_C.TRAIN.LOSS.HAUSDORFF.FACTOR = 0.0
_C.TRAIN.LOSS.HAUSDORFF.CONTOUR_VALS = [0.2, 0.4, 0.6, 0.8, 1.0]
_C.TRAIN.LOSS.HAUSDORFF.CONTOUR_VAL_RADIUS = 0.05
_C.TRAIN.LOSS.HAUSDORFF.NORM_P = 2.0
_C.TRAIN.LOSS.HAUSDORFF.MEAN_P = -1.0

# These values are for the position parameters.
_C.TRAIN.OPTIMIZER.POSITION = CN()
_C.TRAIN.OPTIMIZER.POSITION.LR = 1e-4
_C.TRAIN.OPTIMIZER.POSITION.WEIGHT_DECAY = 0.0
_C.TRAIN.LOSS.POSITION = CN()
_C.TRAIN.LOSS.POSITION.USE_L1_WEIGHT_DECAY = True
_C.TRAIN.LOSS.POSITION.WEIGHT_DECAY_FACTOR = 0.0

_C.TRAIN.OPTIMIZER.FACET_POSITIONS = CN()
_C.TRAIN.OPTIMIZER.FACET_POSITIONS.LR = 3e-2
_C.TRAIN.OPTIMIZER.FACET_POSITIONS.WEIGHT_DECAY = 0.0
_C.TRAIN.LOSS.FACET_POSITIONS = CN()
_C.TRAIN.LOSS.FACET_POSITIONS.USE_L1_WEIGHT_DECAY = True
_C.TRAIN.LOSS.FACET_POSITIONS.WEIGHT_DECAY_FACTOR = 0.0

# These values are for the rotation parameters.
_C.TRAIN.OPTIMIZER.ROTATION_X = CN()
_C.TRAIN.OPTIMIZER.ROTATION_X.LR = 1e-4
_C.TRAIN.OPTIMIZER.ROTATION_X.WEIGHT_DECAY = 0.0
_C.TRAIN.LOSS.ROTATION_X = CN()
_C.TRAIN.LOSS.ROTATION_X.USE_L1_WEIGHT_DECAY = True
_C.TRAIN.LOSS.ROTATION_X.WEIGHT_DECAY_FACTOR = 0.0

_C.TRAIN.OPTIMIZER.ROTATION_Y = CN()
_C.TRAIN.OPTIMIZER.ROTATION_Y.LR = 1e-4
_C.TRAIN.OPTIMIZER.ROTATION_Y.WEIGHT_DECAY = 0.0
_C.TRAIN.LOSS.ROTATION_Y = CN()
_C.TRAIN.LOSS.ROTATION_Y.USE_L1_WEIGHT_DECAY = True
_C.TRAIN.LOSS.ROTATION_Y.WEIGHT_DECAY_FACTOR = 0.0

_C.TRAIN.OPTIMIZER.ROTATION_Z = CN()
_C.TRAIN.OPTIMIZER.ROTATION_Z.LR = 1e-4
_C.TRAIN.OPTIMIZER.ROTATION_Z.WEIGHT_DECAY = 0.0
_C.TRAIN.LOSS.ROTATION_Z = CN()
_C.TRAIN.LOSS.ROTATION_Z.USE_L1_WEIGHT_DECAY = True
_C.TRAIN.LOSS.ROTATION_Z.WEIGHT_DECAY_FACTOR = 0.0

_C.TEST = CN()
_C.TEST.INTERVAL = 100
_C.TEST.USE_IMAGES = False

_C.TEST.IMAGES = CN()
# Remember to set sun directions accordingly!
_C.TEST.IMAGES.PATHS = []

# Reduces test image array to 5, images will be generated with complete array

_C.TEST.SUN_DIRECTIONS = CN()
_C.TEST.SUN_DIRECTIONS.CASE = "random"  # SWITCH FOR SUN DIRECTION VEKTOR GENERATION: vecs, random, grid

_C.TEST.SUN_DIRECTIONS.VECS = CN()
_C.TEST.SUN_DIRECTIONS.VECS.DIRECTIONS = [[-0.8662, 0.4890, 0.1026], ]  # Measurement Date 28.10.21 15:30

_C.TEST.SUN_DIRECTIONS.RAND = CN()
_C.TEST.SUN_DIRECTIONS.RAND.NUM_SAMPLES = 5
_C.TEST.SUN_DIRECTIONS.RAND.LATITUDE = 50.92
_C.TEST.SUN_DIRECTIONS.RAND.LONGITUDE = 6.36

_C.TEST.SUN_DIRECTIONS.GRID = CN()
_C.TEST.SUN_DIRECTIONS.GRID.AZI_RANGE = [-90, 90, 7]  # Start,Stop,Step
_C.TEST.SUN_DIRECTIONS.GRID.ELE_RANGE = [20, 80, 3]  # Start,Stop,Step
_C.TEST.SUN_DIRECTIONS.GRID.PLOT = True

_C.TEST.SUN_DIRECTIONS.SPHERIC = CN()
_C.TEST.SUN_DIRECTIONS.SPHERIC.NUM_SAMPLES = 10

_C.TEST.PLOT = CN()
_C.TEST.PLOT.SPHERIC = False
_C.TEST.PLOT.GRID = False
_C.TEST.PLOT.SEASON = False
_C.TEST.PLOT.REAL_DATA = False

_C.TARGETIMAGES = CN()
_C.TARGETIMAGES.LOW_PASS_DIM = 20
_C.TARGETIMAGES.CENTER_OF_MASS_RATIO = 0.25  # das center of mass darf nicht im äußeren viertel liegen
_C.TARGETIMAGES.FLUX_MULTIPLYIER = 100  # das integral der Targetbilder muss 1 betragen und wird dann multipliziert
_C.TARGETIMAGES.SUNPOS_LIMITS_E = [-0.9528781449839675, 0.9420774665454292]
_C.TARGETIMAGES.SUNPOS_LIMITS_N = [-0.8584008684294668, 0.2552716733585961]
_C.TARGETIMAGES.SUNPOS_LIMITS_U = [0.3000069281443151, 0.8872665284279267]

_C.DEEPLARTS = CN()

_C.DEEPLARTS.TRAIN = CN()
_C.DEEPLARTS.TRAIN.TARGET_IMAGE_SIZE = 64
_C.DEEPLARTS.TRAIN.SURFACE_MIN = -0.004
_C.DEEPLARTS.TRAIN.SURFACE_MAX = 0.004
_C.DEEPLARTS.TRAIN.NSUNPOS = 8
_C.DEEPLARTS.TRAIN.TARGET_IDs = [6, 7]
_C.DEEPLARTS.TRAIN.NSAMPLES_TRAINLOSS = 1000

_C.DEEPLARTS.TRAIN.SKIPLIST = ['AA32_210819', 'AA31_210819', 'AA36_150723', 'AA38_140910', 'AB35_210819', 'AB43_220303',
                               'AC35_210819', 'AC36_210819', 'AC37_210819', 'AD35_210819',
                               'AD36_210819', 'AD37_210819', 'AH36_160407', 'AI21_160510', 'AI43_171122', 'AI44_171122',
                               'AI45_171122', 'AK30_210909', 'AK31_210909', 'AK32_210909', 'AK33_210909', 'AK34_210909',
                               'AK35_210909', 'AK36_210909', 'AK37_210909', 'AN33_220303', 'AN35_220303', 'AO33_210909',
                               'AO33_220303', 'AO34_220303', 'AO35_220303', 'AO49_220303', 'AP34_220303', 'AP35_220303',
                               'AP38_180807', 'AP49_220303', 'AP50_220303', 'AP51_220303', 'AP60_220303', 'AQ25_210909',
                               'AQ26_210909', 'AU66_160510', 'AV36_150424', 'AV38_141125', 'AY19_160510', 'AY36_160510',
                               'AY41_160510', 'AY55_220303', 'AY57_220303', 'AZ43_150428', 'AZ56_220303', 'BA41_150424',
                               'BB40_220303', 'BD34_150803', 'BF27_160510', 'BF29_160510', 'BF37_160510', 'BF39_160510',
                               'BG25_160510', 'BG30_160510', 'BG34_160510', 'BJ25_190227', 'BJ26_190227', 'BJ27_190227',
                               'BJ28_190227', 'BJ30_190227', 'BJ31_190227', 'BJ32_190227', 'BJ32_191114', 'BK19_160510',
                               'BL31_161005', 'BM23_160808', 'BM25_160808', 'BM27_160808', 'BM29_160808', 'BM31_160808',
                               'BM33_160808', 'BM35_160808', 'BM35_161011', 'BM37_161005', 'BM37_161011', 'BM39_160808',
                               'BM41_160808', 'BM43_160808', 'BM45_160808', 'BM47_160808', 'BM49_160808', 'BM51_160808',
                               'BM53_160808', 'BM55_160808', 'BM55_161005', 'BM55_161011', 'BN26_160510', 'BN26_160808',
                               'BN28_160808', 'BN30_160510', 'BN30_160808', 'BN32_160510', 'BN32_160808', 'BN34_160510',
                               'BN34_160808', 'BN36_160808', 'BN38_160510', 'BN38_160808', 'BN40_161005', 'BN40_161011',
                               'BN42_160808', 'BN46_160808', "AA28_230907", "AB26_230907", "AB27_230907", 'AB45_230907',
                               "AY37_150424", "AC35_210819", "AL30_150424", "AL30_150422", "AL30_150723", "AM31_150723",
                               "AL30_160510", "AM31_160510", "AL30_191114", "AM31_191114", "AB46_230907", "AB47_230907",
                               "AC48_230907"]

_C.DEEPLARTS.TRAIN.PICEOFFACETMISSINGLIST = ['AA49_140910', 'AA50_140910', 'AI32_171122', 'AI33_171122', 'AI34_171122',
                                             'AI35_171122', 'AO51_220303', 'AP28_180807', 'AP29_180807', 'AP30_180807',
                                             'AP31_180807',
                                             'AP32_180807', 'AP61_220303', 'AQ24_210909', 'AQ28_210909', 'AQ30_210909',
                                             'AQ31_210909', 'AQ32_210909', 'AU65_160510', 'AU68_160510', 'AU69_160510',
                                             'AU71_160510',
                                             'AY37_150424', 'AY37_160510', 'AZ21_160510', 'AZ26_220303', 'AZ27_220303',
                                             'AZ28_220303', 'AZ33_150424', 'AZ33_150428', 'AZ34_150428', 'BH49_191114',
                                             'BH65_160510']

_C.DEEPLARTS.DOMAIN_RANDOMIZATION = CN()
_C.DEEPLARTS.REDUCE_FLUX = True
_C.DEEPLARTS.P_REDUCE_FLUX = 0.5

_C.DEEPLARTS.JITTER_HELPOS = False
_C.DEEPLARTS.P_JITTER_HELPOS = 0.8
_C.DEEPLARTS.PARA_JITTER_HELPOS = 0.005

_C.DEEPLARTS.JITTER_SUNPOS = False
_C.DEEPLARTS.P_JITTER_SUNPOS = 0.7
_C.DEEPLARTS.PARA_JITTER_SUNPOS = 0.0002

_C.DEEPLARTS.APPLY_LOWPASS = False
_C.DEEPLARTS.P_APPLY_LOWPASS = 0.5
_C.DEEPLARTS.PARA_LOWPASS = 5

_C.DEEPLARTS.APPLY_SURFACE_NOISE = False
_C.DEEPLARTS.P_APPLY_SURFACE_NOISE = 0.7
_C.DEEPLARTS.PARA_SURFACE_NOISE = 1e-7

_C.DEEPLARTS.VALID = CN()

_C.DEEPLARTS.VALID.TESTSET = ['AA35', 'AY26', 'AA44', 'AB44', 'AO51', 'AX56', 'BB39', 'BB41', 'AC30',
                              'AC35', 'AC38', 'AC42', 'AD29', 'AD33', 'AD36', 'AD42', 'AD44', 'AE26', 'AE29',
                              'AE34', 'AF46', 'AF42', 'AF37', 'AF31', 'AY32', 'AY37', 'AY60', 'BA27',
                              'BA29', 'BC60']

_C.DEEPLARTS.VALID.VALIDSET = ["AA31_230907", "AA39_230907", "AB39_230907", "AB42_230907",
                               "AC37_230907", "AC39_230907", "AC40_230907", "AC43_230907", "AD30_230907",

                               "AD31_230907", "AD34_230907", "AD35_230907", "AD37_230907", "AD40_230907",
                               "AD45_230907", "AD46_230907", "AE25_230907", "AE27_230907", "AE30_230907",

                               "AF32_230907", "AF33_230907", "AF34_230907", "AF38_230907", "AF39_230907",
                               "AF40_230907", "AF41_230907", "AF44_230907", "AF45_230907", "AG25_220303",

                               "AG26_220303", "AG28_220303", "AH28_220303", "AH38_220303", "AH39_220303",
                               "AH40_220303", "AI37_220303", "AK39_220303", "AM35_220303", "AN34_220303",

                               "AX54_220303", "AY28_220303", "AY35_230907", "AY36_230907", "AY38_230907",
                               "AY39_230907", "AZ55_220303", "BA28_230206", "BA61_230206", "BA61_230207",

                               "BA62_230206", "BA62_230207", "BA63_230206", "BA65_230206", "BC61_230206",
                               "BC62_230206", "BC64_230206", "BC66_230206"]

_C.DEEPLARTS.VALID.ACCURACY_LIMIT = 0.75
_C.DEEPLARTS.VALID.N_INPUT_TARGETIMAGES = 5
_C.DEEPLARTS.VALID.N_TARGET_TARGETIMAGES = 3

_C.DEEPLARTS.VALID.UNET = "raytracer"  # raytracer, GAN

_C.DEEPLARTS.VALID.SESSIONS = ['220303', '230206', '230207', '230907']
_C.DEEPLARTS.VALID.SURFACEDIR = r'C:\Users\lewe_jn\Desktop\gancstr\rawdata\deflektometrie\discrete_points\data'

_C.DIRECTORIES = CN()
_C.DIRECTORIES.LOCAL = CN()
_C.DIRECTORIES.LOCAL.HOMEDIR = r'C:\Users\anton\Desktop\Masterarbeit\Masterthesis\Unsupervised_learning'
# _C.DIRECTORIES.LOCAL.HOMEDIR = r'C:\Users\lewe_jn\Desktop\gancstr'
_C.DIRECTORIES.LOCAL.CODEDIR = os.path.join(_C.DIRECTORIES.LOCAL.HOMEDIR, 'juwels', 'code')
_C.DIRECTORIES.LOCAL.LIVEIMGDIR = os.path.join(_C.DIRECTORIES.LOCAL.CODEDIR, 'liveimgs')
_C.DIRECTORIES.LOCAL.CHECKPOINTDIR = os.path.join(_C.DIRECTORIES.LOCAL.CODEDIR, 'checkpoints')
_C.DIRECTORIES.LOCAL.DATADIR = os.path.join(_C.DIRECTORIES.LOCAL.HOMEDIR, 'Data')
_C.DIRECTORIES.LOCAL.TRAININGDATADIR = os.path.join(_C.DIRECTORIES.LOCAL.HOMEDIR, 'juwels', 'data', 'trainingdata')
_C.DIRECTORIES.LOCAL.EMPTYTARGETDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "EmptyTargetImages")
_C.DIRECTORIES.LOCAL.RAWDATADIR = os.path.join(_C.DIRECTORIES.LOCAL.HOMEDIR, 'rawdata')
_C.DIRECTORIES.LOCAL.DEFLDIR = os.path.join(_C.DIRECTORIES.LOCAL.DATADIR, 'deflectometry_non_filled')
_C.DIRECTORIES.LOCAL.TARGETIMAGEFOLDERDIR = os.path.join(_C.DIRECTORIES.LOCAL.RAWDATADIR, 'targetImages')
_C.DIRECTORIES.LOCAL.CALIBDATADIR = os.path.join(_C.DIRECTORIES.LOCAL.CODEDIR, 'calibdata.csv')
_C.DIRECTORIES.LOCAL.DFCALIBDATADIR = os.path.join(_C.DIRECTORIES.LOCAL.CODEDIR, 'calibdata.pd')
_C.DIRECTORIES.LOCAL.CNTRLPOINTSDIR = os.path.join(_C.DIRECTORIES.LOCAL.DATADIR, 'cntrl_points')
_C.DIRECTORIES.LOCAL.RESULTSDIR = os.path.join(_C.DIRECTORIES.LOCAL.CODEDIR, 'results')
_C.DIRECTORIES.LOCAL.DATAGENDIR = os.path.join(_C.DIRECTORIES.LOCAL.RESULTSDIR, 'data_generation')
_C.DIRECTORIES.LOCAL.TARGETIMAGEDIR = os.path.join(_C.DIRECTORIES.LOCAL.TARGETIMAGEFOLDERDIR, 'targetImages_Jan')
# _C.DIRECTORIES.LOCAL.MARKERDIR = 'C:/Users/lewe_jn/Desktop/data/targetImages/marker/'
_C.DIRECTORIES.LOCAL.CROPPEDIMAGEDIR = os.path.join(_C.DIRECTORIES.LOCAL.TARGETIMAGEFOLDERDIR, 'targetImages_cropped')
_C.DIRECTORIES.LOCAL.UNETIMAGEDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, 'unetImages')
_C.DIRECTORIES.LOCAL.SIMULATEDDIR = os.path.join(_C.DIRECTORIES.LOCAL.DATADIR, 'simulated')
_C.DIRECTORIES.LOCAL.SAVESIMULATEDDIR = os.path.join(_C.DIRECTORIES.LOCAL.SIMULATEDDIR, 'generated')
_C.DIRECTORIES.LOCAL.DEFLFILLED = os.path.join(_C.DIRECTORIES.LOCAL.DATADIR, 'Deflectometry_Daten')

_C.DIRECTORIES.LOCAL.SAVESIMULATEDTRAINDIR = os.path.join(_C.DIRECTORIES.LOCAL.SAVESIMULATEDDIR, 'train')
_C.DIRECTORIES.LOCAL.SAVESIMULATEDVALIDDIR = os.path.join(_C.DIRECTORIES.LOCAL.SAVESIMULATEDDIR, 'valid')
_C.DIRECTORIES.LOCAL.SAVESIMULATEDSIMREALDIR = os.path.join(_C.DIRECTORIES.LOCAL.SAVESIMULATEDDIR, 'simreal')

_C.DIRECTORIES.LOCAL.SIMULATEDTRAINDIR = os.path.join(_C.DIRECTORIES.LOCAL.SIMULATEDDIR, 'train')
_C.DIRECTORIES.LOCAL.SIMULATEDVALIDDIR = os.path.join(_C.DIRECTORIES.LOCAL.SIMULATEDDIR, 'valid')
_C.DIRECTORIES.LOCAL.SIMULATEDTESTDIR = os.path.join(_C.DIRECTORIES.LOCAL.SIMULATEDDIR, 'test')
_C.DIRECTORIES.LOCAL.SIMULATEDDISTANCEDIR = os.path.join(_C.DIRECTORIES.LOCAL.SIMULATEDDIR, 'distance_valid')
_C.DIRECTORIES.LOCAL.SIMULATEDSIMREALDIR = os.path.join(_C.DIRECTORIES.LOCAL.SIMULATEDDIR, 'simreal')

_C.DIRECTORIES.LOCAL.SIMREALDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "simreal")
_C.DIRECTORIES.LOCAL.VALIDREAL = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "simreal")
_C.DIRECTORIES.LOCAL.TESTREAL = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "simreal")
_C.DIRECTORIES.LOCAL.TRAINDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "train")
_C.DIRECTORIES.LOCAL.RAWTRAINDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "train_raw")
_C.DIRECTORIES.LOCAL.VALIDDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "valid")
_C.DIRECTORIES.LOCAL.TESTDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "test")
_C.DIRECTORIES.LOCAL.TESTREALDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "simreal",
                                                _C.DEEPLARTS.VALID.UNET, 'test')
_C.DIRECTORIES.LOCAL.VALIDREALDIR = os.path.join(_C.DIRECTORIES.LOCAL.TRAININGDATADIR, "simreal",
                                                 _C.DEEPLARTS.VALID.UNET, 'valid')

_C.DIRECTORIES.LOCAL.MODELDIR = os.path.join(_C.DIRECTORIES.LOCAL.CODEDIR, 'models', 'deepLarts')

_C.DIRECTORIES.JUWELS = CN()
_C.DIRECTORIES.JUWELS.SUNPOSDIR = '/p/project1/hai_gancstr/lewen1/gancstr/juwels/code/heldata/sunPos_real.pt'
_C.DIRECTORIES.JUWELS.POSDIR = '/p/project1/hai_gancstr/lewen1/gancstr/juwels/code/heldata/heliostat_position_dictionary.npy'
_C.DIRECTORIES.JUWELS.MODELDIR = '/p/project1/hai_gancstr/lewen1/gancstr/juwels/code/models/deepLarts/'
_C.DIRECTORIES.JUWELS.CODEDIR = '/p/project1/hai_gancstr/lewen1/gancstr/juwels/code/'

_C.DIRECTORIES.JUWELS.DATADIR = '/p/project1/hai_gancstr/lewen1/gancstr/juwels/data'
_C.DIRECTORIES.JUWELS.TRAININGDATADIR = os.path.join(_C.DIRECTORIES.JUWELS.DATADIR, 'trainingdata')
_C.DIRECTORIES.JUWELS.DEFLFILLED = os.path.join(_C.DIRECTORIES.JUWELS.DATADIR, 'deflectometry_filled')
_C.DIRECTORIES.JUWELS.EMPTYTARGETDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "EmptyTargetImages")
_C.DIRECTORIES.JUWELS.DEFLDIR = os.path.join(_C.DIRECTORIES.JUWELS.DATADIR, 'deflectometry_filled')
_C.DIRECTORIES.JUWELS.CNTRLPOINTSDIR = os.path.join(_C.DIRECTORIES.JUWELS.DATADIR, 'cntrl_points')
_C.DIRECTORIES.JUWELS.SIMULATEDDATADIR = os.path.join(_C.DIRECTORIES.JUWELS.DATADIR, 'simulated')

_C.DIRECTORIES.JUWELS.SAVESIMULATEDSIMREALDIR = os.path.join(_C.DIRECTORIES.JUWELS.SIMULATEDDATADIR, "simreal")
_C.DIRECTORIES.JUWELS.SAVESIMULATEDTRAINDIR = os.path.join(_C.DIRECTORIES.JUWELS.SIMULATEDDATADIR, "train")
_C.DIRECTORIES.JUWELS.SAVESIMULATEDVALIDDIR = os.path.join(_C.DIRECTORIES.JUWELS.SIMULATEDDATADIR, "valid")
_C.DIRECTORIES.JUWELS.SAVESIMULATEDTESTDIR = os.path.join(_C.DIRECTORIES.JUWELS.SIMULATEDDATADIR, "test")

_C.DIRECTORIES.JUWELS.SIMREALDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "simreal")
_C.DIRECTORIES.JUWELS.TRAINDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "train")
_C.DIRECTORIES.JUWELS.VALIDDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "valid")
_C.DIRECTORIES.JUWELS.TESTDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "test")
_C.DIRECTORIES.JUWELS.TESTREALDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "simreal",
                                                 _C.DEEPLARTS.VALID.UNET, 'test')
_C.DIRECTORIES.JUWELS.VALIDREALDIR = os.path.join(_C.DIRECTORIES.JUWELS.TRAININGDATADIR, "simreal",
                                                  _C.DEEPLARTS.VALID.UNET, 'valid')

# dieser parameter gibt eine prozentuale veränderung der Geometrieparameter für jede Sonnenposition

_C.STYLEGAN = CN()
_C.STYLEGAN.NAME = 'styleGAN/06-01-2023_15-16-29'
_C.STYLEGAN.LOAD_FROM = r'72'


def get_cfg_defaults() -> CN:
    return _C.clone()


def load_config_file(cfg: CN, config_file_loc: str) -> CN:
    if len(os.path.splitext(config_file_loc)[1]) == 0:
        config_file_loc += '.yaml'
    cfg.merge_from_file(config_file_loc)

    # if experiment_name:
    #     cfg.merge_from_list(["ID", experiment_name])

    return cfg


def merge_any_types() -> None:
    check_and_coerce_cfg_value_type = \
        yacs.config._check_and_coerce_cfg_value_type

    def dont_check_and_coerce_cfg_value_type(
            replacement: Any,
            original: Any,
            key: str,
            full_key: str,
    ) -> Any:
        try:
            return check_and_coerce_cfg_value_type(
                replacement,
                original,
                key,
                full_key,
            )
        except ValueError:
            return replacement

    yacs.config._check_and_coerce_cfg_value_type = \
        dont_check_and_coerce_cfg_value_type


merge_any_types()
