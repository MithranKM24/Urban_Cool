"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Loader2, MapPin, RotateCcw } from "lucide-react";
import ExplanationPanel from "@/components/ExplanationPanel";
import InterventionPanel from "@/components/InterventionPanel";
import MapView from "@/components/ui/MapView";
import MetricTogglePanel from "@/components/ui/MetricTogglePanel";
import { apiClient } from "@/lib/api-client";
import type { HealthResponse, RegionAnalyzeResponse, RegionFeature, SimulateResponse } from "@/lib/api-types";
import { getMetricById } from "@/lib/metrics";

export default function HomePage() {
  const [activeMetricId, setActiveMetricId] = useState("heat_vulnerability");
  const [selectedRegion, setSelectedRegion] = useState<RegionFeature | null>(null);
  const [analysis, setAnalysis] = useState<RegionAnalyzeResponse | null>(null);
  const [metricGrid, setMetricGrid] = useState<GeoJSON.FeatureCollection>();
  const [simulation, setSimulation] = useState<SimulateResponse | null>(null);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [scenarioView, setScenarioView] = useState<"before" | "after">("after");
  const [busy, setBusy] = useState<"analyze" | "metric" | "simulate" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const metric = useMemo(() => getMetricById(activeMetricId), [activeMetricId]);

  useEffect(() => { apiClient.health().then(setHealth).catch(() => setHealth(null)); }, []);

  const handleRegionSelected = useCallback((region: RegionFeature) => {
    setSelectedRegion(region);
    setAnalysis(null);
    setMetricGrid(undefined);
    setSimulation(null);
    setSelectedScenarioId(null);
    setError(null);
  }, []);

  async function analyze() {
    if (!selectedRegion) return;
    setBusy("analyze"); setError(null);
    try {
      const result = await apiClient.analyzeRegion(selectedRegion);
      setAnalysis(result); setMetricGrid(result.grid_geojson);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Could not analyze this area."); }
    finally { setBusy(null); }
  }

  async function selectMetric(id: string) {
    setActiveMetricId(id); setError(null);
    if (!analysis) return;
    if (id === "heat_vulnerability") { setMetricGrid(analysis.grid_geojson); return; }
    setBusy("metric");
    try { setMetricGrid((await apiClient.metricLayer(analysis.region_id, id)).grid_geojson); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Could not load this layer."); }
    finally { setBusy(null); }
  }

  async function runScenarios(ids: string[]) {
    if (!analysis) return;
    setBusy("simulate"); setError(null);
    try { const response = await apiClient.simulate(analysis.region_id, ids); setSimulation(response); setSelectedScenarioId(response.results[0]?.intervention_type ?? null); setScenarioView("after"); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Could not run scenarios."); }
    finally { setBusy(null); }
  }

  const stats = analysis?.heat_vulnerability_summary;
  const selectedScenario = simulation?.results.find((result) => result.intervention_type === selectedScenarioId);
  const displayedGrid = selectedScenario?.grid_geojson ?? metricGrid;
  const displayedProperty = selectedScenario ? (scenarioView === "after" ? "after_score" : "before_score") : undefined;

  return (
    <main className="flex h-screen flex-col overflow-hidden bg-[#f6f7f4] text-[#30352f]">
      <header className="border-b border-[#dfe4de] bg-white">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-5 lg:px-8">
          <div><div className="text-lg font-semibold tracking-tight text-[#254d3b]">Urban Cool</div><div className="text-xs text-[#7a837b]">Heat vulnerability map</div></div>
          <div className="flex items-center gap-2 text-sm text-[#788078]"><MapPin size={14} /> Chennai, Tamil Nadu <span className={`ml-2 h-2 w-2 rounded-full ${health ? "bg-[#4e956d]" : "bg-[#d59a62]"}`} /></div>
        </div>
      </header>

      <div className="mx-auto flex min-h-0 w-full max-w-7xl flex-1 flex-col px-5 py-4 lg:px-8">
        <div className="mb-3 flex items-center justify-between"><div><p className="text-xs text-[#708277]">OMR–ECR corridor</p><h1 className="text-2xl font-semibold tracking-tight text-[#254d3b]">Heat vulnerability map</h1></div><span className="hidden text-sm text-[#788078] lg:block">Select an area to analyze</span></div>

        {error && <div className="mb-5 flex items-center justify-between rounded-md bg-[#fff1e9] px-4 py-3 text-sm text-[#96583e]"><span>{error}</span><button onClick={() => setError(null)} className="underline">close</button></div>}

        <div className="grid min-h-0 flex-1 gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div className="flex min-h-0 min-w-0 flex-col">
            <MapView metric={metric} metricData={displayedGrid} dataProperty={displayedProperty} onRegionSelected={handleRegionSelected} />
            <div className="mt-2 flex justify-end"><button onClick={() => { setSelectedRegion(null); setAnalysis(null); setMetricGrid(undefined); setSimulation(null); setError(null); }} className="flex items-center gap-1.5 text-xs text-[#47755c] hover:underline"><RotateCcw size={13} /> Clear selection</button></div>
          </div>

          <aside className="min-h-0 space-y-3 overflow-hidden pr-1">
            <MetricTogglePanel activeMetricId={activeMetricId} onSelect={selectMetric} />
            <section className="border-t border-[#dfe4de] pt-4">
              <p className="text-sm font-medium text-[#5d6c61]">Selected area</p>
              <p className="mt-1 text-xl font-semibold text-[#254d3b]">{analysis ? `${analysis.pixel_count.toLocaleString()} pixels` : selectedRegion ? "Ready to analyze" : "Nothing selected"}</p>
              {stats && <div className="mt-3 flex gap-8 text-sm"><div><p className="font-mono text-xl text-[#b66346]">{stats.mean.toFixed(1)}</p><p className="text-[#7a837b]">average score</p></div><div><p className="font-mono text-xl text-[#b66346]">{stats.max.toFixed(1)}</p><p className="text-[#7a837b]">highest score</p></div></div>}
              <button disabled={!selectedRegion || busy === "analyze"} onClick={analyze} className="mt-4 flex w-full items-center justify-center gap-2 rounded-md bg-[#39785b] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#2f684d] disabled:cursor-not-allowed disabled:opacity-40">{busy === "analyze" && <Loader2 size={15} className="animate-spin" />}{analysis ? "Update analysis" : "Analyze area"}</button>
            </section>
            <section className="border-t border-[#dfe4de] pt-4"><ExplanationPanel isLoading={busy === "analyze"} plainLanguageSummary={analysis?.plain_language_summary ?? null} shapSummary={analysis?.shap_summary ?? null} /></section>
          </aside>
        </div>

        <div className="mt-3 grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px]"><InterventionPanel results={simulation?.results ?? null} disabled={!analysis} isLoading={busy === "simulate"} selectedId={selectedScenarioId} view={scenarioView} onRun={runScenarios} onSelect={(id, nextView) => { setSelectedScenarioId(id); setScenarioView(nextView); }} /><div /></div>
      </div>
    </main>
  );
}
