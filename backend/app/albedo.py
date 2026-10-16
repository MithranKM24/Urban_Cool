import numpy as np

LIANG_2001_BLUE_COEFFICIENT = 0.356
LIANG_2001_RED_COEFFICIENT = 0.130
LIANG_2001_NIR_COEFFICIENT = 0.373
RENORMALIZATION_DIVISOR = LIANG_2001_BLUE_COEFFICIENT + LIANG_2001_RED_COEFFICIENT + LIANG_2001_NIR_COEFFICIENT

SENTINEL2_REFLECTANCE_SCALE_FACTOR = 10000.0

ALBEDO_VALID_MINIMUM = 0.0
ALBEDO_VALID_MAXIMUM = 1.0


def compute_albedo_from_raw_bands(blue_band_raw, red_band_raw, nir_band_raw):
    blue_reflectance = blue_band_raw.astype(np.float64) / SENTINEL2_REFLECTANCE_SCALE_FACTOR
    red_reflectance = red_band_raw.astype(np.float64) / SENTINEL2_REFLECTANCE_SCALE_FACTOR
    nir_reflectance = nir_band_raw.astype(np.float64) / SENTINEL2_REFLECTANCE_SCALE_FACTOR

    raw_albedo = (
        LIANG_2001_BLUE_COEFFICIENT * blue_reflectance
        + LIANG_2001_RED_COEFFICIENT * red_reflectance
        + LIANG_2001_NIR_COEFFICIENT * nir_reflectance
    ) / RENORMALIZATION_DIVISOR

    number_of_pixels_below_range = int(np.sum(raw_albedo < ALBEDO_VALID_MINIMUM))
    number_of_pixels_above_range = int(np.sum(raw_albedo > ALBEDO_VALID_MAXIMUM))

    clipped_albedo = np.clip(raw_albedo, ALBEDO_VALID_MINIMUM, ALBEDO_VALID_MAXIMUM)

    validation_report = {
        "pixels_clipped_below_zero": number_of_pixels_below_range,
        "pixels_clipped_above_one": number_of_pixels_above_range,
        "total_pixels": int(raw_albedo.size),
    }

    return clipped_albedo, validation_report


ALBEDO_METHOD_METADATA = {
    "method": "Liang (2001) narrowband-to-broadband conversion, renormalized to blue+red+NIR only",
    "is_modeled": True,
    "is_measured": False,
    "excluded_bands": ["SWIR1 (Sentinel-2 B11)", "SWIR2 (Sentinel-2 B12)"],
    "exclusion_reason": "Both SWIR bands are natively 20m, disqualified under this project's 10m-or-finer resolution policy.",
    "renormalization_divisor": RENORMALIZATION_DIVISOR,
    "coefficients_used": {
        "blue": LIANG_2001_BLUE_COEFFICIENT,
        "red": LIANG_2001_RED_COEFFICIENT,
        "nir": LIANG_2001_NIR_COEFFICIENT,
    },
    "caveat": "Broadband albedo estimated from a partial (3-band) empirical formula; expect systematic divergence from true albedo over high-SWIR-contrast surfaces.",
}
