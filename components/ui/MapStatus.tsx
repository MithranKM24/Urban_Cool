import type { ReactNode } from "react";

interface MapStatusProps {
  children: ReactNode;
  tone?: "default" | "error";
}

export default function MapStatus({ children, tone = "default" }: MapStatusProps) {
  const color = tone === "error" ? "text-[#b45f42]" : "text-[#4a463c]";

  return (
    <div className={`absolute top-4 left-4 max-w-xs rounded bg-white/90 px-3 py-2 text-sm shadow-sm z-20 ${color}`}>
      {children}
    </div>
  );
}
