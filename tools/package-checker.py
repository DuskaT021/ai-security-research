#!/usr/bin/env python3
"""
package-checker.py
Validates AI-suggested npm and PyPI packages — checks they exist
and flags potential typosquatting by comparing against known popular packages.

Usage:
    python package-checker.py --file packages.txt
    python package-checker.py --packages numpy,requets,lodash
    python package-checker.py --file packages.txt --output report.txt
"""

import argparse
import json
import urllib.request
import urllib.error
import sys
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path

# ── Known popular packages (typosquatting targets) ────────────────────────────

POPULAR_NPM = [
    "react", "react-dom", "lodash", "express", "axios", "typescript",
    "webpack", "babel", "eslint", "prettier", "next", "vue", "angular",
    "tailwindcss", "vite", "jest", "mocha", "chai", "dotenv", "cors",
    "jsonwebtoken", "bcrypt", "mongoose", "sequelize", "prisma",
    "socket.io", "uuid", "moment", "dayjs", "zod", "yup",
]

POPULAR_PYPI = [
    "numpy", "pandas", "requests", "flask", "django", "fastapi",
    "sqlalchemy", "pytest", "boto3", "pillow", "scipy", "matplotlib",
    "tensorflow", "torch", "scikit-learn", "celery", "redis", "pydantic",
    "httpx", "aiohttp", "click", "rich", "black", "mypy", "cryptography",
    "paramiko", "fabric", "ansible", "scrapy", "beautifulsoup4",
]

# ── Types ─────────────────────────────────────────────────────────────────────

@dataclass
class PackageResult:
    name: str
    registry: str
    exists: bool
    typosquat_matches: list[str]
    status: str  # "ok" | "not_found" | "typosquat_risk"


# ── Registry checks ───────────────────────────────────────────────────────────

def check_npm(package: str) -> bool:
    url = f"https://registry.npmjs.org/{package}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        urllib.request.urlopen(req, timeout=5)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        return True  # other errors = assume exists, don't false-positive
    except Exception:
        return True


def check_pypi(package: str) -> bool:
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        urllib.request.urlopen(url, timeout=5)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        return True
    except Exception:
        return True


# ── Typosquat detection ───────────────────────────────────────────────────────

def check_typosquat(package: str, registry: str) -> list[str]:
    popular = POPULAR_NPM if registry == "npm" else POPULAR_PYPI
    # Already a known popular package — not a risk
    if package.lower() in popular:
        return []
    matches = get_close_matches(package.lower(), popular, n=3, cutoff=0.8)
    return matches


# ── Core logic ────────────────────────────────────────────────────────────────

def detect_registry(package: str) -> str:
    """Guess registry from package name conventions."""
    py_hints = ["py-", "-py", "_py", "python-"]
    for hint in py_hints:
        if hint in package.lower():
            return "pypi"
    return "npm"  # default to npm


def check_package(package: str, registry: str | None = None) -> PackageResult:
    package = package.strip()
    reg = registry or detect_registry(package)

    exists = check_npm(package) if reg == "npm" else check_pypi(package)
    typosquat_matches = check_typosquat(package, reg)

    if not exists:
        status = "not_found"
    elif typosquat_matches:
        status = "typosquat_risk"
    else:
        status = "ok"

    return PackageResult(
        name=package,
        registry=reg,
        exists=exists,
        typosquat_matches=typosquat_matches,
        status=status,
    )


# ── Reporting ─────────────────────────────────────────────────────────────────

ICONS = {"ok": "✅", "not_found": "🚨", "typosquat_risk": "⚠️"}

def print_report(results: list[PackageResult], output_file: str | None = None):
    lines = []

    ok       = [r for r in results if r.status == "ok"]
    missing  = [r for r in results if r.status == "not_found"]
    risky    = [r for r in results if r.status == "typosquat_risk"]

    lines.append(f"\n📦  Package Checker — {len(results)} package(s) checked\n")
    lines.append("=" * 70)
    lines.append(f"  ✅  Safe:              {len(ok)}")
    lines.append(f"  ⚠️   Typosquat risk:    {len(risky)}")
    lines.append(f"  🚨  Not found:         {len(missing)}")
    lines.append("=" * 70)

    if missing:
        lines.append("\n🚨  NOT FOUND — these packages don't exist on the registry")
        lines.append("-" * 50)
        for r in missing:
            lines.append(f"  {r.name}  [{r.registry}]")
            lines.append(f"  → Package does not exist. Do NOT install.")

    if risky:
        lines.append("\n⚠️   TYPOSQUAT RISK — similar to popular packages")
        lines.append("-" * 50)
        for r in risky:
            lines.append(f"  {r.name}  [{r.registry}]")
            lines.append(f"  → Closely matches: {', '.join(r.typosquat_matches)}")
            lines.append(f"  → Verify this is intentional before installing.")

    if ok:
        lines.append("\n✅  OK")
        lines.append("-" * 50)
        for r in ok:
            lines.append(f"  {r.name}  [{r.registry}]")

    lines.append("\n" + "=" * 70)
    lines.append("💡  Always verify AI-suggested packages before running npm install / pip install.\n")

    report = "\n".join(lines)
    print(report)

    if output_file:
        Path(output_file).write_text(report)
        print(f"📝  Report saved to {output_file}")


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate AI-suggested npm/PyPI packages for existence and typosquatting."
    )
    parser.add_argument("--file", help="Path to a .txt file with one package name per line")
    parser.add_argument("--packages", help="Comma-separated list of package names")
    parser.add_argument("--registry", choices=["npm", "pypi"], help="Force a specific registry")
    parser.add_argument("--output", help="Optional file path to save the report")
    args = parser.parse_args()

    if not args.file and not args.packages:
        parser.print_help()
        sys.exit(1)

    package_names = []

    if args.file:
        lines = Path(args.file).read_text().splitlines()
        package_names += [l.strip() for l in lines if l.strip() and not l.startswith("#")]

    if args.packages:
        package_names += [p.strip() for p in args.packages.split(",") if p.strip()]

    if not package_names:
        print("No packages to check.")
        sys.exit(0)

    print(f"🔍  Checking {len(package_names)} package(s)...")
    results = [check_package(p, args.registry) for p in package_names]
    print_report(results, args.output)


if __name__ == "__main__":
    main()
