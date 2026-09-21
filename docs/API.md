# 模型诊断 API

本文档是 Streamlit Web 端、uni-app 小程序端与模型服务之间的共享接口约定。

## 基础约定

- 服务地址使用 HTTPS 根地址，例如 `https://api.example.com`。
- JSON 响应使用 UTF-8 编码。
- 概率统一使用 `0` 到 `1` 之间的小数。
- 当前接口每次诊断一张图片。
- 建议服务端在 120 秒内完成诊断。

## 健康检查

```http
GET /health
```

最低兼容响应：

```json
{
  "status": "ok"
}
```

开发环境可以额外返回分类器和大模型状态，但生产环境不应暴露不必要的硬件信息。

## 图片诊断

```http
POST /diagnose
Content-Type: multipart/form-data
```

表单字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `image` | File | 是 | JPG、JPEG、PNG 或 WEBP 图片 |

成功响应：

```json
{
  "code": 0,
  "data": {
    "candidates": [
      {
        "label_cn": "番茄-晚疫病",
        "label_en": "Tomato Late blight",
        "score": 0.82
      },
      {
        "label_cn": "番茄-早疫病",
        "label_en": "Tomato Early blight",
        "score": 0.12
      }
    ],
    "classifier_top1": "番茄-晚疫病",
    "confidence": 0.82,
    "confidence_level": "high",
    "vlm_report": "【最终诊断】……\n\n【诊断依据】……\n\n【防治方案】……\n\n【复查建议】……",
    "vlm_error": null,
    "elapsed_ms": 2350
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
|---|---|---|
| `candidates` | Array | 候选结果，不能为空 |
| `label_cn` | String | 中文类别名称 |
| `label_en` | String | 英文类别名称 |
| `score` | Number | 候选概率，范围 `0～1` |
| `classifier_top1` | String | 分类器首选结果 |
| `confidence` | Number | 首选结果置信度，范围 `0～1` |
| `confidence_level` | String | `high`、`medium` 或 `low` |
| `vlm_report` | String/null | 大模型复核报告 |
| `vlm_error` | String/null | 大模型复核失败原因 |
| `elapsed_ms` | Integer | 总耗时，单位毫秒 |

模型服务也可以直接返回 `data` 对象而不包裹 `{ "code": 0, "data": ... }`，但推荐统一使用包裹格式。

## 错误响应

接口应使用正确的 HTTP 4xx 或 5xx 状态码，并返回可以展示给用户的错误信息：

```json
{
  "detail": "图片格式不支持"
}
```

生产环境还应加入鉴权、频率限制、真实图片格式校验、文件大小限制和请求日志。
