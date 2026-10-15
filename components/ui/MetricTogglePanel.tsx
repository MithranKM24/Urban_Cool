import { METRICS } from "@/lib/metrics";
import MetricSwatch from "@/components/ui/MetricSwatch";

interface MetricTogglePanelProps {
  activeMetricId: string;
  onSelect: (id: string) => void;
}

export default function MetricTogglePanel({ activeMetricId, onSelect }: MetricTogglePanelProps) {
  return (
    <div className="w-full">
      <div className="mb-2 text-sm font-medium text-[#5d6c61]">Map layer</div>
      <div className="flex flex-col gap-1">
        {METRICS.map((metric) => {
          const active = metric.id === activeMetricId;

          return (
            <button
              key={metric.id}
              onClick={() => onSelect(metric.id)}
              className="flex w-full items-center gap-2.5 rounded px-2 py-2 text-left text-sm transition-colors hover:bg-[#eaf0ea]"
              style={{ background: active ? "#e3eee5" : "transparent" }}
            >
              <MetricSwatch colors={metric.stops} diverging={metric.kind === "diverging"} />
              <span
                className="text-[14px]"
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
