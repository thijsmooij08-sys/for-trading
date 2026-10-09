# PolyTrader Next-Gen: Alpaca-First Master Prompt

Build a modular, evidence-driven, multi-venue trading platform. Start with one
complete vertical slice: US stocks and ETFs through Alpaca paper trading. The
system must not claim or assume profitability. Optimize for verified net
performance after fees, spread, slippage, and realistic execution constraints.

## Authority and scope

- Begin with Alpaca paper trading only; support only an allowlisted set of liquid
  US stocks and ETFs.
- Maintain a future Polymarket adapter boundary, but do not implement its
  authenticated order path in the first vertical slice.
- Use NautilusTrader only behind a simulation/replay adapter; it must not become
  a competing ledger or risk authority.
- Use MLflow, Optuna, DuckDB, and Parquet only for research; they cannot submit,
  approve, or account for orders.
- No real order may be placed during development, CI, test, replay, or paper
  operation.

## Mandatory execution path

`Strategy -> Signal -> Opportunity -> PortfolioDirector -> PositionSizer -> RiskManager -> OrderIntent -> ExecutionRouter -> Fill/Reconciliation -> Ledger -> Attribution`

Every order path must follow this sequence. No agent, plugin, model, dashboard,
or script can bypass the RiskManager. Financial values use exact `Decimal`.
Naked shorting and position-increasing sell orders are rejected unless a later,
explicit policy permits them and inventory/account rules prove eligibility.

## Initial architecture

1. **Data Hub**: Alpaca market data adapter, canonical instruments, timestamps,
   provenance, freshness checks, bounded retries, and persisted raw evidence.
2. **Trading Core**: reservations, deterministic risk decisions, idempotent
   order intents, paper fills, double-entry-style ledger projections, positions,
   and broker reconciliation interfaces.
3. **Research Plane**: Nautilus replay/simulation, DuckDB/Parquet datasets,
   MLflow experiment lineage, and Optuna trials. Research output is advisory.
4. **Strategy Governance**: versioned strategy artifacts, fixed benchmarks,
   walk-forward evaluation, holdout separation, and promotion evidence.
5. **Operations/UI**: a read-only dashboard, health, data freshness, paper
   P&L, rejection reasons, backups, alerts, and decision replay.

## Paper-to-live authorization boundary

Live capability is a future milestone, not an environment-variable flip. Before
any live order route exists, require all of the following:

- explicit user-created, expiring `AutonomousLivePolicy`;
- local secret-store credentials that are never read by research workers;
- broker account eligibility and a verified allowlist;
- reconciliation of cash, positions, and open orders;
- passing fresh-data, risk, kill-switch, and restart/recovery tests;
- a deliberate, time-limited arm action performed locally by the user;
- separate paper/live ledger namespaces and dashboard reporting.

Failure of any condition blocks new exposure. The default state is
`LIVE_DISABLED`.

## Acceptance gates

1. End-to-end paper workflow: data -> signal -> opportunity -> risk -> paper
   order -> fill -> ledger -> dashboard -> restart recovery.
2. Duplicate events/orders do not duplicate cash, fills, or positions.
3. Stale or invalid data blocks exposure.
4. No order can exceed policy, cash reservation, position, or daily-loss limits.
5. Paper P&L is separated from any future live P&L.
6. Strategies are not promoted on small samples or raw backtest returns alone.
7. Every result is traceable from input evidence through final outcome.

## Milestones

- M0: repository setup, source/licence audit, canonical contracts.
- M1: exact ledger, deterministic risk, paper order state machine.
- M2: Alpaca data + stock/ETF paper vertical slice.
- M3: replay/simulation and realistic cost model.
- M4: research store, experiments, benchmarks, and validation gates.
- M5: observability, recovery, adversarial tests, and dashboard.
- M6: prospective forward paper evaluation; retain only strategies with evidence.
- M7: separately scoped Polymarket market-data and paper-simulation adapter.
- M8: only after independent review, design—not activation—of live capability.
