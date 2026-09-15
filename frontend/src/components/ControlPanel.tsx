"use client";

import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadLeadsCsv, scoreLeads, UploadSummary, ScoreSummary } from "@/lib/api";

export function ControlPanel() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const [lastUpload, setLastUpload] = useState<UploadSummary | null>(null);
  const [lastScore, setLastScore] = useState<ScoreSummary | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadLeadsCsv,
    onSuccess: (summary) => {
      setLastUpload(summary);
      setLastScore(null);
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });

  const scoreMutation = useMutation({
    mutationFn: () => scoreLeads(false),
    onSuccess: (summary) => {
      setLastScore(summary);
      queryClient.invalidateQueries({ queryKey: ["leads"] });
    },
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate(file);
    e.target.value = "";
  }

  return (
    <div className="border-b border-hairline bg-panel">
      <div className="max-w-6xl mx-auto px-6 py-4 flex flex-wrap items-center gap-3">
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadMutation.isPending}
          className="px-4 py-2 text-sm rounded-md border border-hairline hover:border-text-secondary transition-colors disabled:opacity-50"
        >
          {uploadMutation.isPending ? "Uploading…" : "Upload leads CSV"}
        </button>

        <button
          onClick={() => scoreMutation.mutate()}
          disabled={scoreMutation.isPending}
          className="px-4 py-2 text-sm rounded-md bg-tier-hot text-bg font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          {scoreMutation.isPending ? "Scoring…" : "Run AI scoring"}
        </button>

        <div className="flex-1" />

        {uploadMutation.isError && (
          <span className="text-sm text-danger">Upload failed. Check the CSV has a company_name column.</span>
        )}

        {lastUpload && !uploadMutation.isPending && (
          <span className="text-sm text-text-secondary tabular">
            Loaded {lastUpload.inserted} rows · {lastUpload.duplicates_flagged} duplicates flagged ·{" "}
            {lastUpload.invalid_emails} invalid emails · {lastUpload.invalid_phones} invalid phones
          </span>
        )}

        {lastScore && !scoreMutation.isPending && (
          <span className="text-sm text-text-secondary tabular">
            Scored {lastScore.scored} · {lastScore.hot} hot · {lastScore.warm} warm · {lastScore.cold} cold
          </span>
        )}
      </div>
    </div>
  );
}