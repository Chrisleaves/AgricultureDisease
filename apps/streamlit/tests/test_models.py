import unittest

from src.chart_data import build_candidate_distribution
from src.models import Candidate, DiagnosisResult
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


class ChartDataTests(unittest.TestCase):
    def test_adds_remaining_probability_as_other_categories(self) -> None:
        rows = build_candidate_distribution(
            [
                Candidate("候选一", "First", 0.6),
                Candidate("候选二", "Second", 0.2),
                Candidate("候选三", "Third", 0.1),
            ]
        )
        self.assertEqual(rows[-1]["label"], "其他类别")
        self.assertAlmostEqual(float(rows[-1]["score"]), 0.1)
        self.assertAlmostEqual(sum(float(row["score"]) for row in rows), 1.0)


if __name__ == "__main__":
    unittest.main()
