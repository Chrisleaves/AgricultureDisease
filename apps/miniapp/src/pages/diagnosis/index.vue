<template>
  <view class="page-shell diagnosis-page">
    <view class="hero-card">
      <view class="hero-badge">AI 作物医生</view>
      <text class="hero-title">拍一张清晰病叶，快速获得诊断建议</text>
      <text class="hero-subtitle">当前轮播中的图片将作为本次诊断图片</text>
    </view>

    <view class="surface-card upload-card">
      <view class="section-heading">
        <view>
          <text class="section-title">选择作物图片</text>
          <text class="muted-text">已选择 {{ state.images.length }} 张</text>
        </view>
        <button class="health-button" :loading="healthChecking" @click="handleHealthCheck">检查服务</button>
      </view>

      <ImageUploader :disabled="busy" :remaining="remaining" @choose="chooseImages" />

      <view v-if="!state.images.length" class="empty-preview">
        <view class="leaf-mark">叶</view>
        <text class="empty-title">还没有图片</text>
        <text class="empty-copy">请拍摄叶片正反面或从相册选择清晰照片</text>
      </view>

      <ImageCarousel
        :images="state.images"
        :current-index="state.currentIndex"
        :disabled="busy"
        @update:current-index="setCurrentIndex"
        @remove="removeImage"
      />
    </view>

    <view v-if="state.message" class="status-banner" :class="`status-${state.stage}`">
      <view v-if="busy" class="status-spinner" />
      <text>{{ state.message }}</text>
    </view>

    <button class="primary-button diagnose-button" :disabled="!currentImage || busy" :loading="busy" @click="submitDiagnosis">
      {{ busy ? "正在分析，请稍候" : "诊断当前图片" }}
    </button>

    <view v-if="!apiConfigured" class="config-notice">
      <text class="config-title">尚未配置模型服务</text>
      <text>复制 .env.example 为 .env.local，填写 VITE_API_BASE_URL 后重新启动构建。</text>
    </view>

    <view class="safety-note">
      <text class="safety-title">使用提示</text>
      <text>识别结果仅供初步参考。施药前请核对农药标签，并咨询当地农技人员。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import ImageCarousel from "@/components/ImageCarousel.vue";
import ImageUploader from "@/components/ImageUploader.vue";
import { checkHealth, diagnoseImage, getReadableError } from "@/services/diagnosis";
import { useDiagnosisStore } from "@/stores/diagnosis";
import type { SelectedImage } from "@/types/diagnosis";
import { saveDiagnosisHistory } from "@/utils/history";
import { MAX_IMAGE_COUNT, validateSelectedImage } from "@/utils/image";

const { state, appendImages, removeImage, setCurrentIndex, setStage, setResult } = useDiagnosisStore();
const healthChecking = ref(false);
const remaining = computed(() => Math.max(0, MAX_IMAGE_COUNT - state.images.length));
const currentImage = computed(() => state.images[state.currentIndex]);
const busy = computed(() => state.stage === "validating" || state.stage === "uploading");
const apiConfigured = computed(() => Boolean(import.meta.env.VITE_API_BASE_URL?.trim()));

async function validateFiles(files: Array<{ path: string; size: number }>) {
  setStage("validating", "正在检查图片…");
  const accepted: SelectedImage[] = [];
  const rejected: string[] = [];

  for (const file of files) {
    try {
      accepted.push(await validateSelectedImage(file.path, file.size));
    } catch (error) {
      rejected.push(getReadableError(error));
    }
  }

  if (accepted.length) appendImages(accepted);
  setStage("idle");

  if (rejected.length) {
    uni.showModal({
      title: "部分图片未加入",
      content: [...new Set(rejected)].join("\n"),
      showCancel: false,
    });
  }
}

function chooseImages(source: "album" | "camera") {
  uni.chooseImage({
    count: source === "camera" ? 1 : remaining.value,
    sourceType: [source],
    sizeType: ["original", "compressed"],
    success(response) {
      const rawFiles = Array.isArray(response.tempFiles) ? response.tempFiles : [response.tempFiles];
      const files = rawFiles.map((file, index) => ({
        path: "path" in file ? file.path : response.tempFilePaths[index],
        size: file.size,
      }));
      void validateFiles(files);
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
    uni.showToast({ title: response.status === "ok" ? "服务运行正常" : `服务状态：${response.status}`, icon: "none" });
  } catch (error) {
    uni.showModal({ title: "服务检查失败", content: getReadableError(error), showCancel: false });
  } finally {
    healthChecking.value = false;
  }
}

async function submitDiagnosis() {
  if (!currentImage.value || busy.value) return;
  setResult(null);
  setStage("uploading", "正在上传并分析当前图片，通常需要数秒…");

  try {
    const result = await diagnoseImage(currentImage.value.path);
    const history = saveDiagnosisHistory(result);
    setResult(result);
    setStage("success", "诊断完成");
    await uni.navigateTo({ url: `/pages/result/index?id=${encodeURIComponent(history.id)}` });
  } catch (error) {
    const message = getReadableError(error);
    setStage("error", message);
    uni.showModal({ title: "诊断未完成", content: message, showCancel: false });
  }
}
</script>

<style scoped lang="scss">
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
.config-notice,.safety-note { margin-top: 22rpx; padding: 22rpx 24rpx; border-radius: 16rpx; font-size: 24rpx; line-height: 1.65; }
.config-notice { color: #795a19; background: #fff7df; border: 1rpx solid #f0dc9f; }
.config-title,.safety-title { display: block; margin-bottom: 5rpx; font-weight: 700; }
.safety-note { color: #59675e; background: #eaf2ec; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
