from __future__ import annotations

import re


SECTION_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:\d+[.、．]\s*)?【([^】]+)】\s*", re.MULTILINE
)


def split_report(report: str) -> list[tuple[str, str]]:
    """把模型报告拆成可单独渲染的标题与正文；无法拆分时保留全文。"""
    matches = list(SECTION_PATTERN.finditer(report))
    if not matches:
        return [("智能诊断报告", report.strip())]

    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(report)
        content = report[start:end].strip()
        if content:
            sections.append((match.group(1).strip(), content))
    return sections or [("智能诊断报告", report.strip())]

