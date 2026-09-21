from __future__ import annotations

from collections.abc import Sequence

from .models import Candidate


def build_candidate_distribution(candidates: Sequence[Candidate]) -> list[dict[str, str | float]]:
    """构造保持总概率为 100% 的候选病害分布数据。"""
    rows: list[dict[str, str | float]] = [
        {"label": candidate.label_cn, "score": candidate.score} for candidate in candidates
    ]
    remaining = max(0.0, 1.0 - sum(candidate.score for candidate in candidates))
    if remaining >= 0.001:
        rows.append({"label": "其他类别", "score": remaining})
    return rows
