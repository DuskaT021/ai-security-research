# Broken access control

Covers IDOR-style leaks, missing server-side checks, and database policies (e.g. Postgres/Supabase RLS) that AI-generated stacks often omit or weaken.

- [`idor-demo/`](./idor-demo/) — endpoint or flow that exposes other users’ data without authorization
- [`missing-rls/`](./missing-rls/) — Row Level Security bypass or “RLS not enabled” scenarios

**Results / status:** WIP — demos and write-ups to be filled in.
