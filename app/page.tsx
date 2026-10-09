"use client";

import { useMemo, useState } from "react";
import { ArrowUpRight, Download, Info, Layers3, MapPin, Menu, Search, SlidersHorizontal } from "lucide-react";
import ExplanationPanel from "@/components/ExplanationPanel";
import CaveatBanner from "@/components/ui/CaveatBanner";
import Legend from "@/components/ui/Legend";
import MapStatus from "@/components/ui/MapStatus";
import MetricTogglePanel from "@/components/ui/MetricTogglePanel";
import { getMetricById } from "@/lib/metrics";

const neighborhoods = [
  { name: "Sholinganallur", x: "64%", y: "34%", score: 82, size: "h-14 w-14" },
  { name: "Perungudi", x: "48%", y: "50%", score: 68, size: "h-10 w-10" },
  { name: "Thoraipakkam", x: "70%", y: "60%", score: 74, size: "h-12 w-12" },
  { name: "Navalur", x: "77%", y: "76%", score: 91, size: "h-16 w-16" },
  { name: "Velachery", x: "30%", y: "68%", score: 57, size: "h-9 w-9" },
  { name: "Kandanchavadi", x: "39%", y: "25%", score: 63, size: "h-11 w-11" },
];

export default function HomePage() {
  const [activeMetricId, setActiveMetricId] = useState("heat_vulnerability");
  const metric = useMemo(() => getMetricById(activeMetricId), [activeMetricId]);

  return (
    <main className="flex min-h-screen flex-col bg-[#f5f2eb] text-[#292821]">
      <header className="flex h-[72px] items-center justify-between border-b border-[#ded9ce] bg-[#fbfaf7] px-6 lg:px-10">
        <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#1e3a5f] text-sm font-bold text-white">UC</div><div><div className="text-[15px] font-semibold tracking-tight text-[#1e3a5f]">Urban Cool</div><div className="text-[10px] uppercase tracking-[0.18em] text-[#938d7e]">Heat vulnerability explorer</div></div></div>
        <div className="hidden items-center gap-6 text-[12px] text-[#716b5e] md:flex"><span className="flex items-center gap-1.5"><MapPin size={14} /> Chennai, Tamil Nadu</span><span className="h-4 w-px bg-[#ded9ce]" /><span>Data updated Oct 2024</span><button className="rounded-md border border-[#d9d3c7] bg-white px-3 py-1.5 font-medium text-[#4a463c] shadow-sm">About this map</button></div>
        <Menu className="text-[#4a463c] md:hidden" size={20} />
      </header>

      <div className="mx-auto flex w-full max-w-[1500px] flex-1 flex-col gap-5 p-5 lg:p-8">
        <section className="flex flex-col justify-between gap-4 lg:flex-row lg:items-end"><div><div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#a09a89]"><Layers3 size={14} /> OMR–ECR corridor</div><h1 className="text-3xl font-semibold tracking-tight text-[#1e3a5f] lg:text-[38px]">See where heat hits hardest.</h1><p className="mt-2 max-w-2xl text-[14px] leading-relaxed text-[#716b5e]">Explore the factors shaping heat vulnerability across Chennai&apos;s fast-growing southern corridor.</p></div><div className="flex items-center gap-2"><button className="flex items-center gap-2 rounded-lg border border-[#d8d2c5] bg-white px-3.5 py-2 text-[12px] font-medium text-[#4a463c] shadow-sm"><Download size={14} /> Export view</button><button className="flex items-center gap-2 rounded-lg bg-[#1e3a5f] px-3.5 py-2 text-[12px] font-medium text-white shadow-sm"><SlidersHorizontal size={14} /> Compare areas</button></div></section>

        <section className="grid min-h-[590px] flex-1 gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
          <div className="relative overflow-hidden rounded-xl border border-[#ddd8ce] bg-[#dce6df] shadow-sm"><div className="absolute inset-0 opacity-50 [background-image:linear-gradient(30deg,transparent_49%,#b7c8bc_50%,transparent_51%),linear-gradient(120deg,transparent_49%,#b7c8bc_50%,transparent_51%)] [background-size:90px_90px]" /><div className="absolute inset-0 bg-[radial-gradient(ellipse_at_58%_48%,rgba(245,242,235,0.95)_0%,rgba(219,229,221,0.35)_48%,transparent_70%)]" /><div className="absolute left-[12%] top-[18%] h-[70%] w-[72%] rotate-[19deg] rounded-[48%] border-2 border-dashed border-[#547b68]/60 bg-[#d8e6d9]/40" /><div className="absolute left-[19%] top-[24%] h-[58%] w-[63%] rotate-[19deg] rounded-[48%] border border-white/80" /><svg className="absolute inset-0 h-full w-full opacity-30" viewBox="0 0 800 600" preserveAspectRatio="none" aria-hidden="true"><path d="M90 530 C230 420 200 330 370 310 S560 250 700 55 M220 540 C360 470 390 365 520 360 S630 250 760 180 M50 180 C190 220 270 180 350 90" fill="none" stroke="#789182" strokeWidth="5" /><path d="M120 70 L670 530 M75 420 L650 115 M260 20 L500 580" fill="none" stroke="#91a99a" strokeWidth="2" /></svg>
            {neighborhoods.map((place) => <div key={place.name} className="group absolute -translate-x-1/2 -translate-y-1/2" style={{ left: place.x, top: place.y }}><div className={`${place.size} flex items-center justify-center rounded-full border-[3px] border-white/90 shadow-lg transition-transform group-hover:scale-110`} style={{ background: `hsl(${Math.max(10, 125 - place.score)} 45% ${Math.max(35, 78 - place.score / 3)}%)` }}><span className="font-mono text-[11px] font-bold text-white drop-shadow">{place.score}</span></div><div className="mt-1 whitespace-nowrap rounded bg-white/85 px-1.5 py-0.5 text-[10px] font-medium text-[#4a463c] shadow-sm">{place.name}</div></div>)}
            <MapStatus><span className="flex items-center gap-2"><Search size={14} className="text-[#547b68]" /> Select an area to inspect its score</span></MapStatus><Legend metric={metric} /><div className="absolute right-4 top-4 rounded-lg bg-white/95 p-2 text-[#716b5e] shadow-lg"><Info size={15} /></div><div className="absolute bottom-4 right-4 rounded bg-white/90 px-2 py-1 font-mono text-[10px] text-[#716b5e] shadow">© OpenStreetMap contributors</div>
          </div>
          <aside className="flex flex-col gap-4"><MetricTogglePanel activeMetricId={activeMetricId} onSelect={setActiveMetricId} /><div className="rounded-lg bg-white p-4 shadow-lg"><div className="mb-3 flex items-center justify-between"><div className="text-[11px] font-semibold uppercase tracking-wide text-[#a09a89]">Selected layer</div><span className="rounded bg-[#eef2ee] px-2 py-1 text-[10px] font-semibold text-[#39785b]">LIVE VIEW</span></div><div className="text-lg font-semibold text-[#1e3a5f]">{metric.shortLabel}</div><p className="mt-1 text-[12px] leading-relaxed text-[#716b5e]">{metric.description}.</p><div className="mt-4 grid grid-cols-2 gap-2 border-t border-[#eeeae2] pt-3"><div><div className="font-mono text-xl font-semibold text-[#b45f42]">72.4</div><div className="text-[10px] text-[#938d7e]">corridor average</div></div><div><div className="font-mono text-xl font-semibold text-[#39785b]">14.2k</div><div className="text-[10px] text-[#938d7e]">people covered</div></div></div></div><div className="rounded-lg border border-[#ded9ce] bg-[#fbfaf7] p-4"><ExplanationPanel isLoading={false} plainLanguageSummary="Low tree cover and dense built-up areas are the strongest contributors to vulnerability in this corridor." shapSummary={[{ feature: "tree_cover", mean_shap_value: -0.42 }, { feature: "built_up_density", mean_shap_value: 0.31 }, { feature: "elderly_population", mean_shap_value: 0.18 }]} /></div></aside>
        </section>
        <CaveatBanner caveat="This exploratory view shows modeled patterns, not a property-level risk assessment. Use local knowledge alongside the map." />
      </div>
      <footer className="flex justify-between border-t border-[#ded9ce] px-6 py-3 text-[10px] text-[#938d7e] lg:px-10"><span>URBAN COOL / DECISION SUPPORT TOOL</span><span className="flex items-center gap-1">Built for climate-resilient Chennai <ArrowUpRight size={11} /></span></footer>
    </main>
  );
}
