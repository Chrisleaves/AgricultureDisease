<template>
  <view class="custom-navbar">
    <view class="navbar-inner">
      <button class="back-settings" @click="changeModel">
        <text class="back-arrow">‹</text>
        <text>模型设置</text>
      </button>
      <text class="navbar-title">智能诊断</text>
    </view>
  </view>

  <view class="page-shell diagnosis-page">
    <view class="hero-card">
      <view class="hero-badge">{{ accessModeLabel }}</view>
      <text class="hero-title">拍一张清晰病叶，快速获得诊断建议</text>
      <text class="hero-subtitle">当前选择的图片将作为本次诊断图片</text>
    </view>

    <view class="surface-card upload-card">
      <view class="section-heading">
        <view>
          <text class="section-title">选择作物图片</text>
          <text class="muted-text">{{ state.image ? "已选择 1 张" : "尚未选择图片" }}</text>
        </view>
        <button class="health-button" :loading="healthChecking" @click="handleHealthCheck">检查服务</button>
      </view>

      <ImageUploader :disabled="busy" @choose="chooseImage" />

      <view v-if="!state.image" class="empty-preview">
        <view class="leaf-mark">叶</view>
        <text class="empty-title">还没有图片</text>
        <text class="empty-copy">请拍摄叶片正反面或从相册选择清晰照片</text>
      </view>

      <ImagePreview
        :image="state.image"
        :disabled="busy"
        @remove="clearImage"
      />
    </view>

    <view v-if="state.stage === 'uploading'" class="surface-card progress-card">
      <view class="progress-heading">
        <text class="progress-title">{{ progressLabel }}</text>
        <text class="progress-percent">{{ diagnosisProgress }}%</text>
      </view>
      <view class="diagnosis-progress-track">
        <view class="diagnosis-progress-value" :style="{ width: `${diagnosisProgress}%` }" />
      </view>
      <text class="progress-tip">模型分析可能需要数十秒，请保持页面开启</text>
    </view>

    <view v-else-if="state.message" class="status-banner" :class="`status-${state.stage}`">
      <view v-if="state.stage === 'validating'" class="status-spinner" />
      <text>{{ state.message }}</text>
    </view>

    <button
      class="primary-button diagnose-button"
      :disabled="(!currentImage && !previewMode) || busy"
      :loading="busy"
      @click="submitDiagnosis"
    >
      {{ busy ? "正在分析，请稍候" : previewMode ? "查看示例诊断" : "诊断当前图片" }}
    </button>

    <view v-if="previewMode" class="config-notice">
      <text class="config-title">当前为预览模式</text>
      <text>图片只在本机用于界面演示，不会上传；诊断结果是模拟数据，不代表真实病害判断。</text>
    </view>

    <view class="safety-note">
      <text class="safety-title">使用提示</text>
      <text>识别结果仅供初步参考。施药前请核对农药标签，并咨询当地农技人员。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import ImagePreview from "@/components/ImagePreview.vue";
import ImageUploader from "@/components/ImageUploader.vue";
import { checkHealth, diagnoseImage, getReadableError } from "@/services/diagnosis";
import { useDiagnosisStore } from "@/stores/diagnosis";
import type { SelectedImage } from "@/types/diagnosis";
import { saveDiagnosisHistory } from "@/utils/history";
import { persistSelectedImage, validateSelectedImage } from "@/utils/image";
import {
  getConfiguredApiBaseUrl,
  getModelAccessConfig,
  type ModelAccessConfig,
} from "@/utils/model-config";

const { state, setImage, clearImage, setStage, setResult } = useDiagnosisStore();
const healthChecking = ref(false);
const currentImage = computed(() => state.image);
const busy = computed(() => state.stage === "validating" || state.stage === "uploading");
const accessConfig = ref<ModelAccessConfig | null>(null);
const previewMode = computed(() => accessConfig.value?.mode === "preview");
const accessModeLabel = computed(() => previewMode.value ? "预览模式" : "AI 模型已连接");
const diagnosisProgress = ref(0);
const progressLabel = ref("正在准备诊断…");
let progressTimer: ReturnType<typeof setInterval> | undefined;

onShow(() => {
  accessConfig.value = getModelAccessConfig();
  if (!accessConfig.value && !getConfiguredApiBaseUrl()) {
    uni.reLaunch({ url: "/pages/setup/index" });
  }
});

async function validateImage(file: { path: string; size: number }) {
  setStage("validating", "正在检查图片…");
  try {
    const selected: SelectedImage = await validateSelectedImage(file.path, file.size);
    setImage(selected);
    setStage("idle");
  } catch (error) {
    setStage("idle");
    uni.showModal({
      title: "图片无法使用",
      content: getReadableError(error),
      showCancel: false,
    });
  }
}

function chooseImage(source: "album" | "camera") {
  uni.chooseImage({
    count: 1,
    sourceType: [source],
    sizeType: ["original", "compressed"],
    success(response) {
      const rawFile = Array.isArray(response.tempFiles) ? response.tempFiles[0] : response.tempFiles;
      if (!rawFile) {
        uni.showToast({ title: "未能读取图片", icon: "none" });
        return;
      }
      const file = {
        path: "path" in rawFile ? rawFile.path : response.tempFilePaths[0],
        size: rawFile.size,
      };
      void validateImage(file);
    },
    fail(error) {
      if (!error.errMsg?.includes("cancel")) {
        uni.showToast({ title: "未能读取图片", icon: "none" });
      }
    },
  });
}

async function handleHealthCheck() {
  healthChecking.value = true;
  try {
    const response = await checkHealth();
    const title = response.status === "preview"
      ? "预览模式无需连接模型"
      : response.status === "ok" ? "服务运行正常" : `服务状态：${response.status}`;
    uni.showToast({ title, icon: "none" });
  } catch (error) {
    uni.showModal({ title: "服务检查失败", content: getReadableError(error), showCancel: false });
  } finally {
    healthChecking.value = false;
  }
}

async function submitDiagnosis() {
  if ((!currentImage.value && !previewMode.value) || busy.value) return;
  setResult(null);
  setStage("uploading", previewMode.value ? "正在生成预览结果…" : "正在上传并分析当前图片，通常需要数秒…");
  startProgress();

  try {
    const sourceImagePath = currentImage.value?.path ?? "";
    const result = await diagnoseImage(sourceImagePath);
    await completeProgress();

    if (result.diagnosis_status === "need_recapture") {
      clearImage();
      setStage("idle");
      const reason = result.recapture_reason || "未识别到清晰的作物叶片，请重新拍摄。";
      await uni.navigateTo({ url: `/pages/recapture/index?reason=${encodeURIComponent(reason)}` });
      return;
    }

    const savedImagePath = sourceImagePath ? await persistSelectedImage(sourceImagePath) : "";
    const history = saveDiagnosisHistory(result, savedImagePath);
    setResult(result);
    clearImage();
    setStage("idle");
    await uni.navigateTo({ url: `/pages/result/index?id=${encodeURIComponent(history.id)}` });
  } catch (error) {
    stopProgress();
    const message = getReadableError(error);
    setStage("error", message);
    uni.showModal({ title: "诊断未完成", content: message, showCancel: false });
  }
}

function startProgress() {
  stopProgress();
  diagnosisProgress.value = 6;
  progressLabel.value = previewMode.value ? "正在生成示例结果…" : "正在上传图片…";
  progressTimer = setInterval(() => {
    const current = diagnosisProgress.value;
    if (current >= 92) return;
    diagnosisProgress.value = Math.min(92, current + Math.max(1, Math.round((92 - current) * 0.08)));
    if (diagnosisProgress.value >= 65) progressLabel.value = "多模态模型正在复核…";
    else if (diagnosisProgress.value >= 25) progressLabel.value = "分类模型正在识别…";
  }, 800);
}

function stopProgress() {
  if (progressTimer) clearInterval(progressTimer);
  progressTimer = undefined;
}

async function completeProgress() {
  stopProgress();
  diagnosisProgress.value = 100;
  progressLabel.value = "分析完成";
  await new Promise((resolve) => setTimeout(resolve, 350));
}

function changeModel() {
  uni.navigateTo({ url: "/pages/setup/index?from=settings" });
}

onUnmounted(stopProgress);
</script>

<style scoped lang="scss">
.custom-navbar { color: #fff; background: #287b4d; padding-top: var(--status-bar-height); }
.navbar-inner { position: relative; display: flex; height: 88rpx; align-items: center; justify-content: center; }
.navbar-title { font-size: 30rpx; font-weight: 700; }
.back-settings { position: absolute; left: 18rpx; display: flex; align-items: center; margin: 0; padding: 8rpx 14rpx 8rpx 6rpx; color: #fff; background: transparent; font-size: 24rpx; line-height: 1.5; }
.back-arrow { margin-right: 5rpx; font-size: 46rpx; font-weight: 300; line-height: .8; }
.diagnosis-page { padding-top: 22rpx; }
.hero-card { padding: 36rpx 32rpx 46rpx; color: #fff; background: linear-gradient(140deg, #184e34, #32865a 62%, #69a869); border-radius: 28rpx; box-shadow: 0 16rpx 36rpx rgba(25, 84, 53, 0.2); }
.hero-badge { display: inline-block; padding: 7rpx 16rpx; color: #dff5e7; background: rgba(255,255,255,.14); border: 1rpx solid rgba(255,255,255,.25); border-radius: 999rpx; font-size: 22rpx; }
.hero-title { display: block; max-width: 580rpx; margin-top: 20rpx; font-size: 42rpx; font-weight: 750; line-height: 1.38; }
.hero-subtitle { display: block; margin-top: 14rpx; color: rgba(255,255,255,.78); font-size: 24rpx; }
.upload-card { margin-top: 24rpx; }
.section-heading { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24rpx; }
.section-heading .section-title { margin-bottom: 2rpx; }
.health-button { margin: 0; padding: 10rpx 18rpx; color: #287b4d; background: transparent; border: 1rpx solid #b8d8c3; border-radius: 999rpx; font-size: 23rpx; line-height: 1.5; }
.empty-preview { display: flex; flex-direction: column; align-items: center; margin-top: 24rpx; padding: 54rpx 24rpx; background: #f8faf8; border: 2rpx dashed #cbdacf; border-radius: 22rpx; }
.leaf-mark { display: flex; width: 82rpx; height: 82rpx; align-items: center; justify-content: center; color: #5b9b6e; background: #e3f2e7; border-radius: 60% 15% 60% 15%; font-size: 30rpx; font-weight: 700; transform: rotate(-8deg); }
.empty-title { margin-top: 20rpx; color: #385442; font-size: 29rpx; font-weight: 650; }
.empty-copy { margin-top: 8rpx; color: #87938b; font-size: 23rpx; text-align: center; }
.status-banner { display: flex; align-items: center; margin-top: 22rpx; padding: 20rpx 24rpx; border-radius: 16rpx; font-size: 25rpx; }
.status-validating,.status-uploading { color: #6a541c; background: #fff7dc; }
.status-error { color: #8e3d32; background: #ffede9; }
.status-success { color: #216540; background: #e7f6ec; }
.status-spinner { width: 22rpx; height: 22rpx; margin-right: 14rpx; border: 4rpx solid rgba(105,84,28,.22); border-top-color: #8c6d21; border-radius: 50%; animation: spin .8s linear infinite; }
.diagnose-button { margin-top: 24rpx; padding: 6rpx 0; line-height: 2.6; }
.progress-card { margin-top: 22rpx; }
.progress-heading { display: flex; align-items: center; justify-content: space-between; }
.progress-title { color: #294431; font-size: 27rpx; font-weight: 650; }
.progress-percent { color: #287b4d; font-size: 27rpx; font-weight: 750; }
.diagnosis-progress-track { height: 16rpx; margin-top: 18rpx; overflow: hidden; background: #dfe9e1; border-radius: 999rpx; }
.diagnosis-progress-value { height: 100%; background: linear-gradient(90deg, #287b4d, #75ba71); border-radius: inherit; transition: width .45s ease; }
.progress-tip { display: block; margin-top: 14rpx; color: #78867c; font-size: 22rpx; }
.config-notice,.safety-note { margin-top: 22rpx; padding: 22rpx 24rpx; border-radius: 16rpx; font-size: 24rpx; line-height: 1.65; }
.config-notice { color: #795a19; background: #fff7df; border: 1rpx solid #f0dc9f; }
.config-title,.safety-title { display: block; margin-bottom: 5rpx; font-weight: 700; }
.safety-note { color: #59675e; background: #eaf2ec; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
