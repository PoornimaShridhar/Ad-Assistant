# Ads Automation Hackathon Implementation Plan

> **For agentic workers:** REQUIRED: Use the `subagent-driven-development` agent (recommended) or `executing-plans` agent to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Google Ads recommendation dashboard for a preschool that monitors campaign performance, generates AI-powered recommendations using MiniCPM5-1B, and allows a human to review, approve, or reject recommendations. Deploy as a Gradio app on a Hugging Face Space (CPU) with SQLite as the source of truth.

**Architecture:** Single Gradio application. Google Ads metrics are imported into SQLite. A deterministic rule engine identifies opportunities and issues. MiniCPM5 generates human-readable explanations for recommendations. Recommendations are displayed in a dashboard where users can approve or reject them. No automatic ad changes are performed.

**Tech Stack:** Python 3.10+, Gradio, SQLAlchemy, google-ads, pandas, llama-cpp-python, pytest, python-dotenv.

---

### Task 1: Scaffold Project Layout

**Files:**

* Create: `app/__init__.py`

* Create: `app/main.py`

* Create: `app/ads/connector.py`

* Create: `app/db/models.py`

* Create: `app/db/repo.py`

* Create: `app/recs/rules.py`

* Create: `app/recs/generate.py`

* Create: `app/models/llm.py`

* Create: `app/ui/dashboard.py`

* Create: `app/ui/recommendations.py`

* Create: `scripts/seed_demo.py`

* Create: `requirements.txt`

* Create: `README.md`

* [ ] Step 1: Create repository structure and install dependencies.

Requirements:

```text
gradio
sqlalchemy
google-ads
pandas
llama-cpp-python
pytest
python-dotenv
requests
```

Verify:

```bash
python -m venv .venv
pip install -r requirements.txt
```

Expected: all packages install successfully.

* [ ] Step 2: Verify imports.

```bash
python -c "import app; print('scaffold ok')"
```

Expected:

```text
scaffold ok
```

---

### Task 2: SQLite Models

**Files:**

* Modify: `app/db/models.py`

* Modify: `app/db/repo.py`

* [ ] Step 1: Create `Campaign` model.

Fields:

```python
id
google_campaign_id
name
budget
spend
clicks
impressions
ctr
leads
cpl
last_synced
```

* [ ] Step 2: Create `Recommendation` model.

Fields:

```python
id
campaign_id
recommendation_type
action
reason
status
created_at
```

Status values:

```text
Pending
Approved
Rejected
```

* [ ] Step 3: Create database initialization helper.

Verify:

```bash
python -c "from app.db.repo import init_db; init_db(); print('db ok')"
```

Expected:

```text
db ok
```

---

### Task 3: Google Ads Read-Only Connector

**Files:**

* Modify: `app/ads/connector.py`

* [ ] Step 1: Implement:

```python
list_campaigns()
```

Returns:

```python
[
  {
    "id": "...",
    "name": "...",
    "budget": ...
  }
]
```

* [ ] Step 2: Implement:

```python
get_campaign_metrics()
```

Returns:

```python
[
  {
    "campaign_id": "...",
    "spend": ...,
    "clicks": ...,
    "impressions": ...,
    "ctr": ...,
    "leads": ...,
    "cpl": ...
  }
]
```

* [ ] Step 3: Add mock tests for connector responses.

Expected:

```bash
$env:PYTHONPATH="."
pytest
```

passes.

---

### Task 4: Rule Engine

**Files:**

* Modify: `app/recs/rules.py`

* [ ] Step 1: Implement High CPL Rule.

Condition:

```text
CPL > Target CPL × 1.5
```

Recommendation:

```text
Reduce budget allocation
```

* [ ] Step 2: Implement Strong Campaign Rule.

Condition:

```text
CPL < Target CPL × 0.8
```

Recommendation:

```text
Increase budget allocation
```

* [ ] Step 3: Implement Low CTR Rule.

Condition:

```text
CTR < 2%
```

Recommendation:

```text
Review ad copy and keywords
```

* [ ] Step 4: Return structured recommendation objects.

Example:

```json
{
  "campaign":"Preschool Search",
  "type":"high_cpl",
  "action":"reduce_budget"
}
```

---

### Task 5: MiniCPM5 Recommendation Generator

**Files:**

* Modify: `app/models/llm.py`

* Modify: `app/recs/generate.py`

* [ ] Step 1: Load MiniCPM5 GGUF using `llama-cpp-python`.

Implement:

```python
load_model()
```

* [ ] Step 2: Generate explanations from recommendation payloads.

Input:

```json
{
  "campaign":"Preschool Search",
  "cpl":42,
  "target_cpl":20,
  "action":"reduce_budget"
}
```

Output:

```text
This campaign's cost per lead is significantly above target. Consider reducing budget allocation until conversion efficiency improves.
```

* [ ] Step 3: Validate output and provide fallback text if model response fails.

* [ ] Step 4: Add mocked tests.

---

### Task 6: Dashboard UI

**Files:**

* Modify: `app/main.py`

* Modify: `app/ui/dashboard.py`

* Modify: `app/ui/recommendations.py`

* [ ] Step 1: Build Campaign Dashboard.

Display:

| Campaign | Spend | Leads | CPL | CTR |
| -------- | ----- | ----- | --- | --- |

* [ ] Step 2: Add dashboard summary cards.

Examples:

```text
Total Spend
Total Leads
Average CPL
Active Campaigns
```

* [ ] Step 3: Add Recommendations Page.

Display:

| Campaign | Recommendation | Status |
| -------- | -------------- | ------ |

* [ ] Step 4: Add Approve button.

Updates:

```text
Pending → Approved
```

* [ ] Step 5: Add Reject button.

Updates:

```text
Pending → Rejected
```

Verification:

```bash
python app/main.py
```

Expected:

Dashboard loads successfully.

---

### Task 7: Demo Data

**Files:**

* Modify: `scripts/seed_demo.py`

* [ ] Step 1: Generate sample campaigns.

Create:

```text
5 campaigns
```

* [ ] Step 2: Generate synthetic metrics.

Create:

```text
30 days of data
```

* [ ] Step 3: Generate recommendations.

Ensure dashboard always contains examples.

Verification:

```bash
python scripts/seed_demo.py
```

Expected:

Database populated with demo content.

---

### Task 8: End-to-End Testing

**Files:**

* Create: `tests/test_e2e.py`

* [ ] Step 1: Seed demo data.

* [ ] Step 2: Run rule engine.

* [ ] Step 3: Generate MiniCPM explanations using mocked model.

* [ ] Step 4: Verify recommendations appear in database.

Expected:

```bash
pytest
```

passes.

---

### Task 9: Hugging Face Space Deployment

**Files:**

* Modify: `README.md`

* Modify: `requirements.txt`

* [ ] Step 1: Add deployment instructions.

* [ ] Step 2: Document model download procedure.

* [ ] Step 3: Document local development workflow.

Example:

```bash
pip install -r requirements.txt
python scripts/seed_demo.py
python app/main.py
```

Expected:

Developer can run locally and deploy to HF Spaces.

---

## Self-Review Checklist

1. Google Ads metrics can be viewed.
2. Rule engine generates recommendations.
3. MiniCPM generates explanations.
4. Recommendations can be approved/rejected.
5. Dashboard works with seeded demo data.
6. No automatic campaign modifications.
7. No scheduler required.
8. No Google Sheets integration required.
9. Deployable on Hugging Face Spaces.

---

## Handoff / Execution Choices

Plan complete. Two execution options:

1. Subagent-Driven (recommended) — run `subagent-driven-development` task-by-task.
2. Inline Execution — implement tasks sequentially in a single session.

Recommended for hackathon: **subagent-driven-development**.
