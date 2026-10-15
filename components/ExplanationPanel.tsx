import { ShapContribution } from "@/lib/api-client";
import { getMetricById } from "@/lib/metrics";

// The plain-language sentence explains the main factors behind the score.
interface ExplanationPanelProps {
  shapSummary: ShapContribution[] | null;
  plainLanguageSummary: string | null;
  isLoading: boolean;
}

export default function ExplanationPanel({ shapSummary, plainLanguageSummary, isLoading }: ExplanationPanelProps) {
  return (
    <div>
      <div className="mb-2 text-sm font-medium text-[#5d6c61]">What is driving it?</div>
      <div className="text-sm leading-6 text-[#59665d]">
        {isLoading
          ? "Analyzing region..."
          : plainLanguageSummary ?? "Draw a region on the map to see which factors drive its heat vulnerability score."}
      </div>
      {shapSummary && shapSummary.length > 0 && (
        <div className="mt-2.5 flex flex-col gap-1">
          {shapSummary.slice(0, 4).map((c) => (
            <div key={c.feature} className="flex items-center justify-between text-sm text-[#6b6656]">
              <span>{getMetricLabelSafe(c.feature)}</span>
              <span className="font-mono" style={{ color: c.mean_shap_value >= 0 ? "#b45f42" : "#2f7d5e" }}>
                {c.mean_shap_value >= 0 ? "+" : ""}
                {c.mean_shap_value.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function getMetricLabelSafe(featureId: string): string {
  try {
    return getMetricById(featureId).label;
  } catch {
    return featureId;
  }
}
