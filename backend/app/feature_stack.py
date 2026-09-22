import os
import glob
import time
import numpy as np
import rasterio
import rasterio.features
from rasterio.enums import MergeAlg
import geopandas as gpd
from scipy.ndimage import uniform_filter

from app.albedo import get_albedo

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(ROOT, "data", "validated")
CACHE_DIR = os.path.join(ROOT, "backend", "cache")
CACHE_PATH = os.path.join(CACHE_DIR, "feature_stack_10m.npz")

BANDS_DIR = os.path.join(DATA_DIR, "sentinel2_10m_monthly_least_cloudy")
NDVI_DIR = os.path.join(DATA_DIR, "ndvi_10m_monthly")
NDWI_DIR = os.path.join(DATA_DIR, "water_ndwi_10m_monthly")
LULC_DIR = os.path.join(DATA_DIR, "lulc_10m_monthly")
BUILDINGS_PATH = os.path.join(DATA_DIR, "building_footprints", "building_footprints.geojson")
ROADS_PATH = os.path.join(DATA_DIR, "road_network", "road_network.geojson")

BUILT_UP = 0
VEGETATION = 1
WATER = 2
NO_DATA = 255

WINDOW = 9
PIXEL = 10.0

FEATURE_NAMES = [
    "ndvi_mean", "ndvi_min", "ndvi_std",
    "ndwi_mean", "ndwi_std",
    "albedo_mean", "albedo_min", "albedo_std",
    "built_up_pct_mean", "vegetation_pct_mean", "water_pct_mean",
    "built_up_pct_trend",
    "building_density_per_km2",
    "road_density_km_per_km2",
]


class Stats:
    def __init__(self, shape, keep_min):
        self.total = np.zeros(shape, dtype=np.float64)
        self.squares = np.zeros(shape, dtype=np.float64)
        self.count = np.zeros(shape, dtype=np.int32)
        self.smallest = None
        if keep_min:
            self.smallest = np.full(shape, np.inf, dtype=np.float64)

    def add(self, values, valid):
        v = values[valid]
        self.total[valid] += v
        self.squares[valid] += v ** 2
        if self.smallest is not None:
            self.smallest[valid] = np.minimum(self.smallest[valid], v)
        self.count[valid] += 1

    def mean(self):
        return np.where(self.count > 0, self.total / np.maximum(self.count, 1), np.nan)

    def std(self, mean):
        variance = np.where(self.count > 0, self.squares / np.maximum(self.count, 1) - mean ** 2, np.nan)
        return np.sqrt(np.maximum(variance, 0))

    def min(self):
        return np.where(self.count > 0, self.smallest, np.nan)


def find_months():
    months = []
    for ndvi_file in sorted(glob.glob(os.path.join(NDVI_DIR, "*.tif"))):
        name = os.path.basename(ndvi_file).replace("ndvi_10m_", "").replace(".tif", "")
        bands = os.path.join(BANDS_DIR, name, "sentinel2_10m_least_cloudy_" + name + ".tif")
        ndwi = os.path.join(NDWI_DIR, "ndwi_10m_" + name + ".tif")
        lulc = os.path.join(LULC_DIR, name, "lulc_10m_" + name + ".tif")
        if os.path.exists(bands) and os.path.exists(ndwi) and os.path.exists(lulc):
            months.append({"name": name, "bands": bands, "ndvi": ndvi_file, "ndwi": ndwi, "lulc": lulc})
    return sorted(months, key=lambda m: m["name"])


def get_grid():
    first = sorted(glob.glob(os.path.join(NDVI_DIR, "*.tif")))[0]
    with rasterio.open(first) as f:
        return f.transform, (f.height, f.width), f.crs


def building_density(transform, shape, crs):
    print("Building density...")
    buildings = gpd.read_file(BUILDINGS_PATH)
    buildings = buildings[buildings.geometry.is_valid]
    centers = buildings.to_crs(crs).geometry.centroid

    points = rasterio.features.rasterize(
        [(c, 1) for c in centers],
        out_shape=shape, transform=transform, fill=0, dtype="float32", merge_alg=MergeAlg.add,
    )
    count = uniform_filter(points, size=WINDOW, mode="constant") * (WINDOW ** 2)
    area_km2 = ((WINDOW * PIXEL) ** 2) / 1e6
    density = count / area_km2

    print("Buildings per km2, min:", round(float(density.min()), 1), "mean:", round(float(density.mean()), 1), "max:", round(float(density.max()), 1))
    return density.astype(np.float32)


def road_density(transform, shape, crs):
    print("Road density...")
    roads = gpd.read_file(ROADS_PATH)
    roads = roads[roads.geometry.is_valid]
    lines = roads.to_crs(crs).geometry

    touched = rasterio.features.rasterize(
        [(line, 1) for line in lines],
        out_shape=shape, transform=transform, fill=0, dtype="uint8", all_touched=True,
    )
    fraction = uniform_filter(touched.astype(np.float32), size=WINDOW, mode="constant")

    pixels = fraction * (WINDOW ** 2)
    length_km = pixels * (PIXEL / 1000.0)
    area_km2 = (WINDOW * PIXEL / 1000.0) ** 2
    density = length_km / area_km2

    print("Road km per km2, min:", round(float(density.min()), 2), "mean:", round(float(density.mean()), 2), "max:", round(float(density.max()), 2))
    return density.astype(np.float32)


def percent(count, total):
    return np.where(total > 0, count / np.maximum(total, 1) * 100.0, np.nan)


def build_feature_stack(rebuild=False):
    if os.path.exists(CACHE_PATH) and not rebuild:
        print("Loading saved features from", CACHE_PATH)
        saved = np.load(CACHE_PATH, allow_pickle=True)
        features = {}
        for f in FEATURE_NAMES:
            features[f] = saved[f]
        return features, dict(saved["meta_shape"])

    print("Building the features from all months, this takes a while...")
    transform, shape, crs = get_grid()
    height, width = shape
    months = find_months()
    print("Grid:", width, "x", height, "pixels, months found:", len(months))

    ndvi = Stats(shape, True)
    ndwi = Stats(shape, False)
    albedo = Stats(shape, True)

    built_up_count = np.zeros(shape, dtype=np.int32)
    vegetation_count = np.zeros(shape, dtype=np.int32)
    water_count = np.zeros(shape, dtype=np.int32)
    lulc_count = np.zeros(shape, dtype=np.int32)

    sum_t = np.zeros(shape, dtype=np.float64)
    sum_y = np.zeros(shape, dtype=np.float64)
    sum_ty = np.zeros(shape, dtype=np.float64)
    sum_tt = np.zeros(shape, dtype=np.float64)
    trend_n = np.zeros(shape, dtype=np.int32)

    below = 0
    above = 0
    start = time.time()

    for m in range(len(months)):
        month = months[m]
        with rasterio.open(month["ndvi"]) as f:
            ndvi_now = f.read(1).astype(np.float64)
        with rasterio.open(month["ndwi"]) as f:
            ndwi_now = f.read(1).astype(np.float64)
        with rasterio.open(month["lulc"]) as f:
            lulc = f.read(1)
        with rasterio.open(month["bands"]) as f:
            bands = f.read()

        ndvi.add(ndvi_now, ~np.isnan(ndvi_now))
        ndwi.add(ndwi_now, ~np.isnan(ndwi_now))

        albedo_now, low, high = get_albedo(bands[0], bands[2], bands[3])
        below += low
        above += high
        albedo.add(albedo_now, np.any(bands != 0, axis=0))

        valid = lulc != NO_DATA
        is_built_up = lulc == BUILT_UP
        lulc_count[valid] += 1
        built_up_count[valid & is_built_up] += 1
        vegetation_count[valid & (lulc == VEGETATION)] += 1
        water_count[valid & (lulc == WATER)] += 1

        y = np.where(valid, is_built_up.astype(np.float64), 0.0)
        t = float(m)
        sum_t[valid] += t
        sum_y[valid] += y[valid]
        sum_ty[valid] += t * y[valid]
        sum_tt[valid] += t * t
        trend_n[valid] += 1

        print("Month", m + 1, "of", len(months), month["name"], round(time.time() - start, 1), "seconds")

    print("Albedo pixels clipped below 0:", below, "above 1:", above)

    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi_mean = ndvi.mean()
        ndwi_mean = ndwi.mean()
        albedo_mean = albedo.mean()

        bottom = trend_n * sum_tt - sum_t ** 2
        trend = np.where(
            (trend_n >= 3) & (np.abs(bottom) > 1e-9),
            (trend_n * sum_ty - sum_t * sum_y) / np.where(bottom == 0, np.nan, bottom),
            np.nan,
        )

        all_features = {
            "ndvi_mean": ndvi_mean, "ndvi_min": ndvi.min(), "ndvi_std": ndvi.std(ndvi_mean),
            "ndwi_mean": ndwi_mean, "ndwi_std": ndwi.std(ndwi_mean),
            "albedo_mean": albedo_mean, "albedo_min": albedo.min(), "albedo_std": albedo.std(albedo_mean),
            "built_up_pct_mean": percent(built_up_count, lulc_count),
            "vegetation_pct_mean": percent(vegetation_count, lulc_count),
            "water_pct_mean": percent(water_count, lulc_count),
            "built_up_pct_trend": trend,
        }

    features = {}
    for name in all_features:
        features[name] = all_features[name].astype(np.float32)
        print(name, "from", round(float(np.nanmin(features[name])), 3), "to", round(float(np.nanmax(features[name])), 3))

    features["building_density_per_km2"] = building_density(transform, shape, crs)
    features["road_density_km_per_km2"] = road_density(transform, shape, crs)

    meta = {"height": height, "width": width, "transform": list(transform)[:6], "crs": str(crs), "n_months": len(months)}
    os.makedirs(CACHE_DIR, exist_ok=True)
    np.savez_compressed(CACHE_PATH, meta_shape=np.array(list(meta.items()), dtype=object), **features)
    print("Saved the features to", CACHE_PATH)

    return features, meta
