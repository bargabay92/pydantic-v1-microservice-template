# pydantic-v1-microservice-template

A small FastAPI **orders** microservice that is intentionally written against **Pydantic v1**.
It is a test target for Morph, a Pydantic v1 → v2 migration agent:
Morph clones it, finds the v1 usages, runs bump-pydantic, and hands what's left to an LLM agent.

## What v1 features it uses (on purpose)

| Feature | Where |
| --- | --- |
| `BaseSettings` from `pydantic`, `class Config` with `env_prefix` | `app/settings.py` |
| Custom types with `__get_validators__` / `__modify_schema__` | `app/types/money.py`, `app/types/sku.py` |
| `@validator` (incl. `pre=True`), `@root_validator` | `app/models/order.py` |
| `Field(regex=...)`, `min_items`, `orm_mode`, `json_encoders`, `anystr_strip_whitespace` | `app/models/order.py` |
| `.dict()`, `.json()`, `.copy(update=...)`, `parse_obj`, `parse_raw`, `.schema()` | `app/store.py`, `app/main.py`, tests |

The custom types are the part bump-pydantic cannot migrate on its own.

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest                      # 12 tests, all green on Pydantic v1
uvicorn app.main:app --reload
```

Or with Docker: `docker build -t orders . && docker run -p 8080:8080 orders`.

## API

`GET /health` · `POST /orders` · `GET /orders` · `GET /orders/{id}` · `GET /orders/{id}/total` · `PATCH /orders/{id}/status`
