export type ConfidenceLevel = "high" | "medium" | "low";
export type DiagnosisStatus = "ok" | "need_recapture";

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
  diagnosis_status: DiagnosisStatus;
  recapture_reason: string | null;
  vlm_report: string | null;
  vlm_error: string | null;
  elapsed_ms: number;
  is_preview?: boolean;
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
  imagePath?: string;
  result: DiagnosisResult;
}

export type DiagnosisStage = "idle" | "validating" | "uploading" | "success" | "error";
