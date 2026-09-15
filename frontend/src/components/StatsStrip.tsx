"use client";

import { Lead } from "@/lib/api";

interface Props {
  leads: Lead[];
}

export function StatsStrip({ leads }: Props) {
  const total = leads.length;
  const hot = leads.filter((l) => l.ai_tier === "Hot").length;
  const warm = leads.filter((l) => l.ai_tier === "Warm").length;
  const cold = leads.filter((l) => l.ai_tier === "Cold").length;
  const avgScore =
    total > 0
      ? leads.reduce((sum, l) => sum + (l.ai_score || 0), 0) /
          leads.filter((l) => l.ai_score !== null).length || 0
      : 0;

  const stats = [
    { label: "Active leads", value: total },
    { label: "Hot", value: hot, color: "text-tier-hot" },
    { label: "Warm", value: warm, color: "text-tier-warm" },
    { label: "Cold", value: cold, color: "text-tier-cold" },
    { label: "Avg score", value: avgScore.toFixed(1) },
  ];

  return (
    <div className="max-w-6xl mx-auto px-6 py-6 flex flex-wrap gap-x-8 gap-y-3">
      {stats.map((s, i) => (
        <div
          key={s.label}
          className={i > 0 ? "pl-8 border-l border-hairline" : ""}
        >
          <div
            className={`text-2xl tabular font-medium ${s.color || "text-text-primary"}`}
          >
            {s.value}
          </div>
          <div className="text-xs text-text-secondary mt-0.5">{s.label}</div>
        </div>
      ))}
    </div>
  );
}
