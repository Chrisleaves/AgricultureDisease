<template>
  <view v-if="image" class="preview-wrap">
    <view class="image-frame">
      <image class="preview-image" :src="image.path" mode="aspectFit" />
    </view>
    <view class="image-meta">
      <text>当前诊断图片</text>
      <text class="file-size">{{ formatFileSize(image.size) }}</text>
    </view>
    <button class="remove-button" :disabled="disabled" @click="$emit('remove')">删除图片</button>
  </view>
</template>

<script setup lang="ts">
import type { SelectedImage } from "@/types/diagnosis";
import { formatFileSize } from "@/utils/image";

defineProps<{
  image: SelectedImage | null;
  disabled?: boolean;
}>();

defineEmits<{
  (event: "remove"): void;
}>();
</script>

<style scoped lang="scss">
.preview-wrap { margin-top: 24rpx; }
.image-frame { height: 470rpx; overflow: hidden; background: #15251b; border-radius: 22rpx; }
.preview-image { width: 100%; height: 100%; }
.image-meta { display: flex; align-items: center; justify-content: space-between; margin-top: 16rpx; color: #415349; font-size: 25rpx; }
.file-size { color: #829086; font-size: 22rpx; }
.remove-button { margin-top: 16rpx; color: #a54335; background: #fff0ed; border-radius: 14rpx; font-size: 25rpx; }
</style>
