import { MetricDefinition } from "@/lib/metrics";

interface LegendProps {
  metric: MetricDefinition;
  labelOverride?: string;
}

export default function Legend({ metric, labelOverride }: LegendProps) {
  return (
    <div className="absolute bottom-4 left-4 z-20 min-w-[220px] rounded bg-white/90 p-3 shadow-sm">
      <div className="mb-2 text-sm font-medium text-[#4a463c]">{labelOverride ?? metric.label}</div>
      <div className="h-2.5 rounded-full" style={{ background: `linear-gradient(90deg, ${metric.stops.join(",")})` }} />
      <div className="flex justify-between mt-1.5 text-sm text-[#8a8578] font-mono">
        <span>{metric.minLabel}</span>
        <span>{metric.maxLabel}</span>
      </div>
    </div>
  );
}
