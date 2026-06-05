# Ads Automation Implementation Plan

> **For agentic workers:** REQUIRED: Use the `subagent-driven-development` agent (recommended) or `executing-plans` agent to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build v1 of a Google Ads recommendation-and-approval system for a preschool that monitors campaigns, generates structured recommendations using MiniCPM5-1B, and applies approved safe changes (budget adjustments, pause/resume, add negative keywords). Deploy as a Gradio app on a Hugging Face Space (CPU) with SQLite as the app source of truth.

**Architecture:** Single Gradio app with an embedded scheduler (APScheduler + SQLite jobstore). Deterministic rule engine produces candidate deltas; MiniCPM5 generates human-readable recommendation text. Google Ads integration uses `google-ads` Python client with admin OAuth. App persists to SQLite and syncs to Google Sheets for visibility.

**Tech Stack:** Python 3.10+, Gradio, SQLAlchemy, APScheduler, google-ads, google-auth, llama-cpp-python, pandas, requests, pytest.

---

### Task 1: Scaffold project layout

**Files:**
- Create: `app/__init__.py`
- Create: `app/main.py` (Gradio entrypoint)
- Create: `app/ads/connector.py`
- Create: `app/db/models.py`
- Create: `app/db/repo.py`
- Create: `app/recs/rules.py`
- Create: `app/models/llm.py`
- Create: `app/scheduler/jobs.py`
- Create: `scripts/seed_demo.py`
- Create: `requirements.txt`
- Create: `README.md`

- [ ] Step 1: Create repository layout and `requirements.txt`.

Create `requirements.txt` with:

```text
gradio
sqlalchemy
alembic
apscheduler
google-ads
google-auth
pandas
requests
llama-cpp-python
pytest
python-dotenv
gspread
oauth2client

tqdm
```

Run locally to verify environment installs:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Expected: packages install without fatal errors.

- [ ] Step 2: Commit the scaffold files (empty imports and module docstrings acceptable) and run a smoke start of `app/main.py` to ensure import graph is valid.

Run:

```bash
python -c "import app; print('scaffold ok')"
```

Expected: prints `scaffold ok`.

---

### Task 2: Implement SQLite schema + ORM

**Files:**
- Modify: `app/db/models.py`
- Create: `app/db/migrate.py` (simple create-tables script)
- Create: `app/db/repo.py` (CRUD helpers)

- [ ] Step 1: Define SQLAlchemy models for `Campaign`, `AdGroup`, `Keyword`, `Lead`, `Recommendation`, `AuditLog`.

Example `Campaign` model snippet (to include in file):

```python
from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    google_campaign_id = Column(String, unique=True, nullable=False)
    name = Column(String)
    managed = Column(Boolean, default=False)
    budget = Column(Float)
    target_cpl_override = Column(Float, nullable=True)
    last_synced = Column(DateTime, default=datetime.utcnow)
```

- [ ] Step 2: Implement `migrate.py` to create tables.

Run to verify:

```bash
python app/db/migrate.py
python - <<'PY'
from app.db.repo import SessionLocal
print('db ok')
PY
```

Expected: DB file created and `db ok` printed.

- [ ] Step 3: Add unit tests for model creation in `tests/test_db.py` using `pytest`.

---

### Task 3: Google Ads connector + admin OAuth

**Files:**
- Create: `app/ads/connector.py` (wraps `google-ads` client)
- Create: `app/ads/oauth.py` (helper for OAuth flow)
- Modify: `app/main.py` (admin settings UI to start OAuth or paste tokens)

- [ ] Step 1: Implement OAuth helper that can accept client_id/client_secret and produce a refresh_token (manual paste fallback supported).

- [ ] Step 2: Implement connector functions:
  - `list_campaigns()` (returns campaigns metadata)
  - `get_campaign_metrics(campaign_ids, start_date, end_date)` (returns spend, clicks, impressions, CTR, conversions/leads)
  - `apply_budget_change(campaign_id, new_budget)`
  - `pause_keyword(keyword_id)`
  - `add_negative_keyword(campaign_id, phrase)`

- [ ] Step 3: Mock Google Ads in tests `tests/test_ads_connector.py` using recorded fixtures or a simple interface stub.

Verification:

- Run `python -c "from app.ads.connector import list_campaigns; print(list_campaigns()[:1])"` with mocked creds to ensure no crashes.

---

### Task 4: Rule engine (deterministic signals)

**Files:**
- Modify: `app/recs/rules.py`

- [ ] Step 1: Implement moving-average smoothing (3-day simple moving average) and min-sample guards.

- [ ] Step 2: Implement the default rules from the spec. Each rule returns a candidate delta dict when fired.

- [ ] Step 3: Unit tests in `tests/test_rules.py` covering each rule with synthetic metric inputs and expected candidate deltas.

---

### Task 5: MiniCPM5 wrapper and prompt pipeline

**Files:**
- Modify/Create: `app/models/llm.py`
- Modify: `app/recs/generate.py` (build prompt, call llm, validate JSON)

- [ ] Step 1: Implement a thin wrapper using `llama_cpp` from `llama-cpp-python` to load GGUF from HF Hub path. Support a `load_model(llm_repo_id, llm_filename, cache_dir)` call.

- [ ] Step 2: Implement prompt template that accepts a JSON payload and instructs the model to return a single `recommendation` JSON object following the schema. Example instructions must enforce JSON-only output.

- [ ] Step 3: Implement output validation using `jsonschema` or Python checks; reject and retry + fallback to deterministic textual reason if parsing fails.

- [ ] Step 4: Unit tests for `generate.py` to assert correct parseable output given a mocked model runner.

Notes: target inference via `llama-cpp-python` with the quantized GGUF. For Space CPU mode, expect slower responses; implement a request timeout and a cached most-recent recommendation for UI responsiveness.

---

### Task 6: Gradio UI pages

**Files:**
- Modify/Create: `app/main.py` (Gradio app)
- Modify/Create: `app/ui/dashboard.py`
- Modify/Create: `app/ui/campaigns.py`
- Modify/Create: `app/ui/recommendations.py`
- Modify/Create: `app/ui/leads.py`
- Modify/Create: `app/ui/admin.py`

- [ ] Step 1: Implement `Main Dashboard` with summary cards and a small time-series chart (use `pandas` to prepare data and `gradio` components to display). Include a button to trigger on-demand review.

- [ ] Step 2: `Campaigns` page: table with per-campaign KPIs and a toggle to mark campaign as `managed`.

- [ ] Step 3: `Recommendations` page: list recommendations, view details, Approve/Reject controls with scheduling and staged rollout UI.

- [ ] Step 4: `Lead Manager` page: table to mark leads as `booked`, manual-add lead form, and export button to Google Sheets.

- [ ] Step 5: `Admin` page: set global `target_cpl`, manage HF Secrets link, manual OAuth flow start.

Verification: start the Gradio app locally:

```bash
python app/main.py
# visit http://localhost:7860
```

Expected: App loads, pages render, no JS errors.

---

### Task 7: Scheduler + Auto-apply

**Files:**
- Modify/Create: `app/scheduler/jobs.py`
- Modify/Create: `app/scheduler/bootstrap.py`

- [ ] Step 1: Wire APScheduler with SQLite jobstore and add daily job to run the review loop.

- [ ] Step 2: Implement apply jobs that call the Ads connector to enact approved changes and write audit logs and rollback snapshots.

- [ ] Step 3: Tests: `tests/test_scheduler.py` with in-memory jobstore verifying a job runs and changes recorded in DB.

---

### Task 8: Google Sheets sync & Lead capture

**Files:**
- Create: `scripts/sheet_sync.py`
- Modify: `app/leads/sync.py`

- [ ] Step 1: Implement Google Sheets API write-only sync for leads; use service-account or OAuth depending on deployment constraints.

- [ ] Step 2: Implement landing page form that writes to DB and triggers immediate UI visibility.

- [ ] Step 3: Tests: `tests/test_sheets.py` with a mocked sheets client.

---

### Task 9: Seeded demo data & testing

**Files:**
- Modify/Create: `scripts/seed_demo.py`

- [ ] Step 1: Implement seed script that creates sample campaigns, keywords, synthetic metrics and leads to exercise rules and model pipeline.

- [ ] Step 2: Add end-to-end smoke test `tests/test_e2e.py` that runs seed, triggers a review, generates recommendations (mocked LLM), and simulates approval + apply (with Ads connector mocked).

---

### Task 10: Documentation & HF Space deploy

**Files:**
- Modify/Create: `README.md` (run/deploy instructions)
- Modify/Create: `Dockerfile` or HF `requirements.txt` and `runtime.txt` if needed

- [ ] Step 1: Write deployment steps for HF Space (including HF Secrets setup and model cache instructions).

- [ ] Step 2: Provide a small `try it` section in `README.md` showing how to run locally and how to seed demo data.

Example local run commands:

```bash
# local dev
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/db/migrate.py
python scripts/seed_demo.py
python app/main.py
```

**Expected:** Developer can run seeded demo locally and browse to the Gradio app.

---

## Self-Review Checklist

1. Spec coverage: every requirement in the design spec maps to Tasks 1–10 above.
2. No placeholders: each step includes the commands/files needed to implement and test.
3. Type consistency: models, repo, and file names used consistently above.

---

## Handoff / Execution choices

Plan complete and saved to `docs/superpowers/plans/2026-06-03-ads-automation-prd.md`. Two execution options:

1. Subagent-Driven (recommended) — run `subagent-driven-development` agent per task, review between tasks.
2. Inline Execution — I (or the `executing-plans` agent) implement tasks in this session according to the checklist.

Which approach do you want? Reply with `subagent` or `inline`.