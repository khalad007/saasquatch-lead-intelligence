"use client";

import { Lead } from "@/lib/api";

interface Props {
  leads: Lead[];
  isLoading: boolean;
}

function formatRevenue(value: number | null): string {
  if (value === null) return "—";
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value}`;
}

function tierColor(tier: string | null): string {
  if (tier === "Hot") return "text-tier-hot";
  if (tier === "Warm") return "text-tier-warm";
  if (tier === "Cold") return "text-tier-cold";
  return "text-text-secondary";
}

function tierDot(tier: string | null): string {
  if (tier === "Hot") return "bg-tier-hot";
  if (tier === "Warm") return "bg-tier-warm";
  if (tier === "Cold") return "bg-tier-cold";
  return "bg-text-secondary";
}

export function LeadsTable({ leads, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-16 text-center text-text-secondary text-sm">
        Loading leads…
      </div>
    );
  }

  if (leads.length === 0) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-16 text-center">
        <p className="text-text-primary mb-1">No leads yet.</p>
        <p className="text-text-secondary text-sm">
          Upload a CSV of scraped leads above to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 pb-16">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="border-b border-hairline text-left text-text-secondary">
            <th className="py-2 pr-4 font-normal">Company</th>
            <th className="py-2 pr-4 font-normal">Industry</th>
            <th className="py-2 pr-4 font-normal">Location</th>
            <th className="py-2 pr-4 font-normal text-right">Revenue</th>
            <th className="py-2 pr-4 font-normal text-right">Employees</th>
            <th className="py-2 pr-4 font-normal">Contact</th>
            <th className="py-2 pr-4 font-normal text-right">AI score</th>
            <th className="py-2 pr-0 font-normal">Why</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id} className="border-b border-hairline/60 hover:bg-panel transition-colors">
              <td className="py-3 pr-4">
                <div className="text-text-primary">{lead.company_name}</div>
                {lead.domain && <div className="text-xs text-text-secondary">{lead.domain}</div>}
              </td>
              <td className="py-3 pr-4 text-text-secondary">{lead.industry || "—"}</td>
              <td className="py-3 pr-4 text-text-secondary">
                {[lead.city, lead.country].filter(Boolean).join(", ") || "—"}
              </td>
              <td className="py-3 pr-4 text-right tabular">{formatRevenue(lead.estimated_revenue)}</td>
              <td className="py-3 pr-4 text-right tabular">{lead.employee_count ?? "—"}</td>
              <td className="py-3 pr-4">
                <div className="flex items-center gap-1.5">
                  <span className={lead.email_valid ? "text-text-primary" : "text-danger line-through decoration-danger/60"}>
                    {lead.email || "no email"}
                  </span>
                </div>
                <div className={`text-xs ${lead.phone_valid ? "text-text-secondary" : "text-danger"}`}>
                  {lead.phone || "no phone"}
                </div>
              </td>
              <td className="py-3 pr-4 text-right">
                <div className="flex items-center justify-end gap-1.5">
                  <span className={`w-1.5 h-1.5 rounded-full ${tierDot(lead.ai_tier)}`} />
                  <span className={`tabular font-medium ${tierColor(lead.ai_tier)}`}>
                    {lead.ai_score !== null ? lead.ai_score.toFixed(1) : "—"}
                  </span>
                </div>
              </td>
              <td className="py-3 pr-0 text-text-secondary max-w-xs text-xs leading-snug">
                {lead.ai_reasoning || "Not scored yet"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}