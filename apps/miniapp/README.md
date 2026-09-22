# uni-app 小程序端

农作物病害智能诊断客户端，使用 uni-app、Vue 3、TypeScript 和 Vite 构建，第一目标平台为微信小程序。

## 已实现功能

- 从相册选择或调用摄像头拍摄图片
- 单张图片选择、拍摄、替换和删除
- 图片大小、格式和可解码性检查
- 模型服务健康检查及单图诊断
- 启动时填写模型 URL，或选择不上传图片的预览模式
- Top-3 候选、概率图、可信度和复核报告展示
- 诊断进度提示、非植物图片重拍引导，以及结果图片和精确诊断时间
- 网络、超时、HTTP 错误和异常响应处理
- 最近 20 条诊断记录的本地存储
- 拍摄指南、可信度说明和用药安全提示

接口实现遵循 [`../../docs/API.md`](../../docs/API.md)。

## 环境配置

应用启动后可直接在“模型接入”页面填写服务根地址，连接成功后会保存在当前设备。也可以使用环境变量提供默认地址：

```powershell
Copy-Item .env.example .env.local
```

```dotenv
VITE_API_BASE_URL=https://api.example.com
```

`.env.local` 已被仓库忽略。该变量会被编译进客户端，只能用于服务地址，不能放置密钥。

没有模型服务时选择“暂无模型，预览模式”。预览模式不会上传图片，诊断结果会明确标注为模拟数据。

目前 `src/manifest.json` 中的微信 AppID 留空，开发阶段暂时关闭域名校验。取得 AppID 后再填写，并在微信公众平台配置对应的 HTTPS request/uploadFile 合法域名；发布前必须重新启用域名校验。

## 本地开发

```powershell
npm install
npm run dev:mp-weixin
```

然后在微信开发者工具中导入 `dist/dev/mp-weixin`。没有 AppID 时可以先完成编译与代码检查，真机上传测试需要有效 AppID 和开发者权限。

H5 开发预览：

```powershell
npm run dev:h5
```

## 验证

```powershell
npm run type-check
npm run build:mp-weixin
```

生产构建产物位于 `dist/build/mp-weixin`，不会提交到 Git。
