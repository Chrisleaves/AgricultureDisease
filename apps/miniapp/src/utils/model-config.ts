export type ModelAccessMode = "api" | "preview";

export interface ModelAccessConfig {
  mode: ModelAccessMode;
  baseUrl: string;
  updatedAt: string;
}

const MODEL_CONFIG_KEY = "model-access-config-v1";

export function normalizeModelUrl(value: string): string {
  return value
    .trim()
    .replace(/\/(health|diagnose)\/?$/i, "")
    .replace(/\/+$/, "");
}

export function validateModelUrl(value: string): string {
  const normalized = normalizeModelUrl(value);
  if (!normalized) throw new Error("请输入模型服务 URL");
  if (!/^https?:\/\//i.test(normalized)) throw new Error("URL 必须以 http:// 或 https:// 开头");

  if (!/^https?:\/\/[^\s]+$/i.test(normalized)) {
    throw new Error("URL 格式不正确，请检查后重试");
  }

  return normalized;
}

export function getModelAccessConfig(): ModelAccessConfig | null {
  try {
    const stored = uni.getStorageSync(MODEL_CONFIG_KEY) as Partial<ModelAccessConfig> | "";
    if (!stored || (stored.mode !== "api" && stored.mode !== "preview")) return null;
    return {
      mode: stored.mode,
      baseUrl: typeof stored.baseUrl === "string" ? stored.baseUrl : "",
      updatedAt: typeof stored.updatedAt === "string" ? stored.updatedAt : "",
    };
  } catch {
    return null;
  }
}

export function saveApiModelConfig(baseUrl: string): ModelAccessConfig {
  const config: ModelAccessConfig = {
    mode: "api",
    baseUrl: validateModelUrl(baseUrl),
    updatedAt: new Date().toISOString(),
  };
  uni.setStorageSync(MODEL_CONFIG_KEY, config);
  return config;
}

export function savePreviewModelConfig(): ModelAccessConfig {
  const config: ModelAccessConfig = {
    mode: "preview",
    baseUrl: "",
    updatedAt: new Date().toISOString(),
  };
  uni.setStorageSync(MODEL_CONFIG_KEY, config);
  return config;
}

export function getConfiguredApiBaseUrl(): string {
  const config = getModelAccessConfig();
  if (config?.mode === "api" && config.baseUrl) return config.baseUrl;

  const environmentUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  return environmentUrl ? normalizeModelUrl(environmentUrl) : "";
}

export function isPreviewMode(): boolean {
  return getModelAccessConfig()?.mode === "preview";
}
