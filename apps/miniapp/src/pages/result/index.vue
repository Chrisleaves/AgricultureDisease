<template>
  <view class="page-shell result-page">
    <template v-if="result">
      <view v-if="historyItem" class="surface-card diagnosis-source">
        <image
          v-if="historyItem.imagePath"
          class="diagnosis-image"
          :src="historyItem.imagePath"
          mode="aspectFit"
        />
        <view class="diagnosis-meta">
          <text class="diagnosis-meta-title">本次诊断图片</text>
          <text class="diagnosis-time">{{ formatDateTime(historyItem.createdAt) }}</text>
        </view>
      </view>
      <ResultCard :result="result" />
      <CandidateChart :candidates="result.candidates" />
      <ReportSections :report="result.vlm_report" :error="result.vlm_error" />

      <view class="safety-card">
        <text class="safety-heading">重要提示</text>
        <text>AI 结果不能替代田间调查与专业鉴定。涉及农药时，请严格遵守产品标签、当地登记范围、安全间隔期和个人防护要求。</text>
      </view>

      <button class="primary-button action-button" @click="backToDiagnosis">继续诊断</button>
    </template>

    <view v-else class="surface-card empty-result">
      <text class="empty-icon">?</text>
      <text class="empty-title">没有可展示的诊断结果</text>
      <text class="muted-text">结果可能已被清理，请返回诊断页重新识别。</text>
      <button class="secondary-button back-button" @click="backToDiagnosis">返回诊断</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import CandidateChart from "@/components/CandidateChart.vue";
import ReportSections from "@/components/ReportSections.vue";
import ResultCard from "@/components/ResultCard.vue";
import { useDiagnosisStore } from "@/stores/diagnosis";
import type { DiagnosisHistoryItem, DiagnosisResult } from "@/types/diagnosis";
import { findDiagnosisHistory } from "@/utils/history";

const { state } = useDiagnosisStore();
const result = ref<DiagnosisResult | null>(null);
const historyItem = ref<DiagnosisHistoryItem | null>(null);

onLoad((options) => {
  const historyId = typeof options?.id === "string" ? decodeURIComponent(options.id) : "";
  historyItem.value = historyId ? findDiagnosisHistory(historyId) ?? null : null;
  result.value = historyItem.value?.result ?? state.latestResult;
});

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function backToDiagnosis() {
  uni.switchTab({ url: "/pages/diagnosis/index" });
}
</script>

<style scoped lang="scss">
.result-page { padding-top: 22rpx; }
.diagnosis-source { margin-bottom: 24rpx; padding: 0; overflow: hidden; }
.diagnosis-image { display: block; width: 100%; height: 390rpx; background: #14251a; }
.diagnosis-meta { display: flex; align-items: center; justify-content: space-between; padding: 22rpx 26rpx; }
.diagnosis-meta-title { color: #294431; font-size: 26rpx; font-weight: 700; }
.diagnosis-time { color: #718078; font-size: 23rpx; }
.safety-card { margin-top: 24rpx; padding: 24rpx 26rpx; color: #71551f; background: #fff7df; border: 1rpx solid #f0dc9f; border-radius: 18rpx; font-size: 25rpx; line-height: 1.7; }
.safety-heading { display: block; margin-bottom: 6rpx; font-weight: 700; }
.action-button { margin-top: 26rpx; }
.empty-result { display: flex; flex-direction: column; align-items: center; margin-top: 80rpx; text-align: center; }
.empty-icon { display: flex; width: 92rpx; height: 92rpx; align-items: center; justify-content: center; color: #fff; background: #8eaa96; border-radius: 50%; font-size: 42rpx; font-weight: 700; }
.empty-title { margin: 24rpx 0 10rpx; color: #294431; font-size: 32rpx; font-weight: 700; }
.back-button { width: 100%; margin-top: 26rpx; }
</style>
