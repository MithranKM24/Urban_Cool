import type {
  HealthResponse,
  MetricLayerResponse,
  RegionAnalyzeResponse,
  RegionFeature,
  SimulateResponse,
} from "@/lib/api-types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new Error(`Backend unavailable at ${API_BASE_URL}`);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const apiClient = {
  health: () => request<HealthResponse>("/api/v1/health"),
  analyzeRegion: (region: RegionFeature) =>
    request<RegionAnalyzeResponse>("/api/v1/region/analyze", {
      method: "POST",
      body: JSON.stringify({ region }),
    }),
  metricLayer: (regionId: string, metricName: string) =>
    request<MetricLayerResponse>(`/api/v1/region/${regionId}/metrics/${metricName}`),
  simulate: (regionId: string, interventionTypes: string[], topN = 10) =>
    request<SimulateResponse>(`/api/v1/region/${regionId}/simulate`, {
      method: "POST",
      body: JSON.stringify({ intervention_types: interventionTypes, top_n: topN }),
    }),
};

export type { RegionFeature, RegionAnalyzeResponse } from "@/lib/api-types";
export type { ShapContribution } from "@/lib/api-types";
