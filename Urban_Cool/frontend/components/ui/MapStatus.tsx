import type { ReactNode } from "react";

interface MapStatusProps {
  children: ReactNode;
  tone?: "default" | "error";
}

export default function MapStatus({ children, tone = "default" }: MapStatusProps) {
  const color = tone === "error" ? "text-[#b45f42]" : "text-[#4a463c]";

  return (
    <div className={`absolute top-4 left-4 max-w-xs bg-white/95 rounded-lg shadow-lg px-4 py-3 text-sm z-20 ${color}`}>
      {children}
    </div>
  );
}
