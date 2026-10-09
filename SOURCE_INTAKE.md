# Source Intake Manifest

Do not bulk-download GitHub projects into the runtime. Each dependency requires
an allowlist entry, a pinned version/commit, a licence check, vulnerability
scan, isolated tests, and an explicit statement of authority.

| Source | Intended role | Initial status | Authority |
| --- | --- | --- | --- |
| https://github.com/nautechsystems/nautilus_trader | replay and execution-realism simulation | evaluate in isolation | never ledger/risk authority |
| https://github.com/alpacahq/alpaca-py | market data and paper adapter | first venue SDK | adapter only |
| https://github.com/mlflow/mlflow | experiment/model lineage | research only | never execution |
| https://github.com/optuna/optuna | bounded parameter search | research only | never execution |
| https://github.com/Polymarket/py-sdk | future Polymarket integration | defer | separate future adapter |

The archived `py-clob-client` must not be selected for new work. Verify the
current official Polymarket SDK, API terms, jurisdictional eligibility, and
licence during the later Polymarket intake.

## Required intake record

For each source capture: repository URL, immutable version/commit, licence,
package hash, owner/maintainer, purpose, data/credential access, integration
test, startup behavior, failure mode, recovery procedure, and removal plan.
