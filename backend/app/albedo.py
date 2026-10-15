import numpy as np

BLUE = 0.356
RED = 0.130
NIR = 0.373
TOTAL = BLUE + RED + NIR

SCALE = 10000.0


def get_albedo(blue, red, nir):
    blue = blue.astype(np.float64) / SCALE
    red = red.astype(np.float64) / SCALE
    nir = nir.astype(np.float64) / SCALE

    albedo = (BLUE * blue + RED * red + NIR * nir) / TOTAL

    below = int(np.sum(albedo < 0.0))
    above = int(np.sum(albedo > 1.0))
    albedo = np.clip(albedo, 0.0, 1.0)

    return albedo, below, above
