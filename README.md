# 🔐 ai-security-research

Security research focused on vulnerabilities introduced by AI-assisted and vibe-coded development.

With nearly half of all AI-generated code containing security flaws despite looking production-ready, this repo documents attack vectors, proof-of-concept demos, and test patterns — from the perspective of a QA engineer who ships security-critical software.

---

## 📂 Structure

| Folder | What's inside |
|---|---|
| [`injection/`](./injection/) | XSS and SQLi demos — vulnerable component + fix |
| [`hardcoded-secrets/`](./hardcoded-secrets/) | Detection scripts + real-world patterns |
| [`broken-access-control/`](./broken-access-control/) | IDOR demos, missing RLS, client-side-only auth |
| [`package-hallucination/`](./package-hallucination/) | Scanner for AI-suggested packages that don't exist |
| [`prompt-injection/`](./prompt-injection/) | Tested payloads + outcomes across AI coding tools |
| [`mcp-attack-surface/`](./mcp-attack-surface/) | MCP CVEs, broad agent access risks |
| [`speed-over-safety/`](./speed-over-safety/) | Before/after: what AI removed and what it cost |
| [`tools/`](./tools/) | Runnable scripts: secret scanner, package checker |

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

- **`secret-scanner.py`** — scans a local repo for hardcoded credentials and exposed API keys
- **`package-checker.py`** — validates AI-suggested npm/PyPI packages exist and aren't typosquatted

```bash
# Scan a repo for secrets
python tools/secret-scanner.py --path /path/to/your/repo

# Check a list of packages
python tools/package-checker.py --file packages.txt
```

---

## 📋 Each Folder Follows This Pattern

```
topic/
├── README.md        # what it is · how to reproduce · what to look for · fix
├── vulnerable/      # intentionally broken example
└── fixed/           # patched version with explanation
```

---

## 👩‍💻 About

Built by [@DuskaT021](https://github.com/DuskaT021) — Senior QA Engineer with 6+ years in QA, 3+ years shipping security-critical blockchain software (Bitcoin wallets, Web3 infra).

> Good tests catch bugs. Good security research catches the bugs tests don't know to look for.

---

*Work in progress — findings added as I go.*
