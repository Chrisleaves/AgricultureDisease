<script setup lang="ts">
import { onLaunch } from "@dcloudio/uni-app";

onLaunch(() => {
  // Reserved for future session initialization.
});
</script>

<style lang="scss">
page {
  min-height: 100%;
  color: #1f2d24;
  background: #f4f7f4;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

button::after {
  border: 0;
}

.page-shell {
  box-sizing: border-box;
  min-height: 100vh;
  padding: 28rpx 28rpx 56rpx;
}

.surface-card {
  box-sizing: border-box;
  padding: 28rpx;
  background: #ffffff;
  border: 1rpx solid #e1e9e3;
  border-radius: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(35, 80, 52, 0.07);
}

.section-title {
  display: block;
  margin-bottom: 18rpx;
  color: #183c28;
  font-size: 32rpx;
  font-weight: 700;
}

.muted-text {
  color: #6e7d72;
  font-size: 26rpx;
  line-height: 1.65;
}

.primary-button {
  color: #ffffff;
  background: linear-gradient(135deg, #287b4d, #3b9865);
  border-radius: 18rpx;
  font-size: 30rpx;
  font-weight: 600;
}

.primary-button[disabled] {
  color: rgba(255, 255, 255, 0.78);
  background: #9eb6a6;
}

.secondary-button {
  color: #287b4d;
  background: #eaf5ee;
  border-radius: 18rpx;
  font-size: 28rpx;
}
</style>
