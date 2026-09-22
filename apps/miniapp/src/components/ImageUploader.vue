<template>
  <view class="uploader">
    <button class="source-button" :disabled="disabled || remaining <= 0" @click="chooseFromAlbum">
      <text class="source-icon">▧</text>
      <text>从相册选择</text>
    </button>
    <button class="source-button" :disabled="disabled || remaining <= 0" @click="takePhoto">
      <text class="source-icon">◉</text>
      <text>拍摄照片</text>
    </button>
  </view>
  <text class="uploader-tip">支持 JPG、PNG、WEBP，单张不超过 10 MB，最多 9 张</text>
</template>

<script setup lang="ts">
const props = defineProps<{
  disabled?: boolean;
  remaining: number;
}>();

const emit = defineEmits<{
  (event: "choose", source: "album" | "camera"): void;
}>();

function chooseFromAlbum() {
  if (!props.disabled && props.remaining > 0) emit("choose", "album");
}

function takePhoto() {
  if (!props.disabled && props.remaining > 0) emit("choose", "camera");
}
</script>

<style scoped lang="scss">
.uploader {
  display: flex;
  gap: 18rpx;
}

.source-button {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-width: 0;
  margin: 0;
  padding: 20rpx 12rpx;
  color: #276b46;
  background: #edf7f0;
  border-radius: 18rpx;
  font-size: 27rpx;
}

.source-button[disabled] {
  color: #9aa79e;
  background: #f1f3f1;
}

.source-icon {
  margin-right: 10rpx;
  font-size: 34rpx;
}

.uploader-tip {
  display: block;
  margin-top: 16rpx;
  color: #829086;
  font-size: 23rpx;
  line-height: 1.5;
}
</style>
