# Architecture

## Authority boundaries

| Component | May do | May not do |
| --- | --- | --- |
| Strategy | produce signals | approve risk or submit orders |
| PortfolioDirector | compare approved opportunities | increase policy limits |
| RiskManager | allow/reject valid intents | be bypassed |
| ExecutionRouter | route approved paper intents | create money or change risk |
| Ledger | record immutable financial events | infer missing fills |
| Research plane | evaluate hypotheses | access live credentials or execute |
| Dashboard | show evidence and controls | directly route trades |

## Three-speed model

- **Fast path:** freshness, risk, reservations, order states, fills, and
  reconciliation. Deterministic and dependency-minimal.
- **Intelligence path:** new data and evidence updates create opportunities.
- **Research path:** replay, training, optimization, and tournaments. Bounded,
  isolated, and never execution-critical.

## Persistence

PostgreSQL is the intended authoritative financial ledger for the new project.
DuckDB/Parquet hold research datasets only. Raw market evidence and decision
traces retain source, event/availability/ingestion timestamps, schema version,
strategy version, and trace ID.

## Future venue adapter rule

Every venue has a separate data adapter, execution adapter, reconciliation
adapter, credential boundary, instrument mapping, and test suite. A venue may
not share account state or credentials with another venue.
