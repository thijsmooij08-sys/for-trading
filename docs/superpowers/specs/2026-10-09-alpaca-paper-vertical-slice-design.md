# Alpaca-First Paper-Trading Vertical Slice

## Status and objective

Build the first runnable PolyTrader Next-Gen vertical slice for allowlisted US
stocks and ETFs. It operates offline by default using a deterministic paper
broker, and may later use Alpaca paper trading only through a dedicated adapter.
Live trading is out of scope and structurally unavailable.

Success is a traceable path from a validated market observation to a
`NO_TRADE` decision or a paper fill and immutable ledger projection. This is
not a profitability claim or an alpha-strategy implementation.

## Scope

The initial implementation contains:

* Decimal-based domain contracts for instruments, observations, signals,
  opportunities, order intents, fills, risk decisions, and ledger events.
* The mandatory authority path: `Strategy -> Signal -> Opportunity ->
  PortfolioDirector -> PositionSizer -> RiskManager -> OrderIntent ->
  ExecutionRouter -> Fill -> Ledger`.
* An allowlist and freshness validation gate, deterministic paper execution,
  idempotency, a no-naked-sell guard, and a PostgreSQL ledger adapter.
* A read-only health/projection API surface, and a Docker Compose PostgreSQL
  service for local integration tests.
* An Alpaca adapter contract and an Alpaca-paper implementation that is not
  enabled by default and cannot access ledger or risk internals directly.

Explicitly excluded: live order routes, live credentials, Polymarket data or
execution, profitability claims, strategy promotion, dashboard UI, Nautilus
execution, and research-to-execution coupling.

## Structure

```text
backend/
  src/polytrader/
    domain/        # Decimal values, contracts, state machines
    data/          # validation and evidence provenance
    strategies/    # non-authoritative signal producer
    portfolio/     # reservations and sizing
    risk/          # final deterministic gate
    execution/     # paper router and Alpaca adapter port
    ledger/        # PostgreSQL events and projections
    api/           # read-only health/projections
  tests/
infra/compose/     # PostgreSQL local test service
docs/source-intake/
```

The domain package has no dependency on a broker SDK, database driver, web
framework, or research package. The risk service consumes a fully formed order
intent and returns an explicit decision. Only an approved decision reaches the
execution router. The router accepts a paper-execution port; no adapter may
construct a ledger event or override a risk decision.

## Data flow and persistence

`MarketObservation` retains source, event, availability, and ingestion
timestamps, schema version, strategy version, and trace ID. Validation rejects
symbols outside the configured allowlist and observations older than the policy
freshness threshold. Rejection becomes `NO_TRADE` with a reason code.

All monetary values and quantities use `Decimal`; floats are rejected at public
financial boundaries. A trace ID follows the decision path. `OrderIntent`,
`Fill`, and ledger event identifiers are idempotency keys. Reprocessing an
identical message is a no-op; a conflicting duplicate fails closed.

PostgreSQL is the sole financial authority. Research data, including DuckDB and
Parquet, is non-authoritative and cannot share a write path with the ledger.

## Integrations and authority

Dependencies are separated into locked extras rather than copied repositories.
Every selected version has a source-intake record with its immutable version,
licence, hash, maintainer, purpose, credential access, startup behavior,
failure/recovery behavior, removal plan, and integration test.

| Group | Integrations | Allowed role |
| --- | --- | --- |
| core | Pydantic, SQLAlchemy, psycopg, Alembic, FastAPI | contracts, ledger persistence, read-only API |
| alpaca | alpaca-py | market-data and paper adapter only |
| simulation | NautilusTrader | isolated replay/simulation only |
| research | DuckDB, PyArrow, MLflow, Optuna | research only |
| dev | pytest, Hypothesis, Ruff, mypy | quality gates |

Optional groups may be installed but must not be imported by the runtime order
path. Their tests prove they cannot obtain execution authority. The initial
implementation does not configure Alpaca credentials; when credentials are
later added, only the paper endpoint and allowlisted symbols are permitted.

## Failure policy

Invalid, stale, or missing market evidence returns `NO_TRADE`. Missing broker
or reconciliation health blocks new exposure. Duplicate intents or fills never
change cash, positions, or the ledger twice. Position-increasing sells are
rejected unless a future policy explicitly permits them and verified inventory
exists. All unexpected adapter failures are represented as explicit failed
states with their trace ID; they cannot fall through to an order submission.

## Verification

Tests run offline against the deterministic broker and, for integration tests,
the Compose PostgreSQL service. They prove:

1. the complete approved paper path produces a balanced ledger projection;
2. stale or invalid observations produce `NO_TRADE` and no intent;
3. every risk rejection prevents execution;
4. duplicate intents and fills are idempotent;
5. naked or position-increasing sells are rejected;
6. Decimal contracts reject float financial input;
7. the Alpaca port cannot bypass risk or write ledger events; and
8. optional research/simulation groups have no execution authority.

## Operational constraints

The default mode is offline paper simulation. No configuration flag can enable
live trading. A future live capability requires a separately designed route,
explicit user policy, local credentials, reconciliation, readiness tests, and
a time-limited local arm action. It is not part of this project milestone.
