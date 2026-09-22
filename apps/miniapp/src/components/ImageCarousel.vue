<template>
  <view v-if="images.length" class="carousel-wrap">
    <swiper class="carousel" :current="currentIndex" circular @change="onChange">
      <swiper-item v-for="image in images" :key="image.id">
        <view class="image-frame">
          <image class="preview-image" :src="image.path" mode="aspectFit" />
        </view>
      </swiper-item>
    </swiper>

    <view class="carousel-footer">
      <button class="nav-button" :disabled="images.length < 2" @click="move(-1)">上一张</button>
      <view class="image-meta">
        <text class="counter">{{ currentIndex + 1 }} / {{ images.length }}</text>
        <text class="file-size">{{ currentImage ? formatFileSize(currentImage.size) : "" }}</text>
      </view>
      <button class="nav-button" :disabled="images.length < 2" @click="move(1)">下一张</button>
    </view>

    <button class="remove-button" :disabled="disabled" @click="$emit('remove', currentIndex)">删除当前图片</button>
  </view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { SelectedImage } from "@/types/diagnosis";
import { formatFileSize } from "@/utils/image";

const props = defineProps<{
  images: SelectedImage[];
  currentIndex: number;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (event: "update:currentIndex", index: number): void;
  (event: "remove", index: number): void;
}>();

const currentImage = computed(() => props.images[props.currentIndex]);

function onChange(event: { detail: { current: number } }) {
  emit("update:currentIndex", event.detail.current);
}

function move(offset: number) {
  if (props.images.length < 2) return;
  const next = (props.currentIndex + offset + props.images.length) % props.images.length;
  emit("update:currentIndex", next);
}
</script>

<style scoped lang="scss">
.carousel-wrap {
  margin-top: 24rpx;
}

.carousel {
  height: 470rpx;
  overflow: hidden;
  background: #15251b;
  border-radius: 22rpx;
}

.image-frame,
.preview-image {
  width: 100%;
  height: 100%;
}

.carousel-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20rpx;
}

.nav-button {
  width: 150rpx;
  margin: 0;
  padding: 10rpx 0;
  color: #287b4d;
  background: #edf7f0;
  border-radius: 14rpx;
  font-size: 25rpx;
}

.nav-button[disabled] {
  color: #a7b1aa;
  background: #f1f3f1;
}

.image-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.counter {
  color: #24432f;
  font-size: 28rpx;
  font-weight: 700;
}

.file-size {
  margin-top: 3rpx;
  color: #829086;
  font-size: 21rpx;
}

.remove-button {
  margin-top: 18rpx;
  color: #a54335;
  background: #fff0ed;
  border-radius: 14rpx;
  font-size: 25rpx;
}
</style>
