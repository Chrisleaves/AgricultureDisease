<template>
  <view class="page-shell history-page">
    <view class="history-header">
      <view>
        <text class="page-title">最近诊断</text>
        <text class="muted-text">最多在本机保存 20 条记录</text>
      </view>
      <button v-if="history.length" class="clear-button" @click="confirmClear">清空</button>
    </view>

    <view v-if="history.length" class="history-list">
      <view v-for="item in history" :key="item.id" class="surface-card history-item" @click="openResult(item.id)">
        <view class="item-topline">
          <text class="disease-name">{{ item.result.classifier_top1 }}</text>
          <text class="confidence-pill" :class="`pill-${item.result.confidence_level}`">
            {{ confidenceText(item.result.confidence_level) }}
          </text>
        </view>
        <view class="item-bottomline">
          <text>{{ formatDate(item.createdAt) }}</text>
          <text class="score">{{ Math.round(item.result.confidence * 100) }}% ›</text>
        </view>
      </view>
    </view>

    <view v-else class="surface-card empty-history">
      <text class="empty-symbol">⌁</text>
      <text class="empty-title">暂无诊断记录</text>
      <text class="muted-text">完成一次图片诊断后，结果会保存在这里。</text>
      <button class="secondary-button start-button" @click="goToDiagnosis">开始诊断</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import type { ConfidenceLevel, DiagnosisHistoryItem } from "@/types/diagnosis";
import { clearDiagnosisHistory, getDiagnosisHistory } from "@/utils/history";

const history = ref<DiagnosisHistoryItem[]>([]);

onShow(() => {
  history.value = getDiagnosisHistory();
});

function confidenceText(level: ConfidenceLevel) {
  return { high: "高可信", medium: "中可信", low: "低可信" }[level];
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function openResult(id: string) {
  uni.navigateTo({ url: `/pages/result/index?id=${encodeURIComponent(id)}` });
}

function goToDiagnosis() {
  uni.switchTab({ url: "/pages/diagnosis/index" });
}

function confirmClear() {
  uni.showModal({
    title: "清空诊断记录",
    content: "此操作只清理当前设备上的记录，且无法恢复。",
    success(response) {
      if (!response.confirm) return;
      clearDiagnosisHistory();
      history.value = [];
    },
  });
}
</script>

<style scoped lang="scss">
.history-header { display: flex; align-items: center; justify-content: space-between; margin: 10rpx 4rpx 24rpx; }
.page-title { display: block; margin-bottom: 5rpx; color: #183c28; font-size: 40rpx; font-weight: 750; }
.clear-button { margin: 0; padding: 8rpx 22rpx; color: #9c4337; background: #fff0ed; border-radius: 999rpx; font-size: 24rpx; line-height: 1.8; }
.history-item { margin-bottom: 18rpx; }
.item-topline,.item-bottomline { display: flex; align-items: center; justify-content: space-between; }
.disease-name { max-width: 500rpx; overflow: hidden; color: #294431; font-size: 31rpx; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.confidence-pill { padding: 7rpx 14rpx; border-radius: 999rpx; font-size: 21rpx; }
.pill-high { color: #17683c; background: #dff4e7; }
.pill-medium { color: #99610c; background: #fff0cf; }
.pill-low { color: #9d4034; background: #fde6e2; }
.item-bottomline { margin-top: 18rpx; color: #819087; font-size: 23rpx; }
.score { color: #287b4d; font-size: 25rpx; font-weight: 650; }
.empty-history { display: flex; flex-direction: column; align-items: center; margin-top: 90rpx; text-align: center; }
.empty-symbol { color: #75a482; font-size: 80rpx; line-height: 1; }
.empty-title { margin: 18rpx 0 9rpx; color: #294431; font-size: 32rpx; font-weight: 700; }
.start-button { width: 100%; margin-top: 28rpx; }
</style>
