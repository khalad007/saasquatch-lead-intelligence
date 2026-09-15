"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchLeads, LeadFilters } from "@/lib/api";
import { ControlPanel } from "@/components/ControlPanel";
import { FilterBar } from "@/components/FilterBar";
import { StatsStrip } from "@/components/StatsStrip";
import { LeadsTable } from "@/components/LeadsTable";

export default function DashboardPage() {
  const [filters, setFilters] = useState<LeadFilters>({
    sort_by: "ai_score",
    order: "desc",
  });

  const { data: leads = [], isLoading } = useQuery({
    queryKey: ["leads", filters],
    queryFn: () => fetchLeads(filters),
  });

  return (
    <main className="flex-1">
      <header className="border-b border-hairline">
        <div className="max-w-6xl mx-auto px-6 pt-8 pb-4">
          <h1 className="text-lg">Lead Intelligence</h1>
          <p className="text-sm text-text-secondary mt-1">
            Deduplication, validation, and AI-prioritized scoring for scraped B2B leads.
          </p>
        </div>
      </header>

      <ControlPanel />
      <FilterBar filters={filters} onChange={setFilters} />
      <StatsStrip leads={leads} />
      <LeadsTable leads={leads} isLoading={isLoading} />
    </main>
  );
}