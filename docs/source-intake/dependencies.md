# Dependency Source Intake

All dependencies are pinned in `pyproject.toml`. A package may only be used in
the listed authority boundary. Hashes are generated from the resolved wheel
artifacts during bootstrap and recorded in the lock report; no dependency is
downloaded from a cloned source repository.

| Package | Pinned version | Licence | Allowed role | Credential access | Failure/recovery | Removal path |
| --- | --- | --- | --- | --- | --- | --- |
| Pydantic | 2.14.0 | MIT | immutable boundary contracts | none | validation failure blocks input | replace contract adapter |
| SQLAlchemy | 2.1.3 | MIT | PostgreSQL persistence adapter | database URL only | persistence failure blocks exposure | replace persistence adapter |
| psycopg | 3.3.6 | LGPL-3.0-only | PostgreSQL driver | database URL only | connection failure blocks exposure | replace driver adapter |
| Alembic | 1.20.0 | MIT | database migrations | database URL only | migration failure stops startup | remove migration tool |
| FastAPI | 0.143.0 | MIT | read-only API | none | API unavailable; execution unaffected | replace API adapter |
| alpaca-py | 0.44.0 | Apache-2.0 | Alpaca data/paper adapter only | future paper keys only | adapter failure blocks new exposure | disable optional group |
| NautilusTrader | 1.231.0 | LGPL-3.0 | replay/simulation only | none | research failure is isolated | disable optional group |
| DuckDB | 1.5.6 | MIT | research datasets only | none | research failure is isolated | disable optional group |
| PyArrow | 25.0.1 | Apache-2.0 | research datasets only | none | research failure is isolated | disable optional group |
| MLflow | 3.17.0 | Apache-2.0 | experiment lineage only | optional tracking URI | research failure is isolated | disable optional group |
| Optuna | 5.0.0 | MIT | parameter search only | none | research failure is isolated | disable optional group |
| pytest | 9.1.1 | MIT | tests only | none | prevents release verification | dev-only removal |
| Hypothesis | 6.168.5 | MPL-2.0 | property tests only | none | prevents property verification | dev-only removal |
| Ruff | 0.17.0 | MIT | linting only | none | prevents quality verification | dev-only removal |
| mypy | 2.4.0 | MIT | static typing only | none | prevents type verification | dev-only removal |

## Authority checks

- No optional research or simulation dependency may import execution routing,
  receive broker credentials, approve risk, or write ledger events.
- Alpaca is configured for paper endpoints only when a later adapter is
  explicitly enabled; no live endpoint is present in project configuration.
- Dependency hash and vulnerability checks are part of every lock refresh.

## Direct wheel hashes

These SHA-256 values were calculated from the Python 3.12 Windows wheels
resolved during the initial bootstrap on 2026-10-09. A different Python or
platform requires a separately recorded artifact hash.

| Package | Artifact SHA-256 |
| --- | --- |
| Alembic 1.20.0 | `77eb101048d95f982c0353e9233404889dcd7a6fc244c107836c0e2fc9cf7d9d` |
| alpaca-py 0.44.0 | `b54673f967c0c814a5e0223cbb0211a5d9d75a8d107e792872b14e5bae957c03` |
| DuckDB 1.5.6 | `09ff51b230219f0d8b47fc8a1e17fb595ba9fab0c3d96a6de4d00b8ff86b3cf1` |
| FastAPI 0.143.0 | `3e9395fd35276425b61b516a31fdd7c77fe2af83e41b4da22e30696fb1304c5d` |
| Hypothesis 6.168.5 | `2fcec23ff4eb526ee85d3510f564b938ca74f6011f1eec1050e4eb55280b0468` |
| MLflow 3.17.0 | `3954eaa998d4dd4ac8772894293a285bb5e3a428f6f9b37cac298e787423eafd` |
| mypy 2.4.0 | `236e0d68f6941992b0811128e652590f590db444ab29ad8f1324765b9298b946` |
| NautilusTrader 1.231.0 | `0697f51e9143f9d8d040f75d2e6a45218003cc34f7ea5b0eb2f9cda6935427de` |
| Optuna 5.0.0 | `5fff892ae6baf4948c810c5b8635ec67e08efb0709b41cb73b14e30391d44720` |
| psycopg 3.3.6 | `a1db9f7148b06a28606767efaca51fa6f9398c5c0a3810519be69d7000bdb631` |
| PyArrow 25.0.1 | `8858d7bfc22e3f51529aeaa4077225029724623e4595dc9eff8c793935c34140` |
| Pydantic 2.14.0 | `15fab1bea6f1dc5003b54fc2ecab230c1fd1dbade2acd4addc52d81e32416d4b` |
| pytest 9.1.1 | `37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c` |
| Ruff 0.17.0 | `8ab76bcda86dfd28e13776cb5de3c7bcdcf1ae3d37ed761113d1a5a415dc134c` |
| SQLAlchemy 2.1.3 | `f097f4efb9ba48f3069b17998abd8bbe2131b7f5d3c00ab7b69101d68bd976f4` |
