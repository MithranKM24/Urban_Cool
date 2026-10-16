"use client";

import { Check, Loader2, Sparkles } from "lucide-react";
import { INTERVENTIONS } from "@/lib/metrics";
import type { InterventionResult } from "@/lib/api-types";

interface InterventionPanelProps {
  results: InterventionResult[] | null;
  disabled: boolean;
  isLoading: boolean;
  selectedId: string | null;
  view: "before" | "after";
  onRun: (ids: string[]) => void;
  onSelect: (id: string, view: "before" | "after") => void;
}

export default function InterventionPanel({ results, disabled, isLoading, selectedId, view, onRun, onSelect }: InterventionPanelProps) {
  const ranked = results ? [...results].sort((a, b) => b.mean_improvement - a.mean_improvement) : [];
  const selectedResult = ranked.find((result) => result.intervention_type === selectedId);

  return (
    <section className="border-t border-[#dfe4de] pt-5">
      <div className="flex items-start justify-between gap-3">
        <div><div className="flex items-center gap-2 text-base font-medium text-[#5d6c61]"><Sparkles size={15} /> Cooling scenarios</div><p className="mt-1 text-sm text-[#69736b]">Modeled options ranked by average improvement.</p></div>
        <button disabled={disabled || isLoading} onClick={() => onRun(INTERVENTIONS.map((item) => item.id))} className="flex shrink-0 items-center gap-1.5 rounded bg-[#39785b] px-3 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40">{isLoading ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />} Run scenarios</button>
      </div>
      {ranked.length > 0 && <div className="mt-4 grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="divide-y divide-[#e1e5e1] border-y border-[#e1e5e1]">
          {ranked.map((result, index) => { const label = INTERVENTIONS.find((item) => item.id === result.intervention_type)?.label ?? result.intervention_type; return <button key={result.intervention_type} onClick={() => onSelect(result.intervention_type, view)} className={`flex w-full items-center gap-3 px-2 py-2.5 text-left hover:bg-[#eef3ee] ${selectedId === result.intervention_type ? "bg-[#e7f0e8]" : ""}`}><span className="w-5 text-xs text-[#8b948c]">{index + 1}</span><span className="flex-1 text-sm text-[#3e4d43]">{label}</span><span className="font-mono text-sm text-[#39785b]">−{result.mean_improvement.toFixed(2)}</span>{selectedId === result.intervention_type && <Check size={14} className="text-[#39785b]" />}</button>; })}
        </div>
        {selectedResult && <div className="text-sm"><div className="mb-2 flex gap-1 rounded bg-[#eef3ee] p-1"><button onClick={() => onSelect(selectedResult.intervention_type, "before")} className={`flex-1 rounded px-2 py-1 ${view === "before" ? "bg-white text-[#254d3b] shadow-sm" : "text-[#788078]"}`}>Before</button><button onClick={() => onSelect(selectedResult.intervention_type, "after")} className={`flex-1 rounded px-2 py-1 ${view === "after" ? "bg-white text-[#254d3b] shadow-sm" : "text-[#788078]"}`}>After</button></div><p className="leading-5 text-[#69736b]">{selectedResult.assumptions.rationale}</p><p className="mt-3 font-medium text-[#5d6c61]">Top locations</p><div className="mt-1 divide-y divide-[#e1e5e1]">{selectedResult.ranked_locations.slice(0, 5).map((location, index) => <div key={`${location.lon}-${location.lat}`} className="flex justify-between py-1.5 text-xs text-[#69736b]"><span>#{index + 1} {location.lat.toFixed(4)}, {location.lon.toFixed(4)}</span><span className="font-mono text-[#39785b]">−{location.improvement.toFixed(2)}</span></div>)}</div></div>}
      </div>}
      {disabled && <p className="mt-3 text-xs text-[#9a5a42]">Analyze a region before running scenarios.</p>}
    </section>
  );
}
