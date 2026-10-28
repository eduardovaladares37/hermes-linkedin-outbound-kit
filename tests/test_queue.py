import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "queue.py"
spec = importlib.util.spec_from_file_location("queue", SCRIPT)
assert spec is not None and spec.loader is not None
queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue)


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write("candidates.csv", queue.CANDIDATE_FIELDS, [
            ["Alpha", "alpha.example", "Ana", "CEO", "https://www.linkedin.com/in/ana/", "https://alpha.example/team", "5", "Cargo confirmado", "Site"],
            ["Alpha", "alpha.example", "Bia", "COO", "https://www.linkedin.com/in/bia/", "https://alpha.example/team", "4", "Cargo confirmado", "Site"],
            ["Beta", "beta.example", "Caio", "CEO", "https://www.linkedin.com/in/caio/", "https://beta.example/team", "2", "Baixa aderência", "Site"],
            ["Gama", "gama.example", "Dani", "CEO", "https://www.linkedin.com/in/dani/", "https://gama.example/team", "4", "Cargo confirmado", "Site"],
            ["Delta", "delta.example", "Eva", "CEO", "https://www.linkedin.com/in/eva/", "https://delta.example/team", "5", "Cargo confirmado", "Site"],
            ["Falso", "fake.example", "Zé", "CEO", "https://not-linkedin.example/in/ze/", "https://fake.example/team", "4", "Cargo confirmado", "Site"],
        ])
        self.write("ledger.csv", queue.LEDGER_FIELDS, [["https://www.linkedin.com/in/dani/", "connection_sent", "2026-01-01", ""]])
        self.write("exclusions.csv", queue.EXCLUSION_FIELDS, [["domain", "delta.example", "cliente"]])

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, filename, fields, rows):
        with (self.root / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(fields)
            writer.writerows(rows)

    def test_prepare_deduplicates_filters_and_writes_queue(self):
        result, counts = queue.prepare(self.root)
        self.assertEqual([r["name"] for r in result], ["Ana"])
        self.assertEqual(counts, {"already_contacted_or_excluded": 2, "duplicate": 1, "needs_verification": 1, "low_score": 1})
        self.assertEqual(len(queue.read_rows(self.root / "review_queue.csv", queue.CANDIDATE_FIELDS)), 1)

    def test_record_is_idempotent_and_then_excludes(self):
        url = "https://www.linkedin.com/in/ana/?trk=test"
        self.assertTrue(queue.record(self.root, url, "connection_sent", "confirmação manual"))
        self.assertFalse(queue.record(self.root, url, "connection_sent", "repetido"))
        self.assertEqual(len(queue.read_rows(self.root / "ledger.csv", queue.LEDGER_FIELDS)), 2)
        result, _ = queue.prepare(self.root)
        self.assertFalse(result)

    def test_rejects_non_profile_urls(self):
        for url in ("http://www.linkedin.com/in/ana/", "https://linkedin.com/company/alpha/", "https://evil.example/in/ana/"):
            self.assertFalse(queue.profile_url(url))
            with self.assertRaises(ValueError):
                queue.record(self.root, url, "connection_sent", "")

    def test_missing_file_is_explicit_error(self):
        (self.root / "candidates.csv").unlink()
        with self.assertRaisesRegex(ValueError, "Arquivo ausente"):
            queue.prepare(self.root)


if __name__ == "__main__":
    unittest.main()
