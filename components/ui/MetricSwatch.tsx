interface MetricSwatchProps {
  colors: string[];
  diverging?: boolean;
}

export default function MetricSwatch({ colors, diverging = false }: MetricSwatchProps) {
  const background = diverging
    ? `linear-gradient(90deg,${colors[0]},${colors[colors.length - 1]})`
    : colors[colors.length - 1];

  return <span className="w-2.5 h-2.5 rounded-[3px] shrink-0" style={{ background }} />;
}
