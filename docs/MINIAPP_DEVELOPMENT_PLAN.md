# uni-app 小程序开发方案与交接记录

本文档用于在新的开发对话中快速恢复上下文。开始工作前应先阅读本文件与同目录的 [`API.md`](API.md)。

## 1. 当前项目状态

仓库采用 Monorepo 结构：

```text
AgricultureDisease/
├─ apps/
│  ├─ streamlit/    已完成并可运行的 Streamlit Web 前端
│  └─ miniapp/      待开发的 uni-app 小程序前端
├─ docs/
│  ├─ API.md
│  └─ MINIAPP_DEVELOPMENT_PLAN.md
├─ .gitignore
└─ README.md
```

Streamlit 版本应继续保留，uni-app 是第二个客户端。两个客户端共用同一套模型 API，不使用两个长期 Git 分支分别保存。

## 2. 已确定的技术方案

| 项目 | 选择 |
|---|---|
| 跨端框架 | uni-app |
| UI 框架 | Vue 3 |
| 开发语言 | TypeScript |
| 构建工具 | Vite |
| 样式 | SCSS 或普通 CSS |
| 编辑器 | VS Code |
| 小程序调试 | 微信开发者工具 |
| 图表 | 优先选择兼容小程序的 uCharts，或使用 Canvas |
| 网络调用 | `uni.request`、`uni.uploadFile` |
| 本地存储 | `uni.setStorageSync`、`uni.getStorageSync` |

第一目标平台是微信小程序，同时保留以后编译为 H5 和 App 的可能性。

## 3. 本机环境检查结果

检查日期：2026-09-21。

| 工具 | 状态 |
|---|---|
| Node.js | 已安装，`v24.15.0` |
| npm | 已安装，`11.12.1` |
| Git | 已安装，`2.54.0.windows.1` |
| VS Code | 已安装，`1.133.0` |
| Vue (Official) 扩展 | 已安装 |
| uni-helper 扩展 | 推荐安装最上方由 `Uni Helper` 发布的扩展包，开始前复核状态 |
| 微信开发者工具 | 尚未检测到，必须安装 |
| HBuilderX | 尚未检测到，当前阶段可不安装 |

微信小程序开发还需要：

1. 微信小程序账号。
2. 小程序 AppID。
3. 当前微信号被加入项目成员，并具有开发者权限。

只开发微信小程序时，不需要 Android Studio、JDK、Flutter 或新的 Conda 环境。以后需要将 uni-app 打包为 APK 时再评估 HBuilderX 或 Android 打包环境。

## 4. 计划中的小程序目录

正式创建项目后，建议形成：

```text
apps/miniapp/
├─ src/
│  ├─ pages/
│  │  ├─ diagnosis/       智能诊断页
│  │  ├─ result/          诊断结果页
│  │  ├─ recapture/       重新拍摄引导页
│  │  ├─ history/         诊断记录页
│  │  └─ guide/           使用指南页
│  ├─ components/
│  │  ├─ ImageUploader.vue
│  │  ├─ CandidateChart.vue
│  │  ├─ ResultCard.vue
│  │  └─ ReportSections.vue
│  ├─ services/
│  │  └─ diagnosis.ts
│  ├─ types/
│  │  └─ diagnosis.ts
│  ├─ stores/
│  │  └─ diagnosis.ts
│  ├─ static/
│  ├─ App.vue
│  ├─ main.ts
│  ├─ pages.json
│  └─ manifest.json
├─ package.json
├─ vite.config.ts
└─ README.md
```

当前 `apps/miniapp/` 只有规划 README，尚未生成脚手架。不要把新项目建立到仓库外部后长期分离维护。

## 5. 页面与功能范围

### 5.1 智能诊断页

- 从相册选择图片。
- 调用手机摄像头拍摄。
- 每次只保留一张待诊断图片，重新选择时替换当前图片。
- 可删除当前图片并重新选择。
- 显示上传、推理进度、成功和失败状态。
- 后端返回 `diagnosis_status: "need_recapture"` 时进入独立重拍引导页。
- 对图片类型、大小和可解码性进行前端初步检查，后端仍需再次校验。

图片选择使用 `uni.chooseImage`，图片上传使用 `uni.uploadFile`。

### 5.2 诊断结果页

- 最终诊断名称。
- 高、中、低可信度。
- Top-3 候选及概率。
- 候选概率饼图，并显示“其他类别”的剩余概率。
- 诊断依据、防治方案和复查建议。
- 显示本次诊断使用的图片，以及精确到秒的诊断时间。
- 模型失败或大模型复核失败时的降级展示。
- 明确的农业安全与用药提示。

Streamlit 使用的 Altair 图表不能直接移植到小程序，需要使用小程序兼容图表组件或 Canvas 重写。

### 5.3 诊断记录页

第一阶段使用小程序本地存储，保存最近若干条诊断记录。以后需要跨设备同步时，再增加用户登录和数据库接口。

### 5.4 使用指南页

- 正确拍摄方法。
- 模型支持的作物和病害范围。
- 结果和可信度说明。
- 用药与专业复核提示。

## 6. 模型接口

完整定义见 [`API.md`](API.md)。核心接口保持不变：

```text
GET  /health
POST /diagnose
```

`POST /diagnose` 使用 `multipart/form-data`，图片字段名必须为 `image`。小程序侧调用形式预计为：

```ts
uni.uploadFile({
  url: `${apiBaseUrl}/diagnose`,
  filePath: currentImagePath,
  name: 'image',
  timeout: 120000
})
```

`uni.uploadFile` 返回的 `data` 可能是字符串，需要进行 `JSON.parse` 并捕获解析异常。

当前交互是单图选择、单图诊断，只上传当前选择的图片，因此现有接口不需要改成批量接口。

## 7. 当前模型联调信息

搭档曾提供临时地址：

```text
https://loose-emus-itch.loca.lt
```

2026-09-21 已实测：

- `GET /health` 返回成功。
- 分类器和大模型均为 ready。
- `POST /diagnose` 能返回现有前端可解析的 JSON。
- 一次测试推理耗时约 7.9 秒。

这是临时 LocalTunnel 地址，只能用于开发联调，不应写死到正式小程序。正式发布需要固定 HTTPS 域名，并在微信小程序后台配置 request/uploadFile 合法域名。

## 8. 正式上线前的后端要求

- 固定 HTTPS 域名。
- 微信小程序合法域名配置。
- 按部署地区要求完成域名备案。
- 用户鉴权或短期会话令牌。
- 按用户或 IP 进行限流。
- 服务端真实图片格式、尺寸和大小校验。
- 统一错误码和可展示的错误信息。
- 请求日志、请求 ID 和模型版本记录。
- 生产环境 `/health` 不暴露 GPU 型号等内部信息。

小程序内的固定密钥可以被提取，不能把长期有效的后台管理密钥直接写入前端代码。

## 9. 推荐开发顺序

1. 安装微信开发者工具并取得 AppID。
2. 复核 Node、npm 与 uni-helper 扩展状态。
3. 在 `apps/miniapp/` 中生成 Vue 3、TypeScript、Vite 版 uni-app 工程。
4. 建立 TypeScript 接口类型和 `services/diagnosis.ts`。
5. 完成单张图片的选择、替换和取消。
6. 接入 `/health` 与 `/diagnose`。
7. 完成诊断结果、进度条和概率图。
8. 完成本地诊断记录与使用指南。
9. 编译微信小程序：`npm run dev:mp-weixin`。
10. 在微信开发者工具中打开 `dist/dev/mp-weixin`。
11. 使用真机测试相册、摄像头、上传和超时处理。
12. 配置固定域名、鉴权和限流后再准备审核发布。

## 10. 第一阶段验收标准

- 项目可通过 npm 安装和构建。
- 微信开发者工具可以正常打开编译结果。
- 页面在常见手机尺寸下没有横向溢出。
- 可选择一张 JPG、PNG 或 WEBP 图片，重新选择时替换当前图片。
- 可删除当前图片，并只将当前图片上传到 `/diagnose`。
- 诊断期间显示进度提示，完成后清空诊断页图片。
- 非植物图片会进入重拍引导页，结果页显示诊断图片和精确到秒的时间。
- 能正确展示候选概率、可信度、报告和错误信息。
- 接口超时、离线、格式错误时页面不会崩溃。
- 不在仓库中提交密钥、临时域名配置、`node_modules` 或编译输出。

## 11. Git 与协作规则

- 使用 Git 管理每个可验证阶段。
- 功能开发使用 `feature/...` 分支，修复使用 `fix/...` 分支。
- `main` 同时保存 Streamlit 与 uni-app，不建立两个长期产品分支。
- 每次提交前至少执行类型检查或构建检查。
- 未经用户明确要求，不推送 GitHub。
- 不提交模型权重、数据集、密钥、临时 tunnel 配置和编辑器本地设置。
- 用户明确要求不要使用 brainstorming 技能；开发时直接依据本方案推进，遇到会改变产品方向的重大选择再询问。

## 12. 新对话建议开场指令

可以在新的对话中发送：

> 请先阅读 `docs/MINIAPP_DEVELOPMENT_PLAN.md` 和 `docs/API.md`，检查当前 Git 状态与本机开发环境，然后按照文档从 `apps/miniapp/` 的 uni-app Vue 3 + TypeScript + Vite 脚手架开始开发。使用 Git 管理，但未经我明确允许不要推送 GitHub，也不要使用 brainstorming。

开始开发前应再次确认微信开发者工具已经安装，并向用户确认是否已经取得可用的小程序 AppID。
