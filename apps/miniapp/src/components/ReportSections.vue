<template>
  <view class="surface-card report-card">
    <text class="section-title">诊断与处置建议</text>
    <view v-if="sections.length">
      <view v-for="section in sections" :key="section.title" class="report-section">
        <text class="report-heading">{{ section.title }}</text>
        <text class="report-content" selectable>{{ section.content }}</text>
      </view>
    </view>
    <view v-else class="fallback-copy">
      <text>模型复核报告暂不可用，请结合候选结果观察植株，并咨询当地农技人员。</text>
      <text v-if="error" class="error-copy">原因：{{ error }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  report: string | null;
  error: string | null;
}>();

const sections = computed(() => {
  if (!props.report?.trim()) return [];
  const normalized = props.report.replace(/\r\n/g, "\n").trim();
  const matches = [...normalized.matchAll(/【([^】]+)】/g)];
  if (!matches.length) return [{ title: "模型复核", content: normalized }];

  return matches.map((match, index) => {
    const start = (match.index ?? 0) + match[0].length;
    const end = index + 1 < matches.length ? matches[index + 1].index ?? normalized.length : normalized.length;
    return {
      title: match[1].trim(),
      content: normalized.slice(start, end).trim(),
    };
  }).filter((section) => section.content);
});
</script>

<style scoped lang="scss">
.report-card { margin-top: 24rpx; }
.report-section + .report-section { margin-top: 28rpx; padding-top: 28rpx; border-top: 1rpx solid #edf1ee; }
.report-heading { display: block; margin-bottom: 10rpx; color: #287b4d; font-size: 28rpx; font-weight: 700; }
.report-content,
.fallback-copy { color: #435148; font-size: 27rpx; line-height: 1.8; white-space: pre-wrap; }
.error-copy { display: block; margin-top: 14rpx; color: #966054; font-size: 24rpx; }
</style>
