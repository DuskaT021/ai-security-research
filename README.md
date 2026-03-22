# 🔐 ai-security-research

Security research focused on vulnerabilities introduced by AI-assisted and vibe-coded development.

With nearly half of all AI-generated code containing security flaws despite looking production-ready, this repo documents attack vectors, proof-of-concept demos, and test patterns — from the perspective of a QA engineer who ships security-critical software.

---

## 📂 Structure

| Folder | What's inside |
|---|---|
| [`injection/`](./injection/) | [`xss-demo/`](./injection/xss-demo/) (vulnerable UI + fix), [`sqli-demo/`](./injection/sqli-demo/) (raw vs parameterized queries) |
| [`hardcoded-secrets/`](./hardcoded-secrets/) | [`detection/`](./hardcoded-secrets/detection/) (scan scripts), [`examples/`](./hardcoded-secrets/examples/) (sanitized patterns) |
| [`broken-access-control/`](./broken-access-control/) | [`idor-demo/`](./broken-access-control/idor-demo/), [`missing-rls/`](./broken-access-control/missing-rls/) (Supabase/Postgres RLS gaps) |
| [`package-hallucination/`](./package-hallucination/) | [`scanner/`](./package-hallucination/scanner/) — verify AI-suggested packages exist; typosquatting notes |
| [`prompt-injection/`](./prompt-injection/) | [`payloads/`](./prompt-injection/payloads/) — tested strings + outcomes |
| [`mcp-attack-surface/`](./mcp-attack-surface/) | [`cves/`](./mcp-attack-surface/cves/) — CurXecute, EscapeRoute, related notes |
| [`speed-over-safety/`](./speed-over-safety/) | [`patterns/`](./speed-over-safety/patterns/) — before/after: what AI removed, what it cost |
| [`tools/`](./tools/) | Repo-wide CLI: [`secret-scanner.py`](./tools/secret-scanner.py), [`package-checker.py`](./tools/package-checker.py) |

---

## 🧪 Attack Vectors

### 💉 Injection & XSS
AI rarely suggests sanitization — it just passes the raw prop. Without explicit prompting for input handling, generated React components are routinely open to XSS.

### 🔑 Hardcoded Secrets
API keys for OpenAI, Stripe, and databases end up hardcoded in frontend JS, visible in page source. Common in vibe-coded apps where `.env` setup is skipped for speed.

### 🚪 Broken Access Control
Missing auth checks, insecure direct object references (IDOR), and client-side-only authentication account for over 60% of security issues found in AI-generated apps.

### 📦 Package Hallucination
~5% of AI-suggested packages don't exist. Attackers register malicious packages with those names — leading to automatic installation on `npm install`.

### 🧩 Prompt Injection
Malicious instructions slipped into context (via docs, filenames, or repo content) redirect AI coding tools to leak data or execute arbitrary commands.

### 🔗 MCP Attack Surface
Model Context Protocol gives agents broad access to the developer's machine. Critical CVEs found in Cursor (CurXecute) and Anthropic's MCP server (EscapeRoute) in 2025.

### ⚡ Speed-over-Safety Patterns
Agents optimized for acceptance remove validation checks, relax DB policies, or disable auth flows simply to resolve runtime errors.

---

## 🛠️ Tools

Quick-start scripts in [`tools/`](./tools/):

- **`secret-scanner.py`** — scans a local repo for hardcoded credentials and exposed API keys (placeholder CLI today; extend with real matchers)
- **`package-checker.py`** — validates AI-suggested npm/PyPI packages exist and aren't typosquatted (placeholder CLI today; add registry checks next)

```bash
# Scan a repo for secrets
python tools/secret-scanner.py --path /path/to/your/repo

# Check a list of packages
python tools/package-checker.py --file packages.txt
```

---

## 📋 How each topic is organized

Every top-level topic has a **README.md** (what you are testing, how to reproduce, what to look for, fixes). Under that, **named subfolders** hold demos, payloads, or scripts — for example `*-demo/`, `detection/`, `payloads/`, `cves/`, or `patterns/`. Names differ by topic; open each topic’s README for pointers.

```text
topic/
├── README.md
├── some-demo/       # or detection/, payloads/, cves/, patterns/, scanner/, …
└── …
```

---

## 👩‍💻 About

Built by [@DuskaT021](https://github.com/DuskaT021) — Senior QA Engineer with 6+ years in QA, 3+ years shipping security-critical blockchain software (Bitcoin wallets, Web3 infra).

> Good tests catch bugs. Good security research catches the bugs tests don't know to look for.

---

*Work in progress — findings added as I go.*
