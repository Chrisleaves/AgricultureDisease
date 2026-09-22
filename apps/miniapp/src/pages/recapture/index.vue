<template>
  <view class="page-shell recapture-page">
    <view class="surface-card notice-card">
      <view class="notice-icon">↻</view>
      <text class="notice-title">需要重新拍摄</text>
      <text class="notice-copy">当前图片中未识别到可诊断的作物叶片。</text>
      <view class="reason-box">
        <text class="reason-label">模型提示</text>
        <text class="reason-text">{{ reason }}</text>
      </view>
    </view>

    <view class="surface-card guide-card">
      <text class="guide-title">这样拍摄更容易识别</text>
      <view v-for="(tip, index) in tips" :key="tip" class="tip-row">
        <text class="tip-index">{{ index + 1 }}</text>
        <text class="tip-text">{{ tip }}</text>
      </view>
    </view>

    <button class="primary-button action-button" :disabled="choosing" @click="chooseImage('camera')">
      重新拍摄
    </button>
    <button class="secondary-button album-button" :disabled="choosing" @click="chooseImage('album')">
      从相册重新选择
    </button>
    <button class="plain-button" @click="backToDiagnosis">稍后再拍，返回诊断页</button>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { getReadableError } from "@/services/diagnosis";
import { useDiagnosisStore } from "@/stores/diagnosis";
import { validateSelectedImage } from "@/utils/image";

const { setImage, setStage } = useDiagnosisStore();
const reason = ref("请拍摄包含清晰作物叶片的近景照片后重试。");
const choosing = ref(false);
const tips = [
  "让作物叶片完整出现在画面中央",
  "靠近叶片拍摄，并让病斑或虫害清晰可见",
  "尽量使用自然光，避免阴影、逆光和明显抖动",
];

onLoad((options) => {
  if (typeof options?.reason === "string" && options.reason) {
    reason.value = decodeURIComponent(options.reason);
  }
});

function chooseImage(source: "album" | "camera") {
  choosing.value = true;
  uni.chooseImage({
    count: 1,
    sourceType: [source],
    sizeType: ["original", "compressed"],
    async success(response) {
      try {
        const rawFile = Array.isArray(response.tempFiles) ? response.tempFiles[0] : response.tempFiles;
        if (!rawFile) throw new Error("未能读取图片");
        const path = "path" in rawFile ? rawFile.path : response.tempFilePaths[0];
        const selected = await validateSelectedImage(path, rawFile.size);
        setImage(selected);
        setStage("idle");
        await uni.switchTab({ url: "/pages/diagnosis/index" });
      } catch (error) {
        uni.showModal({ title: "图片无法使用", content: getReadableError(error), showCancel: false });
      } finally {
        choosing.value = false;
      }
    },
    fail(error) {
      choosing.value = false;
      if (!error.errMsg?.includes("cancel")) {
        uni.showToast({ title: "未能读取图片", icon: "none" });
      }
    },
  });
}

function backToDiagnosis() {
  setStage("idle");
  uni.switchTab({ url: "/pages/diagnosis/index" });
}
</script>

<style scoped lang="scss">
.recapture-page { padding-top: 30rpx; }
.notice-card { display: flex; flex-direction: column; align-items: center; padding-top: 42rpx; text-align: center; }
.notice-icon { display: flex; width: 96rpx; height: 96rpx; align-items: center; justify-content: center; color: #fff; background: #d68a35; border-radius: 50%; font-size: 54rpx; line-height: 1; }
.notice-title { margin-top: 24rpx; color: #294431; font-size: 36rpx; font-weight: 750; }
.notice-copy { margin-top: 10rpx; color: #748079; font-size: 25rpx; }
.reason-box { width: 100%; margin-top: 30rpx; padding: 22rpx 24rpx; box-sizing: border-box; color: #704f1c; background: #fff6dd; border: 1rpx solid #efd89a; border-radius: 16rpx; text-align: left; }
.reason-label { display: block; margin-bottom: 8rpx; font-size: 24rpx; font-weight: 700; }
.reason-text { font-size: 24rpx; line-height: 1.7; }
.guide-card { margin-top: 24rpx; }
.guide-title { display: block; margin-bottom: 12rpx; color: #294431; font-size: 29rpx; font-weight: 700; }
.tip-row { display: flex; align-items: flex-start; padding: 14rpx 0; }
.tip-index { display: flex; flex: 0 0 auto; width: 42rpx; height: 42rpx; align-items: center; justify-content: center; margin-right: 16rpx; color: #287b4d; background: #e6f3e9; border-radius: 50%; font-size: 22rpx; font-weight: 700; }
.tip-text { padding-top: 3rpx; color: #536159; font-size: 25rpx; line-height: 1.55; }
.action-button { margin-top: 28rpx; }
.album-button { margin-top: 18rpx; }
.plain-button { margin-top: 12rpx; color: #718078; background: transparent; font-size: 24rpx; }
</style>
