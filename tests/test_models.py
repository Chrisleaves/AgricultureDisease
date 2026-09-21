import unittest

from src.models import DiagnosisResult
from src.report_parser import split_report


class DiagnosisResultTests(unittest.TestCase):
    def test_parses_wrapped_api_response(self) -> None:
        result = DiagnosisResult.from_api_response(
            {
                "code": 0,
                "data": {
                    "candidates": [
                        {"label_cn": "番茄-晚疫病", "label_en": "Late blight", "score": 1.2}
                    ],
                    "classifier_top1": "番茄-晚疫病",
                    "confidence": 0.8,
                    "confidence_level": "high",
                    "vlm_report": "【最终诊断】测试",
                    "vlm_error": None,
                    "elapsed_ms": 1200,
                },
            }
        )
        self.assertEqual(result.classifier_top1, "番茄-晚疫病")
        self.assertEqual(result.candidates[0].score, 1.0)
        self.assertEqual(result.confidence_level, "high")

    def test_rejects_missing_candidates(self) -> None:
        with self.assertRaisesRegex(ValueError, "候选病害"):
            DiagnosisResult.from_api_response({"code": 0, "data": {"candidates": []}})


class ReportParserTests(unittest.TestCase):
    def test_splits_numbered_sections(self) -> None:
        sections = split_report("1.【最终诊断】晚疫病\n2.【诊断依据】水渍状病斑")
        self.assertEqual(sections, [("最终诊断", "晚疫病"), ("诊断依据", "水渍状病斑")])


if __name__ == "__main__":
    unittest.main()

