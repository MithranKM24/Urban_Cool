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

export const METRICS: MetricDefinition[] = [
  {
    id: "heat_vulnerability",
    label: "Heat vulnerability",
    shortLabel: "Vulnerability",
    description: "Composite exposure, sensitivity, and adaptive-capacity score",
    minLabel: "Lower risk",
    maxLabel: "Higher risk",
    stops: ["#dcebdc", "#e6c77b", "#b45f42"],
    kind: "sequential",
  },
  {
    id: "land_surface_temperature",
    label: "Land surface temperature",
    shortLabel: "Surface temperature",
    description: "Estimated daytime surface temperature",
    minLabel: "29°C",
    maxLabel: "42°C",
    stops: ["#f5e7bf", "#e09a62", "#a73e36"],
    kind: "sequential",
  },
  {
    id: "tree_cover",
    label: "Tree cover",
    shortLabel: "Tree cover",
    description: "Share of land covered by tree canopy",
    minLabel: "Sparse",
    maxLabel: "Dense",
    stops: ["#f0e0bc", "#a9c98b", "#39785b"],
    kind: "sequential",
  },
  {
    id: "built_up_density",
    label: "Built-up density",
    shortLabel: "Built-up density",
    description: "Intensity of impervious built surfaces",
    minLabel: "Open",
    maxLabel: "Dense",
    stops: ["#e4e9e2", "#c6a987", "#6b4d42"],
    kind: "sequential",
  },
  {
    id: "elderly_population",
    label: "Elderly population",
    shortLabel: "Elderly population",
    description: "Residents aged 60 and above",
    minLabel: "Lower share",
    maxLabel: "Higher share",
    stops: ["#e9edf1", "#a6bfd1", "#4c6f85"],
    kind: "sequential",
  },
];

export function getMetricById(id: string): MetricDefinition {
  const metric = METRICS.find((item) => item.id === id);
  if (!metric) throw new Error(`Unknown metric: ${id}`);
  return metric;
}
