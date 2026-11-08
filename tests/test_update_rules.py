"""Offline regression tests for mistakes that could misroute subscription traffic."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import update_rules as rules


class GeneratorTests(unittest.TestCase):
    def test_geosite_conversion_and_explicit_omissions(self):
        fixtures = {
            "root": "include:child\nfull:API.Example.com\nexample.com # note\n"
                    "regexp:.*example.*\nfull:logs.example.net @telemetry\n",
            "child": "domain:assets.example.net\n",
        }
        source = rules.DomainSource("a" * 40, lambda url: fixtures[url.rsplit("/", 1)[-1]])
        self.assertEqual(source.load("root"), {
            "DOMAIN,api.example.com", "DOMAIN-SUFFIX,example.com",
            "DOMAIN-SUFFIX,assets.example.net",
        })
        self.assertEqual(len(source.skipped), 2)

    def test_bad_domains_cannot_inject_policy_or_shared_roots(self):
        for value in ["google.com", "azure.com", "example.com,DIRECT", "*.example.com",
                      "https://example.com", "localhost", "8.8.8.8", "-bad.example.com"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                rules.domain_rule(value)

    def test_cycles_traversal_and_filtered_includes_fail(self):
        for content in ["include:root", "include:../secret", "include:child @ads"]:
            source = rules.DomainSource("a" * 40, lambda url: content)
            with self.subTest(content=content), self.assertRaises(ValueError):
                source.load("root")

    def test_unknown_syntax_fails(self):
        source = rules.DomainSource("a" * 40, lambda url: "unexpected:example.com")
        with self.assertRaises(ValueError):
            source.load("root")

    def test_claude_only_inbound_and_no_embedded_script_addresses(self):
        html = """<script>Inbound IP addresses 9.9.9.9/32 Outbound IP addresses</script>
        <h2>Inbound IP addresses</h2><h3>IPv4</h3><code>160.79.104.0/23</code>
        <h3>IPv6</h3><code>2607:6bc0::/48</code><h2>Outbound IP addresses</h2>
        <code>160.79.104.0/21</code><h2>Phased out IP addresses</h2><code>34.162.46.92/32</code>"""
        self.assertEqual(rules.claude_ranges(html), {
            "IP-CIDR,160.79.104.0/23,no-resolve", "IP-CIDR6,2607:6bc0::/48,no-resolve",
        })
        with self.assertRaises(ValueError):
            rules.claude_ranges("<html>Cloudflare challenge</html>")

    def test_voice_ipv4_and_ipv6(self):
        payload = {"prefixes": [{"ipv4Prefix": "8.8.8.8/32"}, {"ipv6Prefix": "2607:6bc0::/48"}]}
        self.assertEqual(len(rules.voice_ranges(json.dumps(payload))), 2)
        for prefixes in [[], [{"ipv4Prefix": "2607:6bc0::/48"}], [{"unknown": "8.8.8.8/32"}]]:
            with self.subTest(prefixes=prefixes), self.assertRaises(ValueError):
                rules.voice_ranges(json.dumps({"prefixes": prefixes}))

    def test_unsafe_cidrs_rejected(self):
        for value in ["0.0.0.0/0", "10.0.0.0/8", "127.0.0.1/32", "169.254.1.1/32",
                      "::/0", "fc00::/7", "160.79.104.1/23", "8.0.0.0/8"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                rules.cidr_rule(value)

    def test_large_removals_fail_even_when_total_count_is_unchanged(self):
        with self.assertRaises(ValueError):
            rules.check_removals({"A": ["old1", "old2"]}, {"A": ["new1", "new2"]})
        rules.check_removals({"A": ["a", "b", "c", "d"]}, {"A": ["a", "b", "c"]})

    def test_render_deduplicates_and_is_deterministic(self):
        categories = {"A": ["DOMAIN,x.example.com"], "B": ["DOMAIN,x.example.com"]}
        self.assertEqual(rules.render(categories).count("DOMAIN,x.example.com"), 1)
        self.assertEqual(rules.render(categories), rules.render(categories))

    def test_failed_update_preserves_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            previous = {"A": ["DOMAIN,old.example.com"]}
            (root / "AI_Models.list").write_text("last good rules\n")
            lock_text = json.dumps({"categories": previous})
            (root / "sources.lock.json").write_text(lock_text)
            scenarios = [OSError("download failed"), ({"A": []}, {"categories": {"A": []}})]
            for result in scenarios:
                options = {"side_effect": result} if isinstance(result, Exception) else {"return_value": result}
                with patch.object(rules, "ROOT", root), patch.object(sys, "argv", ["update_rules.py"]):
                    with patch.object(rules, "build", **options), self.assertRaises((OSError, ValueError)):
                        rules.main()
                self.assertEqual((root / "AI_Models.list").read_text(), "last good rules\n")
                self.assertEqual((root / "sources.lock.json").read_text(), lock_text)


if __name__ == "__main__":
    unittest.main()
