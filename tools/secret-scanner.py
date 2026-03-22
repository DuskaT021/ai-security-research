#!/usr/bin/env python3
"""
secret-scanner.py
Scans a local repo for hardcoded credentials and exposed API keys.

Usage:
    python secret-scanner.py --path /path/to/repo
    python secret-scanner.py --path . --output report.txt
"""

import re
import os
import argparse
from pathlib import Path
from dataclasses import dataclass

# ── Patterns ──────────────────────────────────────────────────────────────────

PATTERNS = {
    "OpenAI API Key":         r"sk-[a-zA-Z0-9]{32,}",
    "Anthropic API Key":      r"sk-ant-[a-zA-Z0-9\-_]{32,}",
    "AWS Access Key ID":      r"AKIA[0-9A-Z]{16}",
    "AWS Secret Access Key":  r"(?i)aws[_\-\s]?secret[_\-\s]?access[_\-\s]?key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}",
    "GitHub Token":           r"ghp_[a-zA-Z0-9]{36}",
    "GitHub OAuth":           r"gho_[a-zA-Z0-9]{36}",
    "Stripe Secret Key":      r"sk_live_[a-zA-Z0-9]{24,}",
    "Stripe Publishable Key": r"pk_live_[a-zA-Z0-9]{24,}",
    "Stripe Test Key":        r"sk_test_[a-zA-Z0-9]{24,}",
    "Supabase Service Key":   r"eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+",
    "Generic Secret":         r"(?i)(secret|password|passwd|api_key|apikey|access_token|auth_token)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
    "Private Key Block":      r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "Bearer Token":           r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*",
    "Basic Auth in URL":      r"https?://[^:]+:[^@]+@",
    "Hardcoded DB URL":       r"(?i)(mongodb|postgres|mysql|redis):\/\/[^:]+:[^@]+@[^\s\"']+",
}

# Extensions to scan
INCLUDE_EXTENSIONS = {
    ".js", ".ts", ".jsx", ".tsx", ".py", ".go", ".php",
    ".env", ".env.local", ".env.development", ".env.production",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".sh", ".bash", ".zsh",
}

# Paths to always skip
SKIP_DIRS = {
    "node_modules", ".git", ".next", "dist", "build",
    "__pycache__", ".venv", "venv", ".idea", ".vscode",
    "coverage", ".nyc_output",
}

SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
}

# ── Data ──────────────────────────────────────────────────────────────────────

@dataclass
class Finding:
    file: str
    line_number: int
    pattern_name: str
    line_content: str

# ── Scanner ───────────────────────────────────────────────────────────────────

def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    if path.name in SKIP_FILES:
        return True
    if path.suffix not in INCLUDE_EXTENSIONS and path.name not in {".env"}:
        return True
    return False


def scan_file(filepath: Path) -> list[Finding]:
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern_name, pattern in PATTERNS.items():
            if re.search(pattern, line):
                # Redact the actual value in output
                redacted = redact_line(line)
                findings.append(Finding(
                    file=str(filepath),
                    line_number=line_num,
                    pattern_name=pattern_name,
                    line_content=redacted.strip(),
                ))
    return findings


def redact_line(line: str) -> str:
    """Partially redact values so output is safe to share."""
    # Redact long alphanumeric strings that look like secrets
    return re.sub(
        r"([a-zA-Z0-9\-_]{6})[a-zA-Z0-9\-_]+([a-zA-Z0-9\-_]{4})",
        r"\1••••••\2",
        line,
    )


def scan_repo(root: str) -> list[Finding]:
    all_findings = []
    root_path = Path(root).resolve()

    for filepath in root_path.rglob("*"):
        if not filepath.is_file():
            continue
        if should_skip(filepath.relative_to(root_path)):
            continue
        all_findings.extend(scan_file(filepath))

    return all_findings

# ── Reporting ─────────────────────────────────────────────────────────────────

def print_report(findings: list[Finding], output_file: str | None = None):
    lines = []

    if not findings:
        lines.append("✅  No secrets found.")
    else:
        lines.append(f"\n🔐  Secret Scanner — {len(findings)} finding(s)\n")
        lines.append("=" * 70)

        grouped: dict[str, list[Finding]] = {}
        for f in findings:
            grouped.setdefault(f.pattern_name, []).append(f)

        for pattern_name, items in sorted(grouped.items()):
            lines.append(f"\n⚠️  {pattern_name} ({len(items)} occurrence(s))")
            lines.append("-" * 50)
            for item in items:
                lines.append(f"  📄 {item.file}:{item.line_number}")
                lines.append(f"     {item.line_content}")

        lines.append("\n" + "=" * 70)
        lines.append("🛑  Review each finding. Never commit secrets to version control.")
        lines.append("💡  Use environment variables or a secrets manager instead.\n")

    report = "\n".join(lines)
    print(report)

    if output_file:
        Path(output_file).write_text(report)
        print(f"📝  Report saved to {output_file}")

# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scan a repo for hardcoded secrets and exposed API keys."
    )
    parser.add_argument(
        "--path", default=".", help="Root path of the repo to scan (default: current dir)"
    )
    parser.add_argument(
        "--output", default=None, help="Optional file path to save the report"
    )
    args = parser.parse_args()

    print(f"🔍  Scanning: {Path(args.path).resolve()}")
    findings = scan_repo(args.path)
    print_report(findings, args.output)


if __name__ == "__main__":
    main()
