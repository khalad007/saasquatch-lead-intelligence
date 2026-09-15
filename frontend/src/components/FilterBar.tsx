"use client";

import { LeadFilters, Tier, exportUrl } from "@/lib/api";

interface Props {
  filters: LeadFilters;
  onChange: (filters: LeadFilters) => void;
}

const TIERS: Tier[] = ["Hot", "Warm", "Cold"];

export function FilterBar({ filters, onChange }: Props) {
  return (
    <div className="max-w-6xl mx-auto px-6 py-4 flex flex-wrap items-center gap-3">
      <input
        type="text"
        placeholder="Filter by industry…"
        defaultValue={filters.industry}
        onChange={(e) =>
          onChange({ ...filters, industry: e.target.value || undefined })
        }
        className="px-3 py-1.5 text-sm rounded-md bg-panel border border-hairline placeholder:text-text-secondary focus:outline-none focus:border-tier-hot"
      />

      <div className="flex items-center gap-1">
        {TIERS.map((tier) => {
          const active = filters.tier === tier;
          const dotColor =
            tier === "Hot"
              ? "bg-tier-hot"
              : tier === "Warm"
                ? "bg-tier-warm"
                : "bg-tier-cold";
          return (
            <button
              key={tier}
              onClick={() =>
                onChange({ ...filters, tier: active ? undefined : tier })
              }
              className={`px-3 py-1.5 text-sm rounded-md border flex items-center gap-1.5 transition-colors ${
                active
                  ? "border-text-primary bg-hairline"
                  : "border-hairline text-text-secondary hover:border-text-secondary"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
              {tier}
            </button>
          );
        })}
      </div>

      <select
        value={filters.sort_by}
        onChange={(e) =>
          onChange({
            ...filters,
            sort_by: e.target.value as LeadFilters["sort_by"],
          })
        }
        className="px-3 py-1.5 text-sm rounded-md bg-panel border border-hairline focus:outline-none focus:border-tier-hot"
      >
        <option value="ai_score">Sort: AI score</option>
        <option value="estimated_revenue">Sort: Revenue</option>
        <option value="employee_count">Sort: Employees</option>
        <option value="created_at">Sort: Newest</option>
      </select>

      <div className="flex-1" />

      <a
        href={exportUrl(filters)}
        className="px-3 py-1.5 text-sm rounded-md border border-hairline hover:border-text-secondary transition-colors"
      >
        Export CSV
      </a>
    </div>
  );
}
