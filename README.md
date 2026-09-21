# AgricultureDisease

农作物病害智能诊断项目。本仓库采用 Monorepo 结构，同时维护 Streamlit Web 端与规划中的 uni-app 小程序端，两端共用同一套模型 API。

## 项目结构

```text
AgricultureDisease/
├─ apps/
│  ├─ streamlit/    已实现的 Streamlit Web 前端
│  └─ miniapp/      规划中的 uni-app 小程序前端
├─ docs/
│  ├─ API.md                       前后端共享接口规范
│  └─ MINIAPP_DEVELOPMENT_PLAN.md  小程序开发交接方案
├─ .gitignore
└─ README.md
```

## Streamlit Web 端

```powershell
cd apps\streamlit
conda env create -f environment.yml
conda activate AgricultureDisease
python -m streamlit run app.py
```

如果 Conda 环境已经创建，只需激活环境并运行最后一条命令。完整说明见 [`apps/streamlit/README.md`](apps/streamlit/README.md)。

## uni-app 小程序端

小程序端尚未开始构建。计划使用 Vue 3、TypeScript 与 Vite，目标优先覆盖微信小程序，并保留编译为 H5 和 App 的能力。简要说明见 [`apps/miniapp/README.md`](apps/miniapp/README.md)，完整交接方案见 [`docs/MINIAPP_DEVELOPMENT_PLAN.md`](docs/MINIAPP_DEVELOPMENT_PLAN.md)。

## 接口协作

前端与模型服务按照 [`docs/API.md`](docs/API.md) 对接。模型训练代码、数据集和大型权重不放入本仓库。

## Git 协作建议

- `main` 始终同时保留两个客户端的稳定版本。
- 新功能使用 `feature/...` 分支，修复使用 `fix/...` 分支。
- 不使用长期的 `streamlit`、`miniapp` 分支来分别保存两个程序。
- 模型文件、数据集、环境密钥和本地编辑器配置不得提交。
