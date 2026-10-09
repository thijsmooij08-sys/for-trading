# Alpaca-First Paper Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver an offline, deterministic, end-to-end stock/ETF paper-trading path that records an idempotent PostgreSQL ledger projection without any live-trading capability.

**Architecture:** A dependency-free domain core owns immutable Decimal contracts and the order state machine. Data validation, strategy, portfolio, risk, execution, and ledger modules compose the mandatory authority path; adapters implement ports but cannot bypass the risk decision or write ledger events directly. PostgreSQL is the only financial store and the read-only API exposes health and projections.

**Tech Stack:** Python 3.12, Pydantic, SQLAlchemy, psycopg, Alembic, FastAPI, PostgreSQL, Docker Compose, pytest, Hypothesis, Ruff, mypy; optional extras for Alpaca, NautilusTrader, DuckDB/PyArrow, MLflow, and Optuna.

**Spec:** `docs/superpowers/specs/2026-10-09-alpaca-paper-vertical-slice-design.md`

## Global Constraints

- All money and quantities use `Decimal`; floats are rejected at public financial boundaries.
- The required path is `Strategy -> Signal -> Opportunity -> PortfolioDirector -> PositionSizer -> RiskManager -> OrderIntent -> ExecutionRouter -> Fill -> Ledger`.
- `RiskManager` is the final deterministic gate; no adapter, script, API, or optional package bypasses it.
- Default execution is offline deterministic paper simulation; live endpoints and live credentials are absent.
- PostgreSQL is the only authoritative financial ledger; research stores are isolated and non-authoritative.
- Reject stale or non-allowlisted market observations with an explicit `NO_TRADE` reason.
- Use explicit idempotency keys and trace IDs for intents, fills, and ledger events; conflicting duplicates fail closed.
- Position-increasing sells are rejected unless future policy and verified inventory explicitly permit them.
- Every third-party dependency is version-pinned and has a source-intake record before it is used.

## Review Focus

- Decimal string inputs such as `"0.10"` retain exactness, while `0.1` floats fail validation; test in Task 2.
- Boundary-aged observations exactly at the freshness threshold are accepted and one microsecond older is rejected; test in Task 3.
- Replayed fills with the same idempotency key do not alter cash/position twice, while a same-key different-payload replay fails; test in Task 6.
- A sell equal to inventory is allowed but a sell one unit larger is rejected before execution; test in Task 5.
- Optional-package imports cannot construct `ExecutionRouter` or submit an `OrderIntent`; test in Task 8.

---

## File Structure

| Path | Responsibility |
| --- | --- |
| `pyproject.toml` | Python project metadata, exact dependency groups, test/lint/type settings |
| `docs/source-intake/dependencies.md` | package versions, hashes, licenses, authority and removal records |
| `backend/src/polytrader/domain/models.py` | Decimal contracts, IDs, enums, immutable events |
| `backend/src/polytrader/domain/errors.py` | explicit domain failure types |
| `backend/src/polytrader/data/validation.py` | allowlist/freshness evidence validation |
| `backend/src/polytrader/strategies/baseline.py` | deterministic non-authoritative baseline signal producer |
| `backend/src/polytrader/portfolio/director.py` | reservation-aware opportunity selection and sizing |
| `backend/src/polytrader/risk/manager.py` | final policy decision and sell/cash checks |
| `backend/src/polytrader/execution/ports.py` | paper broker and Alpaca adapter protocols |
| `backend/src/polytrader/execution/paper.py` | deterministic offline fill model and router |
| `backend/src/polytrader/ledger/models.py` | SQLAlchemy event/projection tables |
| `backend/src/polytrader/ledger/service.py` | idempotent ledger recording/projections |
| `backend/src/polytrader/application/pipeline.py` | orchestration of mandatory authority path |
| `backend/src/polytrader/api/app.py` | read-only health and projection API |
| `infra/compose/compose.yaml` | isolated PostgreSQL service for this project |
| `backend/tests/` | contract, unit, integration, and authority-boundary tests |

### Task 1: Project bootstrap and auditable dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `backend/src/polytrader/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `docs/source-intake/dependencies.md`
- Create: `infra/compose/compose.yaml`

**Interfaces:**
- Produces the install commands and dependency groups consumed by every later task.

- [ ] **Step 1: Write the failing bootstrap test**

Create `backend/tests/test_project_layout.py` asserting the package can import and that the project version is available from `polytrader.__version__`.

- [ ] **Step 2: Verify it fails before scaffolding**

Run: `python -m pytest backend/tests/test_project_layout.py -v`
Expected: FAIL because `polytrader` cannot be imported.

- [ ] **Step 3: Create the pinned project manifest and source-intake record**

Use Python `>=3.12,<3.13`; define `core`, `alpaca`, `simulation`, `research`, and `dev` extras. Pin the resolved package versions and hashes after `pip install --require-hashes` preparation. Record FastAPI, Pydantic, SQLAlchemy, psycopg, Alembic, Alpaca, NautilusTrader, DuckDB, PyArrow, MLflow, Optuna, pytest, Hypothesis, Ruff, and mypy with allowed authority and licence/source data.

- [ ] **Step 4: Add package skeleton, ignore rules, and the isolated Postgres compose service**

Expose `__version__: str`; ignore `.venv/`, Python caches, `.env`, and local database volumes. Compose must name its project `polytrader-nextgen`, expose PostgreSQL only on a local port, and use no credentials from tracked files.

- [ ] **Step 5: Install and verify the selected groups**

Run: `python -m pip install -e ".[core,alpaca,simulation,research,dev]"`
Expected: successful installation with versions matching the source-intake record.

- [ ] **Step 6: Run the bootstrap test and static checks**

Run: `python -m pytest backend/tests/test_project_layout.py -v; ruff check backend; mypy backend/src`
Expected: PASS, no Ruff diagnostics, no mypy errors.

- [ ] **Step 7: Commit bootstrap artifacts**

```bash
git add pyproject.toml .gitignore backend infra docs/source-intake
git commit -m "chore: bootstrap audited paper trading project"
```

### Task 2: Decimal domain contracts and state-machine primitives

**Files:**
- Create: `backend/src/polytrader/domain/models.py`
- Create: `backend/src/polytrader/domain/errors.py`
- Create: `backend/tests/domain/test_models.py`

**Interfaces:**
- Produces `Instrument`, `MarketObservation`, `Signal`, `Opportunity`, `OrderIntent`, `Fill`, `RiskDecision`, `LedgerEvent`, `Side`, `OrderStatus`, and `NoTradeReason`.
- Consumed by Tasks 3–7.

- [ ] **Step 1: Write failing Decimal contract tests**

Test that `Money(amount: Decimal, currency: str)` and `Quantity(value: Decimal)` accept Decimal values, reject floats, and preserve `Decimal("0.10")`; test immutable IDs and trace IDs on `OrderIntent` and `Fill`.

- [ ] **Step 2: Verify contract tests fail**

Run: `python -m pytest backend/tests/domain/test_models.py -v`
Expected: FAIL because the domain models do not exist.

- [ ] **Step 3: Implement immutable domain models**

Implement Pydantic frozen models and string enums. `OrderIntent` must contain `intent_id`, `trace_id`, `instrument`, `side`, `quantity`, `limit_price`, and `idempotency_key`; `Fill` must contain `fill_id`, `order_intent_id`, `trace_id`, `quantity`, `price`, and `idempotency_key`.

- [ ] **Step 4: Run domain tests and property tests**

Run: `python -m pytest backend/tests/domain/test_models.py -v`
Expected: PASS, including float rejection and Decimal exactness.

- [ ] **Step 5: Commit domain contracts**

```bash
git add backend/src/polytrader/domain backend/tests/domain
git commit -m "feat: add exact financial domain contracts"
```

### Task 3: Market-evidence validation and non-authoritative signal creation

**Files:**
- Create: `backend/src/polytrader/data/validation.py`
- Create: `backend/src/polytrader/strategies/baseline.py`
- Create: `backend/tests/data/test_validation.py`
- Create: `backend/tests/strategies/test_baseline.py`

**Interfaces:**
- Consumes: `MarketObservation`, `Instrument`, `Signal`, `NoTradeReason` from Task 2.
- Produces: `validate_observation(observation: MarketObservation, now: datetime, allowed_symbols: frozenset[str], max_age: timedelta) -> ValidationResult` and `BaselineStrategy.create_signal(observation: MarketObservation) -> Signal`.

- [ ] **Step 1: Write failing validation tests**

Test accepted allowlisted evidence, rejected non-allowlisted symbol, accepted observation at exact threshold, rejected stale observation, and preserved provenance/trace fields.

- [ ] **Step 2: Verify validation tests fail**

Run: `python -m pytest backend/tests/data/test_validation.py -v`
Expected: FAIL because the validation module is absent.

- [ ] **Step 3: Implement fail-closed validation and baseline signal creation**

`ValidationResult` returns either validated evidence or a `NoTradeReason`; never raises for an expected input rejection. The baseline strategy is deterministic and emits a non-authoritative `Signal` only for validated observations.

- [ ] **Step 4: Run validation and strategy tests**

Run: `python -m pytest backend/tests/data/test_validation.py backend/tests/strategies/test_baseline.py -v`
Expected: PASS.

- [ ] **Step 5: Commit evidence gate**

```bash
git add backend/src/polytrader/data backend/src/polytrader/strategies backend/tests/data backend/tests/strategies
git commit -m "feat: validate market evidence before signals"
```

### Task 4: Portfolio reservation, sizing, and final risk gate

**Files:**
- Create: `backend/src/polytrader/portfolio/director.py`
- Create: `backend/src/polytrader/risk/manager.py`
- Create: `backend/tests/portfolio/test_director.py`
- Create: `backend/tests/risk/test_manager.py`

**Interfaces:**
- Consumes: `Opportunity`, `OrderIntent`, `RiskDecision`, `Money`, `Quantity`, and `Side` from Task 2.
- Produces: `PortfolioDirector.create_intent(opportunity: Opportunity, available_cash: Money) -> OrderIntent | NoTradeReason` and `RiskManager.evaluate(intent: OrderIntent, available_cash: Money, inventory: Mapping[str, Quantity]) -> RiskDecision`.

- [ ] **Step 1: Write failing portfolio/risk tests**

Test cash reservation prevents an oversized buy, allowed sell at exact inventory, rejected sell exceeding inventory, and a rejected decision never returns an execution-approved intent.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest backend/tests/portfolio/test_director.py backend/tests/risk/test_manager.py -v`
Expected: FAIL because the services are absent.

- [ ] **Step 3: Implement deterministic sizing and risk reasons**

Use exact Decimal arithmetic. `RiskManager.evaluate` returns `RiskDecision(approved: bool, reason: str | None, trace_id: UUID)` and rejects unknown symbols, insufficient cash, or inventory-increasing sells.

- [ ] **Step 4: Run risk tests**

Run: `python -m pytest backend/tests/portfolio/test_director.py backend/tests/risk/test_manager.py -v`
Expected: PASS.

- [ ] **Step 5: Commit portfolio/risk boundary**

```bash
git add backend/src/polytrader/portfolio backend/src/polytrader/risk backend/tests/portfolio backend/tests/risk
git commit -m "feat: enforce deterministic portfolio and risk decisions"
```

### Task 5: Paper-execution port and deterministic router

**Files:**
- Create: `backend/src/polytrader/execution/ports.py`
- Create: `backend/src/polytrader/execution/paper.py`
- Create: `backend/tests/execution/test_paper_router.py`
- Create: `backend/tests/execution/test_alpaca_port.py`

**Interfaces:**
- Consumes: approved `OrderIntent` and `RiskDecision` from Task 4.
- Produces: `PaperBroker.submit(intent: OrderIntent) -> Fill` and `ExecutionRouter.route(intent: OrderIntent, decision: RiskDecision) -> Fill`.

- [ ] **Step 1: Write failing router tests**

Test approved intent produces a deterministic fill, rejected decision raises `ExecutionBlocked`, and an Alpaca adapter port cannot call `submit` without an approved `RiskDecision`.

- [ ] **Step 2: Verify router tests fail**

Run: `python -m pytest backend/tests/execution/test_paper_router.py backend/tests/execution/test_alpaca_port.py -v`
Expected: FAIL because execution modules are absent.

- [ ] **Step 3: Implement ports and deterministic paper fill behaviour**

Define `PaperExecutionPort` as a protocol that accepts only an approved intent. `ExecutionRouter.route` must check `decision.approved` itself before delegating. The Alpaca adapter is an unconfigured stub implementing the same port and exposes no live endpoint or credential fields.

- [ ] **Step 4: Run execution tests**

Run: `python -m pytest backend/tests/execution -v`
Expected: PASS.

- [ ] **Step 5: Commit paper execution**

```bash
git add backend/src/polytrader/execution backend/tests/execution
git commit -m "feat: add risk-gated deterministic paper execution"
```

### Task 6: PostgreSQL ledger, idempotency, and projections

**Files:**
- Create: `backend/src/polytrader/ledger/models.py`
- Create: `backend/src/polytrader/ledger/service.py`
- Create: `backend/tests/ledger/test_service.py`
- Create: `backend/tests/integration/test_postgres_ledger.py`

**Interfaces:**
- Consumes: `Fill`, `OrderIntent`, `LedgerEvent` from Tasks 2 and 5.
- Produces: `LedgerService.record_fill(fill: Fill, intent: OrderIntent) -> LedgerProjection` and `LedgerService.get_projection(trace_id: UUID) -> LedgerProjection | None`.

- [ ] **Step 1: Write failing ledger tests**

Test a fill creates balanced cash/position projections, same-key replay is a no-op, same-key altered payload raises `IdempotencyConflict`, and an integration test persists/reloads the projection through PostgreSQL.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest backend/tests/ledger/test_service.py -v`
Expected: FAIL because ledger modules are absent.

- [ ] **Step 3: Implement SQLAlchemy models and idempotent service**

Persist immutable ledger events with unique idempotency keys and projection rows. Compare canonical event payload hashes on duplicate insert. Do not allow execution adapters to call the persistence session directly.

- [ ] **Step 4: Start isolated PostgreSQL and run integration tests**

Run: `docker compose -f infra/compose/compose.yaml up -d --wait; python -m pytest backend/tests/ledger backend/tests/integration/test_postgres_ledger.py -v`
Expected: PASS; existing unrelated Docker containers remain untouched.

- [ ] **Step 5: Commit ledger implementation**

```bash
git add backend/src/polytrader/ledger backend/tests/ledger backend/tests/integration infra/compose
git commit -m "feat: record idempotent paper fills in postgres ledger"
```

### Task 7: Application orchestration and read-only API

**Files:**
- Create: `backend/src/polytrader/application/pipeline.py`
- Create: `backend/src/polytrader/api/app.py`
- Create: `backend/tests/application/test_pipeline.py`
- Create: `backend/tests/api/test_read_only.py`

**Interfaces:**
- Consumes: task-level services from Tasks 3–6.
- Produces: `PaperTradingPipeline.process(observation: MarketObservation) -> PipelineResult` and FastAPI `create_app(pipeline: PaperTradingPipeline) -> FastAPI`.

- [ ] **Step 1: Write failing vertical-slice and API tests**

Test one valid observation reaches a ledger projection, stale input returns `NO_TRADE` with no order, and the API exposes only `GET /health` and `GET /projections/{trace_id}` with no order-submission route.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest backend/tests/application/test_pipeline.py backend/tests/api/test_read_only.py -v`
Expected: FAIL because pipeline/API modules are absent.

- [ ] **Step 3: Implement orchestration with explicit stop points**

The pipeline must return immediately on invalid evidence, missing signal, portfolio rejection, or risk rejection. It may invoke `ExecutionRouter.route` only after an approved `RiskDecision`, then records the returned fill through `LedgerService`.

- [ ] **Step 4: Run vertical-slice verification**

Run: `python -m pytest backend/tests/application backend/tests/api -v`
Expected: PASS.

- [ ] **Step 5: Commit pipeline and read-only API**

```bash
git add backend/src/polytrader/application backend/src/polytrader/api backend/tests/application backend/tests/api
git commit -m "feat: orchestrate paper path through read-only API"
```

### Task 8: Optional-integration isolation and full quality gate

**Files:**
- Create: `backend/src/polytrader/research/ports.py`
- Create: `backend/src/polytrader/simulation/ports.py`
- Create: `backend/tests/architecture/test_authority_boundaries.py`
- Create: `README.md`

**Interfaces:**
- Consumes: package dependency groups from Task 1 and pipeline types from Task 7.
- Produces: non-executing research/simulation port markers and verified authority boundaries.

- [ ] **Step 1: Write failing authority-boundary tests**

Test research/simulation modules do not import `execution.paper`, the Alpaca integration is not live-configurable, and no route named `order`, `submit`, or `trade` is exposed by the API.

- [ ] **Step 2: Verify tests fail**

Run: `python -m pytest backend/tests/architecture/test_authority_boundaries.py -v`
Expected: FAIL because the isolation ports/tests are absent.

- [ ] **Step 3: Add marker ports and startup documentation**

Keep research and simulation ports dependency-free and incapable of receiving `ExecutionRouter`, `LedgerService`, or credentials. Document only offline startup, test, PostgreSQL, and future paper-credential setup instructions; explicitly state that live trading is unavailable.

- [ ] **Step 4: Run the complete quality gate**

Run: `docker compose -f infra/compose/compose.yaml up -d --wait; python -m pytest backend/tests -v; ruff check backend; mypy backend/src`
Expected: all tests pass, zero lint diagnostics, zero type errors.

- [ ] **Step 5: Commit and push the vertical slice**

```bash
git add backend README.md docs infra pyproject.toml
git commit -m "feat: complete offline alpaca-first paper vertical slice"
git push -u origin main
```

## Self-Review

Spec coverage is complete: exact contracts (Task 2), evidence freshness (Task 3), portfolio/risk authority (Task 4), paper execution (Task 5), PostgreSQL/idempotency (Task 6), traceable full path/read-only operations (Task 7), and research/simulation isolation (Task 8). The plan makes the optional integration installation auditable but forbids it from entering the runtime authority path. Each Review Focus case maps to an explicit test in Tasks 2–5 and 8. No live route, credential, or activation behavior is planned.
