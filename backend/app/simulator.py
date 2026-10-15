import numpy as np
import pandas as pd
import rasterio.transform

from app.feature_stack import FEATURE_NAMES
from app.grid_utils import pixel_to_lonlat

TREE_NDVI = 0.15

COOL_ROOF_ALBEDO = 0.20

GREEN_SPACE_NDVI = 0.25
GREEN_SPACE_NDWI = 0.05
GREEN_SPACE_BUILT_UP = 20.0

GREEN_ROOF_NDVI = 0.08
GREEN_ROOF_ALBEDO = 0.05

COOL_PAVEMENT_ALBEDO = 0.15
COOL_PAVEMENT_ROAD_DENSITY = 5.0

WATER_NDWI = 0.20
WATER_NDVI = 0.05
WATER_BUILT_UP = 12.0

DENSITY_BUILDINGS = 25.0
DENSITY_BUILT_UP = 10.0
DENSITY_NDVI = 0.10

BUILT_UP_LIMIT = 10.0

INTERVENTIONS = {
    "add_tree_cover": {
        "description": "Plant trees across the selected area.",
        "assumptions": {"TREE_COVER_NDVI_BOOST": TREE_NDVI},
        "rationale": "Tree canopy raises NDVI by about this much in tropical cities. Our assumption, not measured here.",
    },
    "cool_roof": {
        "description": "Put reflective roofing on the built-up area.",
        "assumptions": {"COOL_ROOF_ALBEDO_BOOST": COOL_ROOF_ALBEDO},
        "rationale": "Cool roof coatings raise albedo by about 0.15 to 0.25. Only used where the pixel is built-up.",
    },
    "add_green_space": {
        "description": "Turn built-up area into a park.",
        "assumptions": {
            "GREEN_SPACE_NDVI_BOOST": GREEN_SPACE_NDVI,
            "GREEN_SPACE_NDWI_BOOST": GREEN_SPACE_NDWI,
            "GREEN_SPACE_BUILT_UP_REDUCTION_PCT": GREEN_SPACE_BUILT_UP,
        },
        "rationale": "A park adds plants but also takes the place of some buildings, so built-up % goes down too.",
    },
    "green_roof": {
        "description": "Put plants on the roofs of existing buildings.",
        "assumptions": {"GREEN_ROOF_NDVI_BOOST": GREEN_ROOF_NDVI, "GREEN_ROOF_ALBEDO_BOOST": GREEN_ROOF_ALBEDO},
        "rationale": "Only the roof gets covered so the gain is smaller than trees on the ground or a cool roof.",
    },
    "cool_pavement": {
        "description": "Put a reflective coating on roads.",
        "assumptions": {
            "COOL_PAVEMENT_ALBEDO_BOOST": COOL_PAVEMENT_ALBEDO,
            "COOL_PAVEMENT_ROAD_DENSITY_THRESHOLD_KM_PER_KM2": COOL_PAVEMENT_ROAD_DENSITY,
        },
        "rationale": "Raises albedo of road surfaces, only where road density is high enough. Cool roof is for buildings, this one is for roads.",
    },
    "urban_water_feature": {
        "description": "Add a pond or water feature with plants around it.",
        "assumptions": {
            "WATER_FEATURE_NDWI_BOOST": WATER_NDWI,
            "WATER_FEATURE_NDVI_BOOST": WATER_NDVI,
            "WATER_FEATURE_BUILT_UP_REDUCTION_PCT": WATER_BUILT_UP,
        },
        "rationale": "Water cools the air around it. More moisture, a bit more plants, and some built-up land is used up by the pond.",
    },
    "reduce_building_density": {
        "description": "Rebuild the area with fewer buildings and more open space.",
        "assumptions": {
            "DENSITY_REDUCTION_BUILDING_DENSITY_PCT": DENSITY_BUILDINGS,
            "DENSITY_REDUCTION_BUILT_UP_REDUCTION_PCT": DENSITY_BUILT_UP,
            "DENSITY_REDUCTION_NDVI_BOOST": DENSITY_NDVI,
        },
        "rationale": "A long term planning idea, not a retrofit, so this one is the most uncertain of all.",
    },
}

CAVEAT = (
    "This score is derived from land cover, vegetation, and urban density only "
    "(native 10m resolution); it has not been validated against measured land surface temperature. "
    "Intervention effect sizes are documented planning assumptions, not measured outcomes for this corridor."
)


def apply_intervention(df, name):
    df = df.copy()

    if name == "add_tree_cover":
        df["ndvi_mean"] = np.clip(df["ndvi_mean"] + TREE_NDVI, -1.0, 1.0)

    elif name == "cool_roof":
        built = df["built_up_pct_mean"] > BUILT_UP_LIMIT
        df.loc[built, "albedo_mean"] = np.clip(df.loc[built, "albedo_mean"] + COOL_ROOF_ALBEDO, 0.0, 1.0)

    elif name == "add_green_space":
        df["ndvi_mean"] = np.clip(df["ndvi_mean"] + GREEN_SPACE_NDVI, -1.0, 1.0)
        df["ndwi_mean"] = np.clip(df["ndwi_mean"] + GREEN_SPACE_NDWI, -1.0, 1.0)
        df["built_up_pct_mean"] = np.clip(df["built_up_pct_mean"] - GREEN_SPACE_BUILT_UP, 0.0, 100.0)

    elif name == "green_roof":
        built = df["built_up_pct_mean"] > BUILT_UP_LIMIT
        df.loc[built, "ndvi_mean"] = np.clip(df.loc[built, "ndvi_mean"] + GREEN_ROOF_NDVI, -1.0, 1.0)
        df.loc[built, "albedo_mean"] = np.clip(df.loc[built, "albedo_mean"] + GREEN_ROOF_ALBEDO, 0.0, 1.0)

    elif name == "cool_pavement":
        roads = df["road_density_km_per_km2"] > COOL_PAVEMENT_ROAD_DENSITY
        df.loc[roads, "albedo_mean"] = np.clip(df.loc[roads, "albedo_mean"] + COOL_PAVEMENT_ALBEDO, 0.0, 1.0)

    elif name == "urban_water_feature":
        df["ndwi_mean"] = np.clip(df["ndwi_mean"] + WATER_NDWI, -1.0, 1.0)
        df["ndvi_mean"] = np.clip(df["ndvi_mean"] + WATER_NDVI, -1.0, 1.0)
        df["built_up_pct_mean"] = np.clip(df["built_up_pct_mean"] - WATER_BUILT_UP, 0.0, 100.0)

    elif name == "reduce_building_density":
        df["building_density_per_km2"] = np.clip(df["building_density_per_km2"] * (1.0 - DENSITY_BUILDINGS / 100.0), 0.0, None)
        df["built_up_pct_mean"] = np.clip(df["built_up_pct_mean"] - DENSITY_BUILT_UP, 0.0, 100.0)
        df["ndvi_mean"] = np.clip(df["ndvi_mean"] + DENSITY_NDVI, -1.0, 1.0)

    else:
        raise ValueError("Unknown intervention: " + name)

    return df


def simulate(features, meta, model, rows, cols, name, top_n=10):
    transform = rasterio.transform.Affine(*meta["transform"])

    data = {}
    for f in FEATURE_NAMES:
        data[f] = features[f][rows, cols]
    df = pd.DataFrame(data)

    valid = df[["ndvi_mean", "built_up_pct_mean", "albedo_mean"]].notna().all(axis=1).to_numpy()
    for f in FEATURE_NAMES:
        df[f] = df[f].fillna(df[f].median())

    before = model.predict(df[FEATURE_NAMES], thread_count=-1)
    after = model.predict(apply_intervention(df, name)[FEATURE_NAMES], thread_count=-1)

    rows = rows[valid]
    cols = cols[valid]
    before = before[valid]
    after = after[valid]
    improvement = before - after

    count = len(rows)
    mean = 0.0
    if count > 0:
        mean = float(np.mean(improvement))

    best = np.argsort(-improvement, kind="stable")[:top_n]
    lon, lat = pixel_to_lonlat(transform, rows[best], cols[best])
    top = []
    for k in range(len(best)):
        i = best[k]
        top.append({
            "lon": float(lon[k]),
            "lat": float(lat[k]),
            "before_score": float(before[i]),
            "after_score": float(after[i]),
            "improvement": float(improvement[i]),
        })

    return {
        "name": name,
        "assumptions": INTERVENTIONS[name],
        "count": count,
        "mean": mean,
        "top": top,
        "rows": rows,
        "cols": cols,
        "before": before,
        "after": after,
    }
