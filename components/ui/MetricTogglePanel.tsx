import { METRICS } from "@/lib/metrics";
import MetricSwatch from "@/components/ui/MetricSwatch";

interface MetricTogglePanelProps {
  activeMetricId: string;
  onSelect: (id: string) => void;
}

export default function MetricTogglePanel({ activeMetricId, onSelect }: MetricTogglePanelProps) {
  return (
    <div className="w-full bg-white rounded-lg shadow-lg p-3.5 shrink-0">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-[#a09a89] mb-2.5">Metric layer</div>
      <div className="flex flex-col gap-0.5">
        {METRICS.map((metric) => {
          const active = metric.id === activeMetricId;

          return (
            <button
              key={metric.id}
              onClick={() => onSelect(metric.id)}
              className="flex items-center gap-2.5 px-2 py-2 rounded-md text-left w-full transition-colors"
              style={{ background: active ? "#eef2ee" : "transparent" }}
            >
              <MetricSwatch colors={metric.stops} diverging={metric.kind === "diverging"} />
              <span
                className="text-[12.8px]"
                style={{ color: active ? "#1e3a5f" : "#4a463c", fontWeight: active ? 600 : 400 }}
              >
                {metric.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
