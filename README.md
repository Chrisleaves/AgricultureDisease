# AgricultureDisease

农作物病害智能诊断项目。本仓库包含 Streamlit Web 客户端和基于 uni-app（Vue 3、TypeScript、Vite）的小程序客户端；模型服务通过独立的 HTTP API 接入，不在本仓库中运行。

## 项目结构

```text
AgricultureDisease/
├─ apps/
│  ├─ streamlit/    Streamlit Web 客户端
│  └─ miniapp/      uni-app 小程序客户端（也可编译为 H5）
├─ docs/
│  ├─ API.md                       模型服务接口约定
│  └─ MINIAPP_DEVELOPMENT_PLAN.md  小程序开发计划与背景
└─ README.md
```

两个客户端可以分别运行。小程序端目前支持单张图片诊断、模型服务地址配置、无模型预览模式、结果与本地记录、非植物图片重拍引导和拍摄指南。具体功能与配置见 [小程序端 README](apps/miniapp/README.md)。

## 快速开始

以下命令均从仓库根目录执行。

### Streamlit Web 端

```powershell
cd apps\streamlit
conda env create -f environment.yml
conda activate AgricultureDisease
python -m streamlit run app.py
```

如果 Conda 环境已创建，无需重复执行 `conda env create`。其他配置见 [Streamlit README](apps/streamlit/README.md)。

### uni-app 小程序端

```powershell
cd apps\miniapp
npm ci
npm run dev:h5
```

浏览器中的 H5 预览适合检查页面布局和基本交互。要在微信开发者工具中检查小程序渲染，请改为执行 `npm run dev:mp-weixin`，并导入 `apps/miniapp/dist/dev/mp-weixin`。详细说明见 [小程序端 README](apps/miniapp/README.md)。

目前没有配置微信 AppID；可先进行本地构建和预览，真机调试、上传或发布仍需有效 AppID、相应权限及微信平台的合法域名配置。没有模型服务时，可在应用启动页选择“暂无模型，预览模式”；预览结果是模拟数据，不代表真实诊断。

## 接口与数据

客户端按 [API 文档](docs/API.md) 对接模型服务，使用 `/health` 检查连接，使用 `/diagnose` 上传图片并获取结果。模型训练代码、数据集、大型权重和后端服务不在本仓库中。请勿把密钥、私人服务配置或真实用户图片提交到 Git。

## 版本管理

源代码、依赖锁文件和必要文档由 Git 管理；`node_modules/`、构建产物 `dist/`、本地环境文件等不提交。开发可使用功能分支，合并前分别验证受影响的客户端。
