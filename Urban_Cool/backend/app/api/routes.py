import os
import time
import numpy as np
import pandas as pd
import rasterio.transform
from fastapi import APIRouter, HTTPException

from app.feature_stack import FEATURE_NAMES, CACHE_PATH
from app.model import MODEL_PATH
from app.region_cache import get_region, find_region
from app.simulator import simulate as run_simulation, INTERVENTIONS, CAVEAT
from app.grid_utils import make_grid
from app.schemas import (
    RegionAnalyzeRequest, RegionAnalyzeResponse, MetricStats, ShapContribution,
    MetricLayerResponse, SimulateRequest, SimulateResponse, InterventionResult, RankedLocation,
    HealthResponse,
)
from app.state import get_state

router = APIRouter(prefix="/api/v1")

SHAP_SAMPLES = 500

PLAIN_NAMES = {
    "ndvi_mean": "low vegetation cover",
    "ndwi_mean": "little nearby water/moisture",
    "albedo_mean": "low surface reflectivity (dark, heat-absorbing surfaces)",
    "built_up_pct_mean": "a high proportion of built-up land",
    "vegetation_pct_mean": "limited vegetated land",
    "water_pct_mean": "limited water bodies",
    "built_up_pct_trend": "a rising trend in built-up land over time",
    "building_density_per_km2": "high building density",
    "road_density_km_per_km2": "high road density",
    "ndvi_min": "patches of very low vegetation",
    "ndvi_std": "inconsistent vegetation cover",
    "ndwi_std": "inconsistent moisture presence",
    "albedo_min": "patches of very dark surfaces",
    "albedo_std": "inconsistent surface reflectivity",
}


def get_stats(values):
    values = values[~np.isnan(values)]
    if len(values) == 0:
        return MetricStats(mean=0.0, min=0.0, max=0.0, std=0.0)
    return MetricStats(mean=float(np.mean(values)), min=float(np.min(values)), max=float(np.max(values)), std=float(np.std(values)))


def read_pixels(features, rows, cols):
    data = {}
    for f in FEATURE_NAMES:
        data[f] = features[f][rows, cols]
    df = pd.DataFrame(data)
    valid = df[["ndvi_mean", "built_up_pct_mean", "albedo_mean"]].notna().all(axis=1).to_numpy()
    return df[valid].reset_index(drop=True), rows[valid], cols[valid]


def fill_gaps(df):
    df = df.copy()
    for f in FEATURE_NAMES:
        df[f] = df[f].fillna(df[f].median())
    return df


def write_summary(shap_list):
    top = shap_list[:2]
    names = []
    for s in top:
        names.append(PLAIN_NAMES.get(s.feature, s.feature))

    if len(names) == 2:
        return names[0].capitalize() + " and " + names[1] + " are the main drivers of the heat vulnerability score in this area."
    if len(names) == 1:
        return names[0].capitalize() + " is the main driver of the heat vulnerability score in this area."
    return "No dominant driver identified for this area."


@router.post("/region/analyze", response_model=RegionAnalyzeResponse)
def analyze_region(request: RegionAnalyzeRequest):
    state = get_state()
    meta = state.meta

    region_id, region = get_region(request.region, meta)
    if len(region["rows"]) == 0:
        raise HTTPException(status_code=400, detail="Drawn region contains no pixels inside the study area AOI.")

    df, rows, cols = read_pixels(state.features, region["rows"], region["cols"])
    if len(df) == 0:
        raise HTTPException(status_code=400, detail="Drawn region has no valid (non-nodata) pixels.")

    filled = fill_gaps(df)
    scores = state.model.predict(filled[FEATURE_NAMES], thread_count=-1)

    sample = filled[FEATURE_NAMES]
    if len(sample) > SHAP_SAMPLES:
        sample = sample.sample(n=SHAP_SAMPLES, random_state=0)
    shap_values = state.explainer.shap_values(sample)
    order = np.argsort(-np.abs(shap_values).mean(axis=0))
    shap_list = []
    for i in order:
        shap_list.append(ShapContribution(feature=FEATURE_NAMES[i], mean_shap_value=float(shap_values[:, i].mean())))

    transform = rasterio.transform.Affine(*meta["transform"])
    grid, aggregated, cell_size = make_grid(rows, cols, transform, {"heat_vulnerability_score": scores})

    stats = {}
    for f in FEATURE_NAMES:
        stats[f] = get_stats(df[f].values)

    return RegionAnalyzeResponse(
        region_id=region_id,
        pixel_count=len(df),
        aggregated=aggregated,
        aggregation_cell_size_meters=cell_size if aggregated else None,
        metrics_summary=stats,
        heat_vulnerability_summary=get_stats(scores),
        grid_geojson=grid,
        shap_summary=shap_list,
        plain_language_summary=write_summary(shap_list),
        caveats=CAVEAT,
    )


@router.get("/region/{region_id}/metrics/{metric_name}", response_model=MetricLayerResponse)
def get_metric_layer(region_id: str, metric_name: str):
    state = get_state()
    meta = state.meta

    allowed = FEATURE_NAMES + ["heat_vulnerability"]
    if metric_name not in allowed:
        raise HTTPException(status_code=404, detail="Unknown metric '" + metric_name + "'. Valid options: " + str(allowed))

    try:
        region = find_region(region_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    rows = region["rows"]
    cols = region["cols"]

    if metric_name == "heat_vulnerability":
        df, rows, cols = read_pixels(state.features, rows, cols)
        values = state.model.predict(fill_gaps(df)[FEATURE_NAMES], thread_count=-1)
    else:
        values = state.features[metric_name][rows, cols]
        has_value = ~np.isnan(values)
        values = values[has_value]
        rows = rows[has_value]
        cols = cols[has_value]

    transform = rasterio.transform.Affine(*meta["transform"])
    grid, aggregated, cell_size = make_grid(rows, cols, transform, {metric_name: values})

    return MetricLayerResponse(region_id=region_id, metric_name=metric_name, grid_geojson=grid, caveats=CAVEAT)


@router.post("/region/{region_id}/simulate", response_model=SimulateResponse)
def simulate(region_id: str, request: SimulateRequest):
    state = get_state()
    meta = state.meta

    try:
        region = find_region(region_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    unknown = set(request.intervention_types) - set(INTERVENTIONS.keys())
    if unknown:
        raise HTTPException(status_code=400, detail="Unknown intervention type(s): " + str(unknown) + ". Valid: " + str(sorted(INTERVENTIONS.keys())))

    transform = rasterio.transform.Affine(*meta["transform"])
    results = []

    for name in request.intervention_types:
        r = run_simulation(state.features, meta, state.model, region["rows"], region["cols"], name, request.top_n)

        grid = {"type": "FeatureCollection", "features": []}
        aggregated = False
        cell_size = None
        if r["count"] > 0:
            grid, aggregated, cell_size = make_grid(r["rows"], r["cols"], transform, {"before_score": r["before"], "after_score": r["after"]})

        top = []
        for t in r["top"]:
            top.append(RankedLocation(**t))

        results.append(InterventionResult(
            intervention_type=r["name"],
            assumptions=r["assumptions"],
            region_pixel_count=r["count"],
            mean_improvement=r["mean"],
            ranked_locations=top,
            grid_geojson=grid,
            aggregated=aggregated,
            aggregation_cell_size_meters=cell_size if aggregated else None,
        ))

    return SimulateResponse(region_id=region_id, results=results, caveats=CAVEAT)


@router.get("/health", response_model=HealthResponse)
def health():
    info = get_state().model_info

    features_time = None
    if os.path.exists(CACHE_PATH):
        features_time = time.ctime(os.path.getmtime(CACHE_PATH))

    model_time = None
    if os.path.exists(MODEL_PATH):
        model_time = time.ctime(os.path.getmtime(MODEL_PATH))

    return HealthResponse(
        status="ok",
        model_version="native10m-v1",
        model_r_squared=float(info["r_squared"]),
        model_mae=float(info["mae"]),
        feature_stack_built_at=features_time,
        model_trained_at=model_time,
        n_training_pixels=int(info["n_train"]) + int(info["n_test"]),
        caveats=CAVEAT,
    )
