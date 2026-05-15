import unittest
from datetime import datetime, timezone
from intune_evidence_cli.transform import build_evidence_bundle, graph_quote, normalize_managed_device, parse_include

class TransformTests(unittest.TestCase):
    def test_graph_quote_escapes_single_quote(self):
        self.assertEqual(graph_quote("Jannik's PC"), "Jannik''s PC")
    def test_normalize_managed_device_detects_stale_sync(self):
        device = {"id": "1", "deviceName": "PC-01", "lastSyncDateTime": "2026-05-01T00:00:00Z"}
        normalized = normalize_managed_device(device, now=datetime(2026, 5, 15, tzinfo=timezone.utc))
        self.assertTrue(normalized["stale_sync"])
        self.assertEqual(normalized["last_sync_age_days"], 14)
    def test_build_evidence_bundle_summarizes_items(self):
        device = {"id": "1", "deviceName": "PC-01", "complianceState": "compliant"}
        evidence = {"configuration": {"value": [{"state": "success"}]}, "compliance": {"value": [{"state": "compliant"}]}, "detected-apps": {"value": [{"displayName": "App"}]}}
        bundle = build_evidence_bundle(device, evidence)
        self.assertEqual(bundle["summary"]["detected_app_count"], 1)
        self.assertEqual(bundle["summary"]["configuration_state_counts"]["success"], 1)
    def test_parse_include_validates_values(self):
        self.assertEqual(parse_include("configuration,compliance", {"configuration", "compliance"}), ["configuration", "compliance"])
        with self.assertRaises(ValueError):
            parse_include("bad", {"configuration"})

if __name__ == "__main__":
    unittest.main()
