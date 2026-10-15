export type Coordinate = [number, number];

export interface RegionFeature {
  type: "Feature";
  properties: Record<string, unknown>;
  geometry: {
    type: "Polygon";
    coordinates: Coordinate[][];
  };
}

export interface MetricStats {
  mean: number;
  min: number;
  max: number;
  std: number;
}

export interface ShapContribution {
  feature: string;
  mean_shap_value: number;
}

export interface RegionAnalyzeResponse {
  region_id: string;
  pixel_count: number;
  aggregated: boolean;
  aggregation_cell_size_meters: number | null;
  metrics_summary: Record<string, MetricStats>;
  heat_vulnerability_summary: MetricStats;
  grid_geojson: GeoJSON.FeatureCollection;
  shap_summary: ShapContribution[];
  plain_language_summary: string;
  caveats: string;
}

export interface MetricLayerResponse {
  region_id: string;
  metric_name: string;
  grid_geojson: GeoJSON.FeatureCollection;
  caveats: string;
}

export interface RankedLocation {
  lon: number;
  lat: number;
  before_score: number;
  after_score: number;
  improvement: number;
}

export interface InterventionResult {
  intervention_type: string;
  assumptions: {
    description: string;
    assumptions: Record<string, number>;
    rationale: string;
  };
  region_pixel_count: number;
  mean_improvement: number;
  ranked_locations: RankedLocation[];
  grid_geojson: GeoJSON.FeatureCollection;
  aggregated: boolean;
  aggregation_cell_size_meters: number | null;
}

export interface SimulationSelection {
  intervention_type: string;
  view: "before" | "after";
}

export interface SimulateResponse {
  region_id: string;
  results: InterventionResult[];
  caveats: string;
}

export interface HealthResponse {
  status: string;
  model_version: string;
  model_r_squared: number;
  model_mae: number;
  feature_stack_built_at: string | null;
  model_trained_at: string | null;
  n_training_pixels: number;
  caveats: string;
}
