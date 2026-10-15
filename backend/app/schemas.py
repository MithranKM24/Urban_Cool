from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RegionAnalyzeRequest(BaseModel):
    region: Dict[str, Any]


class MetricStats(BaseModel):
    mean: float
    min: float
    max: float
    std: float


class ShapContribution(BaseModel):
    feature: str
    mean_shap_value: float


class RegionAnalyzeResponse(BaseModel):
    region_id: str
    pixel_count: int
    aggregated: bool = False
    aggregation_cell_size_meters: Optional[float] = None
    metrics_summary: Dict[str, MetricStats]
    heat_vulnerability_summary: MetricStats
    grid_geojson: Dict[str, Any]
    shap_summary: List[ShapContribution]
    plain_language_summary: str
    caveats: str


class MetricLayerResponse(BaseModel):
    region_id: str
    metric_name: str
    grid_geojson: Dict[str, Any]
    caveats: str


class SimulateRequest(BaseModel):
    intervention_types: List[str] = Field(min_length=1)
    top_n: int = Field(default=10, ge=1, le=100)


class RankedLocation(BaseModel):
    lon: float
    lat: float
    before_score: float
    after_score: float
    improvement: float


class InterventionResult(BaseModel):
    intervention_type: str
    assumptions: Dict[str, Any]
    region_pixel_count: int
    mean_improvement: float
    ranked_locations: List[RankedLocation]
    grid_geojson: Dict[str, Any]
    aggregated: bool = False
    aggregation_cell_size_meters: Optional[float] = None


class SimulateResponse(BaseModel):
    region_id: str
    results: List[InterventionResult]
    caveats: str


class HealthResponse(BaseModel):
    status: str
    model_version: str = "native10m-v1"
    model_r_squared: Optional[float] = None
    model_mae: Optional[float] = None
    feature_stack_built_at: Optional[str] = None
    model_trained_at: Optional[str] = None
    n_training_pixels: Optional[int] = None
    caveats: str
