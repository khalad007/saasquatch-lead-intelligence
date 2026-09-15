import axios from "axios";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export type Tier = "Hot" | "Warm" | "Cold";

export interface Lead {
  id: number;
  company_name: string;
  domain: string | null;
  industry: string | null;
  city: string | null;
  country: string | null;
  employee_count: number | null;
  estimated_revenue: number | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  source_confidence: number | null;
  email_valid: boolean;
  phone_valid: boolean;
  is_duplicate: boolean;
  duplicate_of_id: number | null;
  ai_score: number | null;
  ai_reasoning: string | null;
  ai_tier: Tier | null;
  created_at: string;
}

export interface UploadSummary {
  total_rows: number;
  inserted: number;
  duplicates_flagged: number;
  invalid_emails: number;
  invalid_phones: number;
}

export interface ScoreSummary {
  scored: number;
  hot: number;
  warm: number;
  cold: number;
}

export interface LeadFilters {
  industry?: string;
  tier?: Tier;
  min_score?: number;
  sort_by?: "ai_score" | "estimated_revenue" | "employee_count" | "created_at";
  order?: "asc" | "desc";
}

export async function uploadLeadsCsv(file: File): Promise<UploadSummary> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<UploadSummary>("/leads/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function scoreLeads(rescore = false): Promise<ScoreSummary> {
  const { data } = await api.post<ScoreSummary>(`/leads/score?rescore=${rescore}`);
  return data;
}

export async function fetchLeads(filters: LeadFilters): Promise<Lead[]> {
  const { data } = await api.get<Lead[]>("/leads", { params: filters });
  return data;
}

export function exportUrl(filters: LeadFilters): string {
  const params = new URLSearchParams();
  if (filters.industry) params.set("industry", filters.industry);
  if (filters.tier) params.set("tier", filters.tier);
  if (filters.min_score !== undefined) params.set("min_score", String(filters.min_score));
  return `${API_BASE_URL}/leads/export?${params.toString()}`;
}