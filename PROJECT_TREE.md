# Suggested Initial Repository Tree

```text
polytrader-nextgen/
  backend/
    src/polytrader/
      domain/           # Decimal contracts and state machines
      data/             # Alpaca data, canonicalization, evidence
      strategies/       # versioned, non-authoritative strategies
      portfolio/        # allocation and reservations
      risk/             # final deterministic risk gate
      execution/        # paper router and reconciliation interface
      ledger/           # PostgreSQL persistence and projections
      simulation/       # Nautilus adapter and replay
      research/         # MLflow/Optuna/DuckDB adapters
      operations/       # health, backup, scheduling, audit
      api/              # read-only projections and guarded control API
    tests/
  frontend/
  infra/
    compose/
    migrations/
    observability/
  docs/
    decisions/
    exec-plans/
  scripts/
  AGENTS.md
  README.md
```

Create the first executable feature only after tests define its failure modes:
an allowlisted Alpaca paper-market observation flowing through validation,
opportunity/risk rejection, a paper order intent, a reconciled fill, and a
ledger projection.
