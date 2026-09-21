from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

import requests

from .models import DiagnosisResult


class DiagnosisError(RuntimeError):
    """可安全展示给用户的诊断服务异常。"""


class DiagnosisService(Protocol):
    def diagnose(self, image_bytes: bytes, filename: str, mime_type: str) -> DiagnosisResult:
        ...


@dataclass(frozen=True)
class ApiDiagnosisService:
    base_url: str
    timeout: int = 120

    def health(self) -> dict:
        try:
            response = requests.get(f"{self.base_url.rstrip('/')}/health", timeout=8)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            raise DiagnosisError(f"无法连接诊断服务：{exc}") from exc

    def diagnose(self, image_bytes: bytes, filename: str, mime_type: str) -> DiagnosisResult:
        endpoint = f"{self.base_url.rstrip('/')}/diagnose"
        files = {"image": (filename, image_bytes, mime_type or "image/jpeg")}
        try:
            response = requests.post(endpoint, files=files, timeout=self.timeout)
        except requests.Timeout as exc:
            raise DiagnosisError("诊断超时，请稍后重试或检查模型服务是否已启动。") from exc
        except requests.RequestException as exc:
            raise DiagnosisError(f"无法连接诊断服务：{exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise DiagnosisError(f"服务返回了无法解析的内容（HTTP {response.status_code}）。") from exc

        if not response.ok:
            message = payload.get("detail") if isinstance(payload, dict) else None
            raise DiagnosisError(str(message or f"诊断请求失败（HTTP {response.status_code}）"))

        try:
            return DiagnosisResult.from_api_response(payload)
        except (TypeError, ValueError) as exc:
            raise DiagnosisError(f"诊断结果格式不正确：{exc}") from exc


class MockDiagnosisService:
    def diagnose(self, image_bytes: bytes, filename: str, mime_type: str) -> DiagnosisResult:
        del image_bytes, filename, mime_type
        time.sleep(0.7)
        return DiagnosisResult.from_api_response(
            {
                "code": 0,
                "data": {
                    "candidates": [
                        {
                            "label_cn": "番茄-晚疫病",
                            "label_en": "Tomato Late blight",
                            "score": 0.6019,
                        },
                        {
                            "label_cn": "番茄-早疫病",
                            "label_en": "Tomato Early blight",
                            "score": 0.1994,
                        },
                        {
                            "label_cn": "马铃薯-晚疫病",
                            "label_en": "Potato Late blight",
                            "score": 0.0876,
                        },
                    ],
                    "classifier_top1": "番茄-晚疫病",
                    "confidence": 0.6019,
                    "confidence_level": "medium",
                    "vlm_report": (
                        "【最终诊断】采信候选 1，初步判断为番茄晚疫病。\n\n"
                        "【诊断依据】叶片可见不规则水渍状病斑，边缘颜色较深，形态与晚疫病特征较吻合。\n\n"
                        "【防治方案】及时摘除重病叶并带离田间；改善通风，避免叶面长时间积水。"
                        "用药前请核对当地登记作物、标签剂量和安全间隔期，并咨询当地农技人员。\n\n"
                        "【复查建议】3～5 天后在相同光照下重新拍摄，对比病斑是否继续扩展。"
                    ),
                    "vlm_error": None,
                    "elapsed_ms": 6820,
                },
            }
        )

