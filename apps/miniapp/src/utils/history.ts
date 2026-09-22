import type { DiagnosisHistoryItem, DiagnosisResult } from "@/types/diagnosis";

const HISTORY_KEY = "diagnosis-history-v1";
const MAX_HISTORY_COUNT = 20;

function isHistoryItem(value: unknown): value is DiagnosisHistoryItem {
  if (typeof value !== "object" || value === null) return false;
  const item = value as Partial<DiagnosisHistoryItem>;
  return typeof item.id === "string" && typeof item.createdAt === "string" && !!item.result;
}

export function getDiagnosisHistory(): DiagnosisHistoryItem[] {
  try {
    const stored = uni.getStorageSync(HISTORY_KEY) as unknown;
    if (!Array.isArray(stored)) return [];
    return stored.filter(isHistoryItem).slice(0, MAX_HISTORY_COUNT);
  } catch {
    return [];
  }
}

export function saveDiagnosisHistory(result: DiagnosisResult, imagePath = ""): DiagnosisHistoryItem {
  const now = new Date();
  const item: DiagnosisHistoryItem = {
    id: `${now.getTime()}-${Math.random().toString(36).slice(2, 8)}`,
    createdAt: now.toISOString(),
    imagePath: imagePath || undefined,
    result,
  };
  const next = [item, ...getDiagnosisHistory()].slice(0, MAX_HISTORY_COUNT);
  uni.setStorageSync(HISTORY_KEY, next);
  return item;
}

export function clearDiagnosisHistory() {
  uni.removeStorageSync(HISTORY_KEY);
}

export function findDiagnosisHistory(id: string): DiagnosisHistoryItem | undefined {
  return getDiagnosisHistory().find((item) => item.id === id);
}
