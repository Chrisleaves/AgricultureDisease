# uni-app 小程序端

农作物病害智能诊断客户端，使用 uni-app、Vue 3、TypeScript 和 Vite 构建。当前主要面向微信小程序，同时提供 H5 开发预览；仓库不包含模型服务。

## 已实现功能

- 在“模型接入”页填写模型服务器根地址，健康检查通过后进入诊断页；也可选择“暂无模型，预览模式”。
- 从相册选择或拍摄一张图片，显示预览，并支持替换、删除及格式、大小、可解码性检查。
- 调用模型服务进行单图诊断；展示候选概率、可信度、诊断报告、诊断图片及精确到秒的时间。
- 对 `diagnosis_status: "need_recapture"` 展示重拍引导，不将其作为正常诊断结果保存。
- 诊断开始后显示模拟进度条：每次随机生成三个变速节点，约 22 秒到达 99%；若服务仍未返回则停在 99%，若提前返回则逐步加速至 100% 后跳转。百分比是等待提示，不代表模型实际处理进度。
- 最近 20 条诊断记录保存在本机；另有拍摄指南、可信度说明和用药安全提示。
- 处理连接、超时、HTTP 错误及异常响应。

接口字段与请求约定见 [API 文档](../../docs/API.md)。

## 目录说明

```text
src/
├─ pages/         模型接入、诊断、结果、重拍、记录和指南页面
├─ components/    图片选择、结果卡片、概率图和报告组件
├─ services/      健康检查与图片诊断请求
├─ stores/        本次诊断的页面间状态
├─ utils/         模型地址、图片校验和本地记录工具
├─ types/         诊断接口类型
├─ static/        页签图标、标志和首页树叶背景图
├─ pages.json     页面路由与导航配置
└─ manifest.json  应用及各平台配置
```

## 模型服务配置

启动后在“模型接入”页填写服务**根地址**，例如 `https://your-model.example.com`，不要附加 `/health` 或 `/diagnose`。客户端会请求 `GET /health`，连接成功后将地址保存在当前设备；诊断时通过 `POST /diagnose` 上传单张图片。健康检查超时为 15 秒，诊断上传超时为 120 秒。

也可复制示例环境文件，提供编译时的默认地址：

```powershell
Copy-Item .env.example .env.local
```

```dotenv
VITE_API_BASE_URL=https://your-model.example.com
```

`.env.local` 已被 Git 忽略。`VITE_` 变量会编译进客户端，只能用于公开的服务地址，不能存放密钥。临时内网穿透地址可能失效，请在使用前重新检查连接。

没有模型服务时，选择“暂无模型，预览模式”。该模式不会将图片上传到服务器，展示的诊断数据仅供界面演示。

## 本地运行与验证

在本目录 `apps/miniapp/` 执行：

```powershell
npm ci
npm run dev:h5
```

浏览器可查看 H5 布局和基本交互，但不能替代微信小程序的运行时测试。微信开发者工具的本地预览使用：

```powershell
npm run dev:mp-weixin
```

然后导入本目录生成的 `dist/dev/mp-weixin`。请不要把开发产物与 `dist/build/mp-weixin` 混用。代码检查和生产构建使用：

```powershell
npm run check
```

`check` 会依次运行 TypeScript 检查和微信小程序构建；产物位于 `dist/build/mp-weixin`，不提交到 Git。也可单独运行 `npm run type-check`、`npm run build:mp-weixin` 或 `npm run build:h5`。

目前 `src/manifest.json` 的微信 AppID 留空，开发配置暂时关闭域名校验。无 AppID 可以先进行编译和本地预览；真机调试、上传或发布需要有效 AppID、开发者权限及微信平台配置的 HTTPS `request`、`uploadFile` 合法域名，发布前应重新启用域名校验。

如果微信开发者工具显示旧页面，或出现 `true%`、按钮文字异常等热更新不同步现象，请停止旧编译进程，重新运行 `npm run dev:mp-weixin`，在开发者工具中执行“清缓存 → 全部清除”后重新编译。
