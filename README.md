# PolyTrader Next-Gen — Alpaca-First Handoff

This is a documentation-only handoff for starting a new trading-system project.
It contains no credentials, wallet data, broker account data, executable order
submission code, or profitability claims.

## Starting decision

Build one complete US stock/ETF paper-trading vertical slice with Alpaca before
adding further venues. Design the boundaries for later Polymarket support, but
do not enable it in the first build.

The goal is independently verified net performance after costs and sufficient
forward evidence. `NO_TRADE` is a successful outcome when the evidence is weak.

## Included

- `MASTER_PROMPT.md` — implementation brief for the new project.
- `ARCHITECTURE.md` — target boundaries and mandatory data flow.
- `MIGRATION_HEADSTART.md` — reusable, tested ideas from the v11 handoff.
- `SOURCE_INTAKE.md` — approved source evaluation and licensing rules.
- `PROJECT_TREE.md` — suggested initial repository layout.

## Non-negotiable safety

The initial runnable mode is paper trading only. A future live mode must remain
unavailable unless a user deliberately supplies local credentials, creates an
explicit policy, passes reconciliation/readiness checks, and performs a
time-limited arm action. Automated tests must never submit real orders.
