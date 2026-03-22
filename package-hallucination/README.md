# Package hallucination

AI-suggested package names sometimes do not exist; typosquatting and dependency confusion follow. This area documents checks you can run before trusting a model’s `npm install` / `pip install` list.

- [`scanner/`](./scanner/) — script(s) to verify packages exist and flag suspicious names

**Results / status:** WIP — scanner logic may also live under [`../tools/package-checker.py`](../tools/package-checker.py); this folder is for topic-specific experiments and notes.
