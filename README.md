# 叶知 · 农作物病害诊断前端

基于 Streamlit 的农作物病害诊断展示端。当前可使用内置 Mock 数据独立开发和演示；模型服务完成后，可切换为 FastAPI 真实接口。

## 功能

- 上传叶片图片或调用设备摄像头拍摄
- 使用饼图和进度条展示 Top-3 候选、剩余概率、置信度和诊断耗时
- 分区展示最终诊断、诊断依据、防治方案和复查建议
- 大模型失败时降级展示分类候选
- 当前会话内保存最近 20 条诊断记录
- 支持 Mock/真实接口一键切换和服务健康检查
- 针对桌面与手机浏览器进行响应式布局

## 本地运行

项目使用独立的 Conda 环境 `AgricultureDisease`（Python 3.11）：

```powershell
cd AgricultureDisease
conda create -n AgricultureDisease python=3.11 -y
conda activate AgricultureDisease
python -m pip install -r requirements.txt
streamlit run app.py
```

也可以使用仓库内的环境声明一次创建：

```powershell
conda env create -f environment.yml
conda activate AgricultureDisease
```

打开浏览器显示的本地地址。默认处于“演示模式”，不需要后端即可体验完整流程。

## 接入模型接口

接口应遵循项目根目录 `API.md` 的约定：

- `GET /health`
- `POST /diagnose`
- 上传格式为 `multipart/form-data`
- 图片字段名为 `image`
- 响应格式为 `{ "code": 0, "data": { ... } }`

复制配置模板：

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

然后填写内网穿透后的 HTTPS 根地址：

```toml
DIAGNOSIS_API_URL = "https://your-tunnel.example.com"
DIAGNOSIS_API_TIMEOUT = 120
```

也可以使用环境变量：

```powershell
$env:DIAGNOSIS_API_URL = "https://your-tunnel.example.com"
streamlit run app.py
```

启动页面后，在侧边栏把“运行模式”切换为“真实接口”，可先点击“检查服务连接”。

## 测试

```powershell
conda run -n AgricultureDisease python -m unittest discover -s tests -v
```

## 目录说明

```text
app.py                    Streamlit 页面入口
assets/styles.css         页面视觉样式
src/chart_data.py         候选概率图表数据整理
src/config.py             环境变量和 secrets 配置
src/diagnosis_service.py  Mock 与真实 HTTP 调用
src/models.py             接口数据模型及校验
src/report_parser.py      诊断报告分段渲染
tests/                    不依赖模型的单元测试
```

## 注意

- 内网穿透地址应尽量使用 HTTPS。
- 不要把 `.streamlit/secrets.toml` 提交到 Git。
- 当前历史记录仅保存在 Streamlit 会话中；如需跨设备或长期保存，后续接入 SQLite/数据库。
- AI 诊断和农药建议仅供辅助参考，正式用药前必须核对登记信息并咨询当地农技人员。
