#!/usr/bin/env python3
"""从社区域名数据和官方 IP 来源生成 Rules/AI/AI.list，仅使用标准库。"""

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
# 防止整个共享平台被分流；这不是完整的公共后缀或域名归属数据库。
SHARED_ROOTS = {
    "com", "net", "org", "ai", "dev", "app", "io", "google", "cloud",
    "google.com", "googleapis.com", "googleusercontent.com", "gstatic.com",
    "cloudflare.com", "cloudflare.net", "azure.com", "azureedge.net",
    "azurefd.net", "windows.net", "amazonaws.com", "cloudfront.net",
    "githubusercontent.com", "github.com", "x.com", "livekit.cloud",
}
MAX_BYTES = 4 * 1024 * 1024


def fetch(url):
    """限制下载大小并重试网络错误；不向数据源发送凭据。"""
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0 MyRules/1.0"})
            with urlopen(request, timeout=30) as response:
                if not response.url.startswith("https://"):
                    raise ValueError("Source redirected away from HTTPS")
                data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError(f"Source exceeds {MAX_BYTES} bytes: {url}")
            return data.decode("utf-8")
        except OSError:
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
    # 同时检查网段两端，拒绝私网、默认路由和过宽的云平台网段。
    minimum = 16 if network.version == 4 else 32
    if (network.prefixlen < minimum or not network.network_address.is_global
            or not network.broadcast_address.is_global):
        raise ValueError(f"Unsafe IP range: {value}")
    kind = "IP-CIDR" if network.version == 4 else "IP-CIDR6"
    return f"{kind},{network},no-resolve"


def load_domains(revision):
    """展开同一上游版本的 include，返回规则、来源信息和跳过的条目。"""
    contents, files, skipped = {}, {}, []

    def load(name, stack=()):
        # include 只能引用上游文件名，不能是 URL 或本地路径。
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            raise ValueError(f"Invalid include: {name}")
        if name in stack or len(stack) >= 10:
            raise ValueError(f"Recursive/deep include: {name}")
        if len(files) >= 100 and name not in files:
            raise ValueError("Too many included files")
        if name not in contents:
            url = f"https://raw.githubusercontent.com/v2fly/domain-list-community/{revision}/data/{name}"
            contents[name] = fetch(url)
            files[name] = {"url": url, "sha256": digest(contents[name])}
        rules = set()
        for number, raw in enumerate(contents[name].splitlines(), 1):
            fields = raw.split("#", 1)[0].split()
            if not fields:
                continue
            token, *attributes = fields
            if any(not x.startswith("@") for x in attributes):
                raise ValueError(f"Unexpected syntax at {name}:{number}")
            if token.startswith("include:"):
                # 带属性的 include 需要过滤，不能直接导入整个类别。
                if attributes:
                    raise ValueError(f"Filtered include needs review: {name}:{number}")
                rules.update(load(token[8:], (*stack, name)))
            elif token.startswith(("regexp:", "keyword:")) or attributes:
                # 不扩大正则匹配范围；广告/遥测可能使用共享域名，记录后跳过。
                skipped.append({"file": name, "line": number, "entry": raw.strip()})
            else:
                rules.add(domain_rule(token))
        if not rules or len(rules) > 2000:
            raise ValueError(f"Unexpected domain count for {name}: {len(rules)}")
        return rules

    categories = {label: sorted(load(name)) for label, name in PROVIDERS.items()}
    return categories, dict(sorted(files.items())), skipped


class VisibleText(HTMLParser):
    """提取页面正文，避免匹配脚本内嵌的重复文档。"""
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
    # 只取入站段，避免将 MCP 出口和退役 IP 当成客户端请求目标。
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
        if set(prefix) not in ({"ipv4Prefix"}, {"ipv6Prefix"}):
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
    """任一类别超过 25% 的旧规则消失时，停止自动更新。"""
    for name, rules in previous.items():
        old = set(rules)
        removed = old - set(current.get(name, []))
        if old and len(removed) / len(old) > 0.25:
            raise ValueError(f"{name}: {len(removed)}/{len(old)} rules removed; review sources first")


def build():
    revision = json.loads(fetch(COMMIT_URL))["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Invalid upstream commit SHA")
    categories, files, skipped = load_domains(revision)
    ip_sources = []
    for label, url, parse in [
        ("ChatGPT Voice (official IPs)", VOICE_URL, voice_ranges),
        ("Claude API inbound (official IPs)", CLAUDE_URL, claude_ranges),
    ]:
        categories[label] = sorted(parse(fetch(url)))
        # IP 来源只记录规则哈希，忽略文档页面的样式等变化。
        ip_sources.append({"name": label, "url": url,
                           "rules_sha256": digest("\n".join(categories[label]))})
    return {"domain_source": "v2fly/domain-list-community", "revision": revision,
            "files": files, "ip_sources": ip_sources, "skipped": skipped,
            "categories": categories}


def render(categories):
    lines = ["# AI.list - generated by scripts/update_rules.py; DO NOT EDIT",
             "# Domain data: v2fly/domain-list-community (MIT; see THIRD_PARTY_NOTICES.md)",
             "# Official IPs: ChatGPT Voice and Claude API inbound only.",
             "# Provenance and skipped entries: sources.lock.json", ""]
    seen = set()
    for name, rules in categories.items():
        lines.append(f"# {name}")
        lines.extend(sorted(set(rules) - seen))
        seen.update(rules)
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accept-removals", action="store_true",
                        help="Bypass removal guard after manually reviewing upstream changes")
    args = parser.parse_args()
    manifest = build()
    categories = manifest["categories"]
    lock_path = ROOT / "sources.lock.json"
    if lock_path.exists() and not args.accept_removals:
        check_removals(json.loads(lock_path.read_text(encoding="utf-8"))["categories"], categories)
    # 全部数据通过校验后才写入。Actions 仅在脚本成功时提交发布。
    outputs = {ROOT / "Rules" / "AI" / "AI.list": render(categories),
               lock_path: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"}
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
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
