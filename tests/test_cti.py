import json
from pathlib import Path
import tempfile
import unittest

from sagaz.cti import CTIError, search, summary


class CTICatalogTests(unittest.TestCase):
    def test_summary_keeps_all_records_unverified(self):
        result = summary()
        self.assertEqual(result["count"], 10)
        self.assertEqual(result["status_counts"], {"unverified": 10})
        self.assertEqual(result["records"][0]["id"], "ALFA-CTI-0011")
        self.assertEqual(result["records"][-1]["title"], "Mt. Gox")

    def test_search_matches_id_name_theme_and_keyword(self):
        self.assertEqual(search("ALFA-CTI-0013")["results"][0]["title"], "Emotet")
        self.assertEqual(search("DuckHunt")["results"][0]["id"], "ALFA-CTI-0012")
        self.assertEqual(search("ransomware")["count"], 3)
        self.assertEqual(search("G0046")["results"][0]["title"], "FIN7")

    def test_search_limit_and_input_validation(self):
        self.assertEqual(search("crypto", limit=1)["count"], 1)
        for query in (None, "", " \n ", "x" * 201, "bad\x00query"):
            with self.subTest(query=query), self.assertRaises(ValueError):
                search(query)
        for limit in (True, 0, 51, "2", None):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                search("crypto", limit=limit)

    def test_search_does_not_claim_sources_or_verification(self):
        records = summary()["records"]
        self.assertTrue(all(record["status"] == "unverified" for record in records))
        self.assertEqual(search("Mt. Gox")["results"][0]["id"], "ALFA-CTI-0020")

    def test_malformed_optional_catalog_fields_raise_controlled_error(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "catalog.json"
            path.write_text(json.dumps({"records": [{"id": "x", "title": "x", "status": "unverified",
                                                        "themes": "not-a-list"}]}), encoding="utf-8")
            with self.assertRaises(CTIError):
                search("x", path=path)


if __name__ == "__main__":
    unittest.main()