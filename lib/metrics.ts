export type MetricKind = "sequential" | "diverging";

export interface MetricDefinition {
  id: string;
  label: string;
  shortLabel: string;
  description: string;
  minLabel: string;
  maxLabel: string;
  stops: string[];
  kind: MetricKind;
}

// IDs mirror backend/app/feature_stack.py FEATURE_NAMES.
export const METRICS: MetricDefinition[] = [
  { id: "heat_vulnerability", label: "Heat vulnerability", shortLabel: "Vulnerability", description: "Composite modeled heat vulnerability score", minLabel: "Lower", maxLabel: "Higher", stops: ["#dcebdc", "#e6c77b", "#b45f42"], kind: "sequential" },
  { id: "ndvi_mean", label: "Vegetation cover", shortLabel: "Vegetation", description: "Average vegetation index", minLabel: "Sparse", maxLabel: "Dense", stops: ["#f0e0bc", "#a9c98b", "#39785b"], kind: "sequential" },
  { id: "ndwi_mean", label: "Moisture", shortLabel: "Moisture", description: "Average water or moisture index", minLabel: "Dry", maxLabel: "Moist", stops: ["#f2e3c3", "#a7c6cf", "#3f7181"], kind: "sequential" },
  { id: "albedo_mean", label: "Surface reflectivity", shortLabel: "Reflectivity", description: "Average surface albedo", minLabel: "Dark", maxLabel: "Reflective", stops: ["#6b4d42", "#d7bb83", "#f3eee0"], kind: "sequential" },
  { id: "built_up_pct_mean", label: "Built-up land", shortLabel: "Built-up", description: "Share of land classified as built-up", minLabel: "Open", maxLabel: "Dense", stops: ["#e4e9e2", "#c6a987", "#6b4d42"], kind: "sequential" },
  { id: "building_density_per_km2", label: "Building density", shortLabel: "Buildings", description: "Estimated buildings per square kilometre", minLabel: "Lower", maxLabel: "Higher", stops: ["#e4e9e2", "#c6a987", "#6b4d42"], kind: "sequential" },
  { id: "road_density_km_per_km2", label: "Road density", shortLabel: "Roads", description: "Estimated road length per square kilometre", minLabel: "Lower", maxLabel: "Higher", stops: ["#e4e9e2", "#d9ad77", "#9b4f3d"], kind: "sequential" },
  { id: "built_up_pct_trend", label: "Built-up trend", shortLabel: "Built-up trend", description: "Change in built-up land over time", minLabel: "Declining", maxLabel: "Increasing", stops: ["#39785b", "#e6c77b", "#b45f42"], kind: "diverging" },
];

export function getMetricById(id: string): MetricDefinition {
  return METRICS.find((item) => item.id === id) ?? METRICS[0];
}

export const INTERVENTIONS = [
  { id: "add_tree_cover", label: "Add tree cover", description: "Increase vegetation across the selected region." },
  { id: "cool_roof", label: "Cool roofs", description: "Increase roof reflectivity on built-up pixels." },
  { id: "add_green_space", label: "Add green space", description: "Convert part of built-up land to planted space." },
  { id: "green_roof", label: "Green roofs", description: "Add vegetation and reflectivity to existing roofs." },
  { id: "cool_pavement", label: "Cool pavement", description: "Increase reflectivity where road density is high." },
  { id: "urban_water_feature", label: "Water feature", description: "Add moisture and reduce built-up land." },
  { id: "reduce_building_density", label: "Reduce building density", description: "Model a long-term lower-density scenario." },
];
