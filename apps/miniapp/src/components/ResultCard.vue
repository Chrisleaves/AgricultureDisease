<template>
  <view class="result-card surface-card">
    <view class="result-heading">
      <view>
        <text class="eyebrow">{{ result.is_preview ? "预览模式 · 模拟结果" : "模型首选结果" }}</text>
        <text class="result-name">{{ result.classifier_top1 }}</text>
      </view>
      <text class="confidence-tag" :class="`confidence-${result.confidence_level}`">
        {{ confidenceLabel }}可信度
      </text>
    </view>

    <view class="confidence-row">
      <text>置信度</text>
      <text class="confidence-value">{{ percentage(result.confidence) }}</text>
    </view>
    <view class="progress-track">
      <view class="progress-value" :style="{ width: percentage(result.confidence) }" />
    </view>
    <text v-if="result.elapsed_ms" class="elapsed">诊断耗时 {{ (result.elapsed_ms / 1000).toFixed(1) }} 秒</text>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { DiagnosisResult } from "@/types/diagnosis";

const props = defineProps<{ result: DiagnosisResult }>();

const confidenceLabel = computed(() => ({ high: "高", medium: "中", low: "低" }[props.result.confidence_level]));
const percentage = (value: number) => `${Math.round(value * 100)}%`;
</script>

<style scoped lang="scss">
.result-card {
  background: linear-gradient(155deg, #ffffff 25%, #eff9f2);
}

.result-heading,
.confidence-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.eyebrow,
.result-name {
  display: block;
}

.eyebrow {
  margin-bottom: 8rpx;
  color: #718078;
  font-size: 23rpx;
}

.result-name {
  color: #183c28;
  font-size: 40rpx;
  font-weight: 750;
}

.confidence-tag {
  flex-shrink: 0;
  margin-left: 20rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 650;
}

.confidence-high { color: #17683c; background: #dff4e7; }
.confidence-medium { color: #99610c; background: #fff0cf; }
.confidence-low { color: #9d4034; background: #fde6e2; }

.confidence-row {
  margin-top: 30rpx;
  color: #5d6e62;
  font-size: 26rpx;
}

.confidence-value { color: #287b4d; font-weight: 700; }

.progress-track {
  height: 14rpx;
  margin-top: 12rpx;
  overflow: hidden;
  background: #dce8df;
  border-radius: 999rpx;
}

.progress-value {
  height: 100%;
  background: linear-gradient(90deg, #3d9b67, #77bd71);
  border-radius: inherit;
}

.elapsed {
  display: block;
  margin-top: 16rpx;
  color: #87938b;
  font-size: 22rpx;
  text-align: right;
}
</style>
