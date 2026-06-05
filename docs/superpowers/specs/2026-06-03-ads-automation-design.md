# Ads Automation — v1 Design

Date: 2026-06-03
Project: Preschool Ads Automation (Google Ads)
Scope: Hugging Face Space deploy, CPU runtime, recommendation-and-approval automation for Google Search campaigns.

**Summary**
- Deliver a single Gradio app that monitors Google Ads campaigns, generates structured recommendations using a local MiniCPM5-1B model (GGUF via `llama-cpp-python`), and applies approved, limited safe changes (budget adjustments, pause/resume, add negative keywords).  
- App source-of-truth: SQLite. Syncs to Google Sheets for visibility.  
- Scheduler: APScheduler in-process with SQLite jobstore; daily review loop + manual runs.  
- Auth/secrets: HF Secrets for deployed Space; `.env` for local dev. Admin access via single password.

**High-level Architecture**
- Frontend: Gradio app with pages: Dashboard, Campaigns, Recommendations, Lead Manager, Audit & Logs, Settings.  
- Backend modules (Python):
  - `app/ads/`: Google Ads connector (official `google-ads` Python client) + admin OAuth flow to obtain refresh token.  
  - `app/db/`: SQLAlchemy models and repository layer (SQLite).  
  - `app/recs/`: deterministic rule engine (thresholds, smoothing) that produces candidate deltas.  
  - `app/models/`: MiniCPM5 wrapper using `llama-cpp-python` that accepts a JSON instruction and returns structured JSON recommendations.  
  - `app/scheduler/`: APScheduler bootstrap + job definitions (daily review, retry logic, on-demand runs).  
  - `scripts/`: utilities (seed demo data, sheet sync, admin tasks).

**Data Model (core tables)**
- `campaigns` {id, google_campaign_id, name, managed:bool, budget, target_cpl_override, last_synced}  
- `ad_groups` {id, campaign_id, google_ad_group_id, name}  
- `keywords` {id, ad_group_id, google_keyword_id, text, match_type, active, last_metrics}  
- `leads` {id, source, campaign_id, utm, name, phone, email, created_at, status(booked/visited/other)}  
- `recommendations` {id, timestamp, campaign_id, entity_type, action, delta (json), reason, risk, confidence, origin_rule, apply_options, approved_by, applied_by, audit_json}  
- `audit_logs` {id, user, action, payload, timestamp}

**Recommendation Pipeline**
1. Metrics ingestion: request last N days of metrics via Google Ads API (default 7/30-day windows). Store snapshots in SQLite.  
2. Rule engine: evaluate deterministic rules (3-day smoothed moving averages, min-sample guards). If a rule fires, create a candidate delta.  
3. Model prompt: build JSON-only prompt with: recent aggregates, supporting time-series summary, candidate delta, and entity metadata.  
4. MiniCPM5 (local GGUF via `llama-cpp-python`) returns structured recommendation JSON following agreed schema.  
5. Persist recommendation, send in-app notification/email/webhook.  
6. Approver (admin) reviews in Recommendations page, chooses immediate/scheduled/staged apply or rejects.  
7. If approved and auto-apply allowed, scheduler enqueues the apply job; apply executes via Google Ads client and writes audit and rollback metadata.

**Rule Defaults (v1)**
- Pause keyword: CPL > 1.5×target CPL for 3 consecutive days AND clicks ≥ 10.  
- Add negative keyword: impressions ≥ 500, clicks ≥ 20, leads = 0, CTR < 0.5% for 7 days.  
- Increase budget: CPL < 0.8×target CPL for 3 days AND leads ≥ 3 → +10% budget (cap per-campaign).  
- Decrease budget: CPL > 1.25×target CPL for 3 days AND spend ≥ $20/day → −15% budget.

**Recommendation Schema (v1)**
- `id`, `timestamp`, `campaign_id`, `campaign_name`, `entity_type`, `action`, `delta`, `estimated_impact`, `reason`, `risk`, `confidence`, `origin_rule`, `supporting_metrics`, `apply_options`, `rollback_plan`, `audit`.

**Auto-apply Safety**
- Allowed actions: budget adjustments, pause/resume, negative keyword additions only.  
- Approval required for any apply; app supports immediate, scheduled, or staged rollout (e.g., 25→50→100% over 48h).  
- All changes include rollback metadata; maintain previous setting snapshot and a reversible job.

**Model/Prompting**
- Use `Abiray/MiniCPM5-1B-GGUF` (GGUF file). Load via `llama-cpp-python` at startup; cache in Space environment.  
- Prompt must be strict: return only the `recommendation` JSON. Include a short human-readable summary for UI display.  
- Model role: generate human-friendly `reason`, `risk`, `confidence`, and `estimated_impact` text. Deterministic numbers (spend/lead deltas) come from rule engine heuristics.

**Lead Capture & Attribution**
- Primary lead capture: single landing page form that writes to app DB (captures UTM parameters).  
- Leads sync to Google Sheets (read-only audit view). Approver marks `booked` visits in Lead Manager; app updates lead status and syncs back to Sheets.

**Auth & Secrets**
- Deploy-time secrets stored in HF Secrets (Google OAuth client_id/secret, developer token, admin password). Local dev: `.env` only.  
- Admin auth: single admin password for approving changes; optional read-only viewer links.

**Deployment**
- Target: Hugging Face Space (CPU-enabled). Use `requirements.txt` including `gradio`, `sqlalchemy`, `google-ads`, `google-auth`, `apscheduler`, `llama-cpp-python`.  
- At startup: download GGUF from HF Hub if not cached, load model via `llama-cpp-python` with quantized Q4_K_M file.  
- Provide `scripts/seed_demo.py` to populate seeded demo mode and `scripts/sheet_sync.py` for manual sync.

**Testing & Demo Mode**
- Seeded demo data for presentation mode when no live campaigns are available.  
- Unit tests for rule engine, recommendation schema validation, DB migrations, and Google Ads connector mocks.

**Privacy & Safety**
- No secrets in repo. Provide clear audit trail for any change applied to Google Ads. Approver must explicitly approve before any change that modifies live campaigns.  

**Next Steps (implementation checklist)**
- [ ] Scaffold repo layout and `requirements.txt`  
- [ ] Implement SQLite schema + SQLAlchemy models  
- [ ] Implement admin OAuth flow and `google-ads` connector (read-only + mutating calls)  
- [ ] Implement rule engine and recommendation generator (model wrapper)  
- [ ] Build Gradio UI pages and flows (approve/apply)  
- [ ] Implement APScheduler loop + job persistence  
- [ ] Add Google Sheets sync and `scripts/`  
- [ ] Write README, HF Space instructions, and seeded demo data  

**Appendix — Key decisions (v1)**
- Mode: Recommendation-and-approval (no fully autonomous without approval)  
- KPI: Qualified leads / booked campus visits (CPL optimization)  
- Channels: Google Search Ads only (v1)  
- Auto-apply actions: budgets, pause/resume, negative keywords  
- Model: MiniCPM5-1B (GGUF) used for textual recommendation generation only  

---

Spec authored by: GitHub Copilot assistant (design session)

Please review this spec file and tell me if you want any edits before I write the implementation plan.