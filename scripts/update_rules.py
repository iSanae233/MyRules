#!/usr/bin/env python3
"""Generate a Loon subscription from versioned domain data and official IP feeds.

Only Python's standard library is needed. Remote content is parsed as data, never
executed. All sources must pass validation before either tracked output is written.
"""

import argparse
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = {
    "ChatGPT / OpenAI": "openai",
    "Gemini / Google AI": "google-gemini",
    "Claude / Anthropic": "anthropic",
    "Grok / xAI": "xai",
    "Perplexity": "perplexity",
    "Groq": "groq",
    "GitHub Copilot": "github-copilot",
}
VOICE_URL = "https://openai.com/chatgpt-voice.json"
CLAUDE_URL = "https://platform.claude.com/docs/en/api/ip-addresses"
COMMIT_URL = "https://api.github.com/repos/v2fly/domain-list-community/commits/master"
# Entire shared platforms would route unrelated apps. Add narrowly scoped hosts
# instead; this is a guardrail, not a complete public suffix or ownership database.
SHARED_ROOTS = {
    "com", "net", "org", "ai", "dev", "app", "io", "google", "cloud",
    "google.com", "googleapis.com", "googleusercontent.com", "gstatic.com",
    "cloudflare.com", "cloudflare.net", "azure.com", "azureedge.net",
    "azurefd.net", "windows.net", "amazonaws.com", "cloudfront.net",
    "githubusercontent.com", "github.com", "x.com", "livekit.cloud",
}
MAX_BYTES = 4 * 1024 * 1024


def fetch(url):
    """Bound downloads and retry transient network failures without credentials."""
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 MyLoonRules/1.0"})
            with urlopen(request, timeout=30) as response:
                if not response.url.startswith("https://"):
                    raise ValueError("Source redirected away from HTTPS")
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError(f"Source exceeds {MAX_BYTES} bytes: {url}")
            return data.decode("utf-8")
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def domain_rule(token):
    kind = "DOMAIN-SUFFIX"
    if token.startswith("full:"):
        kind, token = "DOMAIN", token[5:]
    elif token.startswith("domain:"):
        token = token[7:]
    token = token.lower().rstrip(".")
    labels = token.split(".")
    if (len(token) > 253 or len(labels) < 2 or token in SHARED_ROOTS
            or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", x)
                   for x in labels)):
        raise ValueError(f"Invalid or overly broad domain: {token!r}")
    try:
        ipaddress.ip_address(token)
    except ValueError:
        return f"{kind},{token}"
    raise ValueError(f"IP literal in domain source: {token}")


def cidr_rule(value):
    network = ipaddress.ip_network(value, strict=True)
    # Official service feeds should never contain LAN, default-route or very
    # broad cloud ranges. Check both endpoints, not just the network address.
    minimum = 16 if network.version == 4 else 32
    if (network.prefixlen < minimum or not network.network_address.is_global
            or not network.broadcast_address.is_global):
        raise ValueError(f"Unsafe IP range: {value}")
    kind = "IP-CIDR" if network.version == 4 else "IP-CIDR6"
    return f"{kind},{network},no-resolve"


class DomainSource:
    def __init__(self, revision, loader=fetch):
        self.revision = revision
        self.loader = loader
        self.files = {}
        self.skipped = []

    def load(self, name, stack=()):
        # Includes are file identifiers, never arbitrary URLs or filesystem paths.
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            raise ValueError(f"Invalid include: {name}")
        if name in stack or len(stack) >= 10:
            raise ValueError(f"Recursive/deep include: {name}")
        if len(self.files) >= 100 and name not in self.files:
            raise ValueError("Too many included files")
        url = f"https://raw.githubusercontent.com/v2fly/domain-list-community/{self.revision}/data/{name}"
        if name not in self.files:
            content = self.loader(url)
            self.files[name] = {"url": url, "sha256": digest(content), "content": content}
        rules = set()
        for number, raw in enumerate(self.files[name]["content"].splitlines(), 1):
            fields = raw.split("#", 1)[0].split()
            if not fields:
                continue
            token, *attributes = fields
            if any(not x.startswith("@") for x in attributes):
                raise ValueError(f"Unexpected syntax at {name}:{number}")
            if token.startswith("include:"):
                # Attribute-filtered includes have different semantics; fail rather
                # than silently importing the whole category or guessing a filter.
                if attributes:
                    raise ValueError(f"Filtered include needs review: {name}:{number}")
                rules.update(self.load(token[8:], (*stack, name)))
            elif token.startswith(("regexp:", "keyword:")) or attributes:
                # Loon has no equivalent for every geosite expression. Telemetry
                # and ads can also use shared hosts. Keep an audit trail of omissions.
                self.skipped.append({"file": name, "line": number, "entry": raw.strip()})
            else:
                rules.add(domain_rule(token))
        if not rules or len(rules) > 2000:
            raise ValueError(f"Unexpected domain count for {name}: {len(rules)}")
        return rules


class VisibleText(HTMLParser):
    """Read document text without accidentally matching embedded JS/JSON copies."""
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


def claude_ranges(html):
    parser = VisibleText()
    parser.feed(html)
    text = "\n".join(parser.parts)
    # Direction matters: outbound/MCP and phased-out addresses are NOT endpoints
    # for a user's Claude requests. A changed heading must fail the update.
    section = re.search(r"Inbound IP addresses\s+(.*?)\s+Outbound IP addresses", text, re.S)
    if not section:
        raise ValueError("Claude inbound/outbound section boundaries not found")
    ranges = re.findall(r"(?<![\w:])([0-9a-fA-F:.]+/\d{1,3})(?!\w)", section[1])
    rules = {cidr_rule(x) for x in ranges}
    if not 1 <= len(rules) <= 50:
        raise ValueError("Unexpected Claude inbound IP count")
    return rules


def voice_ranges(content):
    prefixes = json.loads(content)["prefixes"]
    rules = set()
    for prefix in prefixes:
        if len(prefix) != 1 or next(iter(prefix)) not in {"ipv4Prefix", "ipv6Prefix"}:
            raise ValueError(f"Unexpected voice prefix format: {prefix!r}")
        key, value = next(iter(prefix.items()))
        if ipaddress.ip_network(value).version != (4 if key == "ipv4Prefix" else 6):
            raise ValueError("Voice prefix address family mismatch")
        rules.add(cidr_rule(value))
    if not 1 <= len(rules) <= 5000:
        raise ValueError("Unexpected ChatGPT Voice IP count")
    return rules


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_removals(previous, current):
    """Require maintainer review when over 25% of a category disappears."""
    for name, rules in previous.items():
        old = set(rules)
        removed = old - set(current.get(name, []))
        if old and len(removed) / len(old) > 0.25:
            raise ValueError(f"{name}: {len(removed)}/{len(old)} rules removed; review sources first")


def build():
    revision = json.loads(fetch(COMMIT_URL))["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Invalid upstream commit SHA")
    source = DomainSource(revision)
    categories = {label: sorted(source.load(name)) for label, name in PROVIDERS.items()}
    ip_sources = []
    for label, url, parse in [
        ("ChatGPT Voice (official IPs)", VOICE_URL, voice_ranges),
        ("Claude API inbound (official IPs)", CLAUDE_URL, claude_ranges),
    ]:
        content = fetch(url)
        categories[label] = sorted(parse(content))
        # For HTML, hash the extracted rules: cosmetic site changes should not
        # create commits. Domain files retain their exact input hashes below.
        ip_sources.append({"name": label, "url": url,
                           "rules_sha256": digest("\n".join(categories[label]))})
    manifest = {"domain_source": "v2fly/domain-list-community", "revision": revision,
                "files": {name: {k: v for k, v in record.items() if k != "content"}
                          for name, record in sorted(source.files.items())},
                "ip_sources": ip_sources, "skipped": source.skipped,
                "categories": categories}
    return categories, manifest


def render(categories):
    lines = ["# AI_Models.list - generated by scripts/update_rules.py; DO NOT EDIT",
             "# Domain data: v2fly/domain-list-community (MIT; see THIRD_PARTY_NOTICES.md)",
             "# Official IPs: ChatGPT Voice and Claude API inbound only.",
             "# Provenance and skipped entries: sources.lock.json", ""]
    seen = set()
    for name, rules in categories.items():
        lines.append(f"# {name}")
        for rule in sorted(rules):
            if rule not in seen:
                lines.append(rule)
                seen.add(rule)
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accept-removals", action="store_true",
                        help="Bypass removal guard after manually reviewing upstream changes")
    args = parser.parse_args()
    categories, manifest = build()
    lock_path = ROOT / "sources.lock.json"
    if lock_path.exists() and not args.accept_removals:
        check_removals(json.loads(lock_path.read_text())["categories"], categories)
    # Stage both complete outputs before replacing either file. GitHub only
    # commits if this process succeeds; failures leave the published list intact.
    outputs = {ROOT / "AI_Models.list": render(categories),
               lock_path: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"}
    for path, text in outputs.items():
        path.with_suffix(path.suffix + ".tmp").write_text(text, encoding="utf-8")
    for path in outputs:
        path.with_suffix(path.suffix + ".tmp").replace(path)
    for name, rules in categories.items():
        print(f"{name}: {len(rules)} rules")
    print(f"Skipped {len(manifest['skipped'])} expressions; see sources.lock.json")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Update failed: {error}", file=sys.stderr)
        sys.exit(1)
