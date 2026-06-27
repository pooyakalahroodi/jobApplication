const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type JobAd = {
  id: number;
  url: string | null;
  title: string;
  company: string | null;
  location: string | null;
  description: string | null;
  source: string | null;
  page_title: string | null;
  selected_text: string | null;
  raw_text: string | null;
  json_ld: Record<string, unknown>[] | null;
  status: "not_applied" | "applied" | "rejected" | "accepted" | "archived";
  captured_at: string | null;
  created_at: string;
};

export type Email = {
  id: number;
  subject: string;
  sender: string | null;
  body: string;
  extracted_company: string | null;
  extracted_role_title: string | null;
  extraction_confidence: number | null;
  received_at: string | null;
  email_status: "pending" | "rejected" | "accepted" | "unknown";
  match_status: "not_set" | "set" | "needs_review";
  created_at: string;
};

export type Application = {
  id: number;
  job_ad_id: number | null;
  status: "applied" | "pending" | "rejected" | "accepted" | "unknown";
  company: string | null;
  role_title: string | null;
  created_at: string;
  updated_at: string;
};

export type MatchingRunResult = {
  processed_count: number;
  matched_count: number;
  needs_review_count: number;
  unmatched_count: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function listJobAds() {
  return request<JobAd[]>("/job-ads");
}

export function listEmails() {
  return request<Email[]>("/emails");
}

export function listApplications() {
  return request<Application[]>("/applications");
}

export function runMatching() {
  return request<MatchingRunResult>("/matching/run", { method: "POST" });
}

