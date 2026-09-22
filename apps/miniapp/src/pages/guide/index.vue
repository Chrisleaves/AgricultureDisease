<template>
  <view class="page-shell guide-page">
    <view class="guide-hero">
      <text class="guide-kicker">拍摄质量会直接影响识别结果</text>
      <text class="guide-title">这样拍，诊断更准确</text>
    </view>

    <view class="surface-card guide-card">
      <text class="section-title">拍摄建议</text>
      <view v-for="(tip, index) in photoTips" :key="tip.title" class="tip-row">
        <text class="step-number">{{ index + 1 }}</text>
        <view class="tip-copy">
          <text class="tip-title">{{ tip.title }}</text>
          <text class="muted-text">{{ tip.content }}</text>
        </view>
      </view>
    </view>

    <view class="surface-card guide-card">
      <text class="section-title">如何理解结果</text>
      <view class="confidence-guide high"><text>高可信度</text><text>特征较明确，仍建议结合田间情况核对。</text></view>
      <view class="confidence-guide medium"><text>中可信度</text><text>候选较接近，建议补拍其他叶片或不同角度。</text></view>
      <view class="confidence-guide low"><text>低可信度</text><text>不建议直接采取防治措施，应请专业人员复核。</text></view>
    </view>

    <view class="surface-card guide-card">
      <text class="section-title">支持范围与限制</text>
      <text class="body-copy">模型支持的作物和病害类别由后端模型版本决定。无法保证识别所有病害、虫害、缺素、生理性障碍或药害，也不能替代实验室检测。</text>
      <text class="body-copy">若叶片存在多个问题，建议分别拍摄典型症状，并结合植株整体、茎秆、果实和田间分布进行判断。</text>
    </view>

    <view class="warning-card">
      <text class="warning-title">用药安全</text>
      <text>不要仅凭 AI 结果混配或增加农药剂量。请使用当地登记产品，遵守标签剂量、安全间隔期与防护要求。</text>
    </view>
  </view>
</template>

<script setup lang="ts">
const photoTips = [
  { title: "保证光线自然", content: "避免过暗、强烈反光和滤镜，尽量让病斑颜色接近肉眼所见。" },
  { title: "对焦典型症状", content: "让病斑占据画面主要区域，同时保留少量健康组织作对比。" },
  { title: "保持画面干净", content: "避免手指、标签或其他叶片遮挡，不要使用严重模糊的图片。" },
  { title: "多角度补拍", content: "可添加叶片正面、背面及植株整体照片，再逐张选择诊断。" },
];
</script>

<style scoped lang="scss">
.guide-page { padding-top: 22rpx; }
.guide-hero { padding: 34rpx 30rpx; color: #fff; background: linear-gradient(135deg, #2b7450, #76a866); border-radius: 26rpx; }
.guide-kicker { display: block; color: rgba(255,255,255,.76); font-size: 23rpx; }
.guide-title { display: block; margin-top: 10rpx; font-size: 40rpx; font-weight: 750; }
.guide-card { margin-top: 22rpx; }
.tip-row { display: flex; align-items: flex-start; padding: 18rpx 0; }
.tip-row + .tip-row { border-top: 1rpx solid #edf1ee; }
.step-number { display: flex; flex: 0 0 48rpx; width: 48rpx; height: 48rpx; align-items: center; justify-content: center; margin-right: 18rpx; color: #287b4d; background: #e4f3e9; border-radius: 50%; font-size: 23rpx; font-weight: 700; }
.tip-copy { flex: 1; min-width: 0; }
.tip-title { display: block; margin-bottom: 5rpx; color: #294431; font-size: 28rpx; font-weight: 650; }
.confidence-guide { margin-top: 14rpx; padding: 18rpx 20rpx; border-radius: 14rpx; }
.confidence-guide text { display: block; font-size: 24rpx; line-height: 1.55; }
.confidence-guide text:first-child { margin-bottom: 3rpx; font-size: 27rpx; font-weight: 700; }
.high { color: #216540; background: #e7f6ec; }
.medium { color: #7b5b18; background: #fff7df; }
.low { color: #8e3d32; background: #ffede9; }
.body-copy { display: block; color: #4b5a50; font-size: 26rpx; line-height: 1.75; }
.body-copy + .body-copy { margin-top: 18rpx; }
.warning-card { margin-top: 22rpx; padding: 24rpx 26rpx; color: #704f19; background: #fff3cf; border: 1rpx solid #ead18a; border-radius: 18rpx; font-size: 25rpx; line-height: 1.7; }
.warning-title { display: block; margin-bottom: 6rpx; font-weight: 700; }
</style>
