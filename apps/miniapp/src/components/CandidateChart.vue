<template>
  <view class="surface-card chart-card">
    <text class="section-title">候选概率</text>
    <view class="chart-layout">
      <canvas canvas-id="candidate-chart" class="pie-canvas" />
      <view class="legend">
        <view v-for="(item, index) in chartData" :key="item.label" class="legend-item">
          <view class="legend-dot" :style="{ backgroundColor: colors[index] }" />
          <view class="legend-copy">
            <text class="legend-name">{{ item.label }}</text>
            <text class="legend-score">{{ percentage(item.score) }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onMounted, watch } from "vue";
import type { DiagnosisCandidate } from "@/types/diagnosis";

const props = defineProps<{ candidates: DiagnosisCandidate[] }>();
const colors = ["#287b4d", "#6caf65", "#d7a539", "#cbd4cc"];
const instance = getCurrentInstance();

const chartData = computed(() => {
  const top = [...props.candidates].sort((a, b) => b.score - a.score).slice(0, 3);
  const sum = top.reduce((total, item) => total + item.score, 0);
  return [
    ...top.map((item) => ({ label: item.label_cn, score: item.score })),
    { label: "其他类别", score: Math.max(0, 1 - sum) },
  ];
});

const percentage = (value: number) => `${(value * 100).toFixed(value < 0.01 ? 1 : 0)}%`;

function drawChart() {
  const context = uni.createCanvasContext("candidate-chart", instance?.proxy);
  const center = 74;
  const radius = 62;
  let angle = -Math.PI / 2;

  chartData.value.forEach((item, index) => {
    const slice = item.score * Math.PI * 2;
    if (slice <= 0) return;
    context.beginPath();
    context.moveTo(center, center);
    context.arc(center, center, radius, angle, angle + slice);
    context.closePath();
    context.setFillStyle(colors[index]);
    context.fill();
    angle += slice;
  });

  context.beginPath();
  context.arc(center, center, 34, 0, Math.PI * 2);
  context.setFillStyle("#ffffff");
  context.fill();
  context.draw();
}

onMounted(() => nextTick(drawChart));
watch(chartData, () => nextTick(drawChart), { deep: true });
</script>

<style scoped lang="scss">
.chart-card { margin-top: 24rpx; }
.chart-layout { display: flex; align-items: center; }
.pie-canvas { flex: 0 0 296rpx; width: 296rpx; height: 296rpx; }
.legend { flex: 1; min-width: 0; margin-left: 20rpx; }
.legend-item { display: flex; align-items: center; margin: 14rpx 0; }
.legend-dot { flex: 0 0 18rpx; width: 18rpx; height: 18rpx; margin-right: 12rpx; border-radius: 50%; }
.legend-copy { display: flex; flex: 1; min-width: 0; align-items: center; justify-content: space-between; }
.legend-name { max-width: 190rpx; overflow: hidden; color: #405047; font-size: 23rpx; text-overflow: ellipsis; white-space: nowrap; }
.legend-score { margin-left: 10rpx; color: #1f3f2b; font-size: 24rpx; font-weight: 650; }
</style>
