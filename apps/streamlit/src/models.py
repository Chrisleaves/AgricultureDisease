from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


ConfidenceLevel = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class Candidate:
    label_cn: str
    label_en: str
    score: float

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Candidate":
        score = float(value.get("score", 0))
        return cls(
            label_cn=str(value.get("label_cn", "未知病害")),
            label_en=str(value.get("label_en", "Unknown")),
            score=max(0.0, min(score, 1.0)),
        )


@dataclass(frozen=True)
class DiagnosisResult:
    candidates: tuple[Candidate, ...]
    classifier_top1: str
    confidence: float
    confidence_level: ConfidenceLevel
    vlm_report: str | None
    vlm_error: str | None
    elapsed_ms: int

    @classmethod
    def from_api_response(cls, payload: dict[str, Any]) -> "DiagnosisResult":
        """解析后端 `{code, data}` 响应，同时兼容直接传入 data。"""
        if "code" in payload:
            if payload.get("code") != 0:
                message = payload.get("message") or payload.get("detail") or "诊断失败"
                raise ValueError(str(message))
            data = payload.get("data")
        else:
            data = payload

        if not isinstance(data, dict):
            raise ValueError("接口响应缺少 data 对象")

        raw_candidates = data.get("candidates", [])
        if not isinstance(raw_candidates, list):
            raise ValueError("接口响应中的 candidates 格式不正确")

        candidates = tuple(
            Candidate.from_dict(item) for item in raw_candidates if isinstance(item, dict)
        )
        if not candidates:
            raise ValueError("接口没有返回候选病害")

        confidence = max(0.0, min(float(data.get("confidence", 0)), 1.0))
        level = str(data.get("confidence_level", "low")).lower()
        if level not in {"high", "medium", "low"}:
            level = "low"

        return cls(
            candidates=candidates,
            classifier_top1=str(data.get("classifier_top1") or candidates[0].label_cn),
            confidence=confidence,
            confidence_level=level,  # type: ignore[arg-type]
            vlm_report=_optional_text(data.get("vlm_report")),
            vlm_error=_optional_text(data.get("vlm_error")),
            elapsed_ms=max(0, int(data.get("elapsed_ms", 0))),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

