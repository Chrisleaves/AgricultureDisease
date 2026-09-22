<template>
  <view class="setup-page">
    <view class="brand-block">
      <view class="brand-mark"><text>叶</text></view>
      <text class="brand-kicker">AGRICULTURE AI</text>
      <text class="brand-title">农作物病害智能诊断</text>
      <text class="brand-subtitle">连接你的模型服务，或先进入预览模式体验完整流程</text>
    </view>

    <view class="access-card">
      <text class="card-title">接入模型</text>
      <text class="field-label">模型服务 URL</text>
      <view class="url-field" :class="{ focused: inputFocused }">
        <text class="protocol-mark">↗</text>
        <input
          v-model="modelUrl"
          class="url-input"
          type="text"
          placeholder="https://your-model.example.com"
          placeholder-class="input-placeholder"
          :disabled="connecting"
          :maxlength="300"
          @focus="inputFocused = true"
          @blur="inputFocused = false"
        />
        <text v-if="modelUrl" class="clear-input" @click="modelUrl = ''">×</text>
      </view>
      <text class="field-help">请填写模型服务器根节点</text>

      <view v-if="statusMessage" class="connection-status" :class="statusType">
        <text>{{ statusMessage }}</text>
      </view>

      <button class="primary-button connect-button" :loading="connecting" :disabled="connecting || !modelUrl.trim()" @click="connectModel">
        {{ connecting ? "正在检测连接" : "连接模型并进入" }}
      </button>

      <view class="divider"><view /><text>或者</text><view /></view>

      <button class="preview-button" :disabled="connecting" @click="enterPreview">
        <view class="preview-icon">◇</view>
        <view class="preview-copy">
          <text class="preview-title">暂无模型，预览模式</text>
          <text class="preview-description">使用清晰标注的模拟结果体验页面，不会上传图片</text>
        </view>
        <text class="preview-arrow">›</text>
      </button>
    </view>

    <button v-if="openedFromSettings" class="cancel-button" @click="cancelSettings">保留当前设置并返回</button>

    <view class="privacy-note">
      <text class="shield">✓</text>
      <text>模型地址只保存在当前设备。预览模式不会向任何服务器发送图片。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { checkHealthAtUrl, getReadableError } from "@/services/diagnosis";
import {
  getModelAccessConfig,
  saveApiModelConfig,
  savePreviewModelConfig,
} from "@/utils/model-config";

const modelUrl = ref("");
const inputFocused = ref(false);
const connecting = ref(false);
const statusMessage = ref("");
const statusType = ref<"status-success" | "status-error" | "">("");
const openedFromSettings = ref(false);

onLoad((options) => {
  openedFromSettings.value = options?.from === "settings";
  const saved = getModelAccessConfig();
  if (saved?.mode === "api") modelUrl.value = saved.baseUrl;
});

function enterApp() {
  uni.switchTab({ url: "/pages/diagnosis/index" });
}

async function connectModel() {
  if (!modelUrl.value.trim() || connecting.value) return;
  connecting.value = true;
  statusMessage.value = "正在请求健康检查接口…";
  statusType.value = "";

  try {
    const health = await checkHealthAtUrl(modelUrl.value);
    const config = saveApiModelConfig(modelUrl.value);
    modelUrl.value = config.baseUrl;
    statusMessage.value = `连接成功，服务状态：${health.status}`;
    statusType.value = "status-success";
    setTimeout(enterApp, 450);
  } catch (error) {
    statusMessage.value = getReadableError(error);
    statusType.value = "status-error";
  } finally {
    connecting.value = false;
  }
}

function enterPreview() {
  savePreviewModelConfig();
  uni.showToast({ title: "已进入预览模式", icon: "none" });
  enterApp();
}

function cancelSettings() {
  enterApp();
}
</script>

<style scoped lang="scss">
.setup-page {
  box-sizing: border-box;
  min-height: 100vh;
  padding: calc(54rpx + var(--status-bar-height)) 30rpx 50rpx;
  background:
    radial-gradient(circle at 90% 4%, rgba(117, 183, 120, 0.2), transparent 30%),
    linear-gradient(160deg, #f7fbf7 0%, #eef5ef 100%);
}

.brand-block { display: flex; flex-direction: column; align-items: center; text-align: center; }
.brand-mark { display: flex; width: 104rpx; height: 104rpx; align-items: center; justify-content: center; color: #fff; background: linear-gradient(145deg, #1e6d43, #68ad6c); border-radius: 66% 24% 66% 24%; box-shadow: 0 14rpx 32rpx rgba(39, 123, 77, .24); transform: rotate(-8deg); }
.brand-mark text { font-size: 38rpx; font-weight: 750; transform: rotate(8deg); }
.brand-kicker { margin-top: 24rpx; color: #639075; font-size: 20rpx; font-weight: 700; letter-spacing: 5rpx; }
.brand-title { margin-top: 10rpx; color: #173b27; font-size: 42rpx; font-weight: 780; }
.brand-subtitle { max-width: 590rpx; margin-top: 12rpx; color: #728078; font-size: 25rpx; line-height: 1.65; }

.access-card { margin-top: 38rpx; padding: 34rpx 30rpx; background: rgba(255,255,255,.96); border: 1rpx solid #e0e9e2; border-radius: 28rpx; box-shadow: 0 16rpx 44rpx rgba(30, 77, 47, .1); }
.card-title { display: block; color: #1c402b; font-size: 34rpx; font-weight: 750; }
.field-label { display: block; margin-top: 28rpx; margin-bottom: 12rpx; color: #405448; font-size: 25rpx; font-weight: 650; }
.url-field { display: flex; height: 92rpx; align-items: center; padding: 0 22rpx; background: #f6f9f6; border: 2rpx solid #dce7df; border-radius: 18rpx; transition: border-color .2s, box-shadow .2s; }
.url-field.focused { border-color: #39895b; box-shadow: 0 0 0 6rpx rgba(57,137,91,.09); }
.protocol-mark { margin-right: 14rpx; color: #468d61; font-size: 32rpx; }
.url-input { flex: 1; min-width: 0; height: 100%; color: #263b2d; font-size: 27rpx; }
.input-placeholder { color: #9ca8a0; }
.clear-input { display: flex; width: 44rpx; height: 44rpx; align-items: center; justify-content: center; color: #8b9890; background: #e8eeea; border-radius: 50%; font-size: 30rpx; }
.field-help { display: block; margin-top: 11rpx; color: #89968d; font-size: 22rpx; line-height: 1.5; }
.connection-status { margin-top: 18rpx; padding: 16rpx 18rpx; color: #5d6a61; background: #f0f3f1; border-radius: 12rpx; font-size: 23rpx; line-height: 1.5; }
.connection-status.status-success { color: #20663e; background: #e4f5e9; }
.connection-status.status-error { color: #913f34; background: #ffebe7; }
.connect-button { margin-top: 24rpx; padding: 5rpx 0; line-height: 2.7; }

.divider { display: flex; align-items: center; margin: 28rpx 0; }
.divider view { flex: 1; height: 1rpx; background: #e5ebe6; }
.divider text { margin: 0 18rpx; color: #9aa59d; font-size: 22rpx; }
.preview-button { display: flex; width: 100%; align-items: center; margin: 0; padding: 22rpx; color: #294432; background: #f0f7f2; border: 1rpx solid #d7e9dc; border-radius: 18rpx; text-align: left; line-height: 1.4; }
.preview-icon { display: flex; flex: 0 0 58rpx; width: 58rpx; height: 58rpx; align-items: center; justify-content: center; color: #287b4d; background: #dcefe2; border-radius: 16rpx; font-size: 34rpx; }
.preview-copy { flex: 1; min-width: 0; margin-left: 16rpx; }
.preview-title,.preview-description { display: block; }
.preview-title { font-size: 27rpx; font-weight: 700; }
.preview-description { margin-top: 4rpx; color: #748379; font-size: 21rpx; }
.preview-arrow { margin-left: 10rpx; color: #659276; font-size: 40rpx; }

.cancel-button { margin-top: 22rpx; color: #557060; background: transparent; font-size: 25rpx; }
.privacy-note { display: flex; max-width: 620rpx; align-items: flex-start; justify-content: center; margin: 28rpx auto 0; color: #77857b; font-size: 22rpx; line-height: 1.55; }
.shield { flex-shrink: 0; margin-right: 10rpx; color: #39895b; font-weight: 700; }
</style>
