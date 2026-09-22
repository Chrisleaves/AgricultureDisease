import type {
  ConfidenceLevel,
  DiagnosisCandidate,
  DiagnosisResponseEnvelope,
  DiagnosisResult,
  HealthResponse,
} from "@/types/diagnosis";
import { getConfiguredApiBaseUrl, isPreviewMode, validateModelUrl } from "@/utils/model-config";

const REQUEST_TIMEOUT_MS = 120_000;

export class DiagnosisApiError extends Error {
  constructor(message: string, public readonly statusCode?: number) {
    super(message);
    this.name = "DiagnosisApiError";
  }
}

function getApiBaseUrl(): string {
  const configured = getConfiguredApiBaseUrl();
  if (!configured) {
    throw new DiagnosisApiError("尚未配置模型服务，请返回模型接入页完成设置");
  }
  return configured;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function parseJson(value: unknown): unknown {
  if (typeof value !== "string") return value;

  try {
    return JSON.parse(value) as unknown;
  } catch {
    throw new DiagnosisApiError("服务器返回了无法解析的数据");
  }
}

function getErrorMessage(payload: unknown, fallback: string): string {
  const parsed = parseJson(payload);
  if (!isRecord(parsed)) return fallback;

  const detail = parsed.detail ?? parsed.message;
  return typeof detail === "string" && detail.trim() ? detail : fallback;
}

function isConfidenceLevel(value: unknown): value is ConfidenceLevel {
  return value === "high" || value === "medium" || value === "low";
}

function parseCandidate(value: unknown): DiagnosisCandidate | null {
  if (!isRecord(value)) return null;
  const { label_cn, label_en, score } = value;
  if (typeof label_cn !== "string" || typeof label_en !== "string" || typeof score !== "number") {
    return null;
  }
  if (!Number.isFinite(score) || score < 0 || score > 1) return null;
  return { label_cn, label_en, score };
}

function parseDiagnosisResult(payload: unknown): DiagnosisResult {
  const parsed = parseJson(payload);
  if (!isRecord(parsed)) throw new DiagnosisApiError("诊断响应格式不正确");

  let body: unknown = parsed;
  if ("data" in parsed) {
    if (typeof parsed.code === "number" && parsed.code !== 0) {
      throw new DiagnosisApiError(getErrorMessage(parsed, "诊断服务返回失败"));
    }
    body = (parsed as unknown as DiagnosisResponseEnvelope).data;
  }

  if (!isRecord(body)) throw new DiagnosisApiError("诊断响应缺少 data 字段");

  const candidates = Array.isArray(body.candidates)
    ? body.candidates.map(parseCandidate).filter((item): item is DiagnosisCandidate => item !== null)
    : [];

  if (
    candidates.length === 0 ||
    typeof body.classifier_top1 !== "string" ||
    typeof body.confidence !== "number" ||
    !Number.isFinite(body.confidence) ||
    body.confidence < 0 ||
    body.confidence > 1 ||
    !isConfidenceLevel(body.confidence_level)
  ) {
    throw new DiagnosisApiError("诊断响应缺少必要字段或概率超出范围");
  }

  return {
    candidates,
    classifier_top1: body.classifier_top1,
    confidence: body.confidence,
    confidence_level: body.confidence_level,
    vlm_report: typeof body.vlm_report === "string" ? body.vlm_report : null,
    vlm_error: typeof body.vlm_error === "string" ? body.vlm_error : null,
    elapsed_ms: typeof body.elapsed_ms === "number" ? body.elapsed_ms : 0,
  };
}

function requestHealth(baseUrl: string): Promise<HealthResponse> {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${baseUrl}/health`,
      method: "GET",
      timeout: 15_000,
      success(response) {
        if (response.statusCode < 200 || response.statusCode >= 300) {
          reject(new DiagnosisApiError(getErrorMessage(response.data, "模型服务暂不可用"), response.statusCode));
          return;
        }

        const data = parseJson(response.data);
        if (!isRecord(data) || typeof data.status !== "string") {
          reject(new DiagnosisApiError("健康检查响应格式不正确"));
          return;
        }
        resolve(data as HealthResponse);
      },
      fail(error) {
        reject(new DiagnosisApiError(error.errMsg || "无法连接模型服务"));
      },
    });
  });
}

export function checkHealth(): Promise<HealthResponse> {
  if (isPreviewMode()) return Promise.resolve({ status: "preview" });
  return requestHealth(getApiBaseUrl());
}

export function checkHealthAtUrl(value: string): Promise<HealthResponse> {
  let baseUrl: string;
  try {
    baseUrl = validateModelUrl(value);
  } catch (error) {
    return Promise.reject(new DiagnosisApiError(error instanceof Error ? error.message : "模型服务 URL 不正确"));
  }
  return requestHealth(baseUrl);
}

function getPreviewResult(): DiagnosisResult {
  return {
    candidates: [
      { label_cn: "番茄-晚疫病（示例）", label_en: "Tomato Late blight", score: 0.82 },
      { label_cn: "番茄-早疫病（示例）", label_en: "Tomato Early blight", score: 0.12 },
      { label_cn: "番茄-叶霉病（示例）", label_en: "Tomato Leaf Mold", score: 0.04 },
    ],
    classifier_top1: "番茄-晚疫病（预览示例）",
    confidence: 0.82,
    confidence_level: "high",
    vlm_report:
      "【最终诊断】这是预览模式生成的模拟结果，不代表所选图片的真实诊断。\n\n【诊断依据】当前没有连接模型服务，此处用于演示候选概率、报告分段和页面布局。\n\n【防治方案】接入真实模型后，请根据真实结果并结合当地登记用药制定方案。\n\n【复查建议】配置模型 URL 后重新诊断，并由农技人员结合田间症状复核。",
    vlm_error: null,
    elapsed_ms: 900,
    is_preview: true,
  };
}

export function diagnoseImage(filePath: string): Promise<DiagnosisResult> {
  if (isPreviewMode()) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(getPreviewResult()), 900);
    });
  }

  const baseUrl = getApiBaseUrl();
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${baseUrl}/diagnose`,
      filePath,
      name: "image",
      timeout: REQUEST_TIMEOUT_MS,
      success(response) {
        if (response.statusCode < 200 || response.statusCode >= 300) {
          reject(new DiagnosisApiError(getErrorMessage(response.data, "图片诊断失败"), response.statusCode));
          return;
        }

        try {
          resolve(parseDiagnosisResult(response.data));
        } catch (error) {
          reject(error);
        }
      },
      fail(error) {
        const message = error.errMsg?.includes("timeout")
          ? "诊断超时，请检查网络后重试"
          : error.errMsg || "图片上传失败，请检查网络后重试";
        reject(new DiagnosisApiError(message));
      },
    });
  });
}

export function getReadableError(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  return "发生未知错误，请稍后重试";
}
