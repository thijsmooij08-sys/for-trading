# Migration Head Start from v11

The v11 handoff is migration evidence, not controlling authority. Reuse these
ideas after port-level tests prove them in the new repository.

## Keep / adapt

- Exact `Decimal` financial math and cost-basis accounting.
- Deterministic final RiskManager and explicit rejection reasons.
- Idempotent order-intent flow and no-naked-sell guard.
- Book/depth-aware paper fill modelling, fee/slippage provenance, and replay.
- Evidence freshness, data health, source timestamps, and decision traceability.
- Population lineage, fixed benchmarks, Champion/Challenger evidence gates.
- Prometheus/Grafana-style read-only operations, backup health, and alerts.

## Do not promote as alpha

`DevelopmentStrategy` is an unvalidated seed only. The handoff reports negative
paper P&L, negative expectancy, and insufficient samples. Retain it solely as a
baseline/research candidate until it passes new independent evidence gates.

## Replace or defer

- Replace SQLite only through a reconciled PostgreSQL migration; never operate
  two authoritative ledgers.
- Defer optional providers/frameworks until source, licence, data quality, cost,
  and measurable contribution are verified.
- Do not copy historical wallet paths, `.env` files, browser profiles, or
  authenticated execution code into the new project.
