import { AlertTriangle } from "lucide-react";

interface CaveatBannerProps {
  caveat: string;
}

export default function CaveatBanner({ caveat }: CaveatBannerProps) {
  return (
    <div className="flex items-start gap-2 border-t border-[#dfe4de] py-3 text-[#7a837b]">
      <AlertTriangle size={15} className="mt-0.5 shrink-0 text-[#c18a51]" />
      <span className="text-xs leading-5">{caveat}</span>
    </div>
  );
}
