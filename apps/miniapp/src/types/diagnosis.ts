export type ConfidenceLevel = "high" | "medium" | "low";

export interface DiagnosisCandidate {
  label_cn: string;
  label_en: string;
  score: number;
}

export interface DiagnosisResult {
  candidates: DiagnosisCandidate[];
  classifier_top1: string;
  confidence: number;
  confidence_level: ConfidenceLevel;
  vlm_report: string | null;
  vlm_error: string | null;
  elapsed_ms: number;
}

export interface DiagnosisResponseEnvelope {
  code: number;
  data: DiagnosisResult;
  message?: string;
}

export interface HealthResponse {
  status: string;
  [key: string]: unknown;
}

export interface SelectedImage {
  id: string;
  path: string;
  size: number;
  width?: number;
  height?: number;
  type?: string;
}

export interface DiagnosisHistoryItem {
  id: string;
  createdAt: string;
  result: DiagnosisResult;
}

export type DiagnosisStage = "idle" | "validating" | "uploading" | "success" | "error";
