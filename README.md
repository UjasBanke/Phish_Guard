# PhishGuard — Hybrid Phishing URL Detection & Risk Analysis

PhishGuard analyses a URL **as a string** (it never visits, resolves or executes it) and returns
**LOW RISK / SUSPICIOUS / HIGH RISK** with a 0–100 score and plain-language reasons. It combines a
RandomForest classifier with a rule engine, exposed through a FastAPI service and a dark
"threat detection console" Streamlit dashboard.

```
HIGH RISK — 92/100

Reasons:
- Impersonates paypal on an unrelated domain
- Suspicious keywords: login, verify, account, secure
- Suspicious TLD ".tk"
- Connection is not encrypted (HTTP)
```

> **Synthetic data notice:** the bundled dataset and model are **synthetic/demo**. The ~99 % hold-out
> score reflects the generator's patterns, not real-world accuracy. See `data/DATASET_README.md`.

## Quick start (Windows)
```bat
setup_windows.bat        :: venv + install + train (once)
run_dashboard.bat        :: http://localhost:8501
run_api.bat              :: http://127.0.0.1:8000/docs
```
Requires Python 3.11+.

## Quick start (any OS)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python train.py                                  # optional: model is already included
streamlit run dashboard/streamlit_app.py
uvicorn app.main:app --reload
```

## API
```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/analyze -H "Content-Type: application/json" \
     -d '{"url": "http://paypal.secure-verify.tk/login"}'
```
Response fields: `risk_score`, `verdict`, `ml_prediction`, `ml_confidence` (0–1), `ml_phishing_probability`,
`rule_score`, `score_breakdown`, `indicators[]`, `reasons[]`, `explanation`, `features{}`, `ml_drivers[]`.
Invalid input (empty, too long, non-http scheme) returns HTTP 422.

## How scoring works
`risk = 0.6 × ML probability (0–100) + 0.4 × rule score (0–100)`; LOW < 35, SUSPICIOUS 35–64, HIGH ≥ 65.
Weights, thresholds, keywords, TLDs and brands live in `feature_engineering/feature_config.json`.
Features (28): lengths, dots/hyphens/digits, subdomains, HTTPS, IP host, `@`, keywords, special
characters, query params, domain/path entropy, suspicious TLD, shortener, punycode, port, brand
impersonation, and more.

## Dashboard
Scanner (threat meter, target analysis, threat cards, Plotly charts, feature table, JSON export),
batch CSV scanner with download, session scan history, and a system tab with model metrics.
Batch CSV: a `url` column, or one URL per line (`data/sample_batch.csv`).

## Project layout
```
app/                 FastAPI, analyzer, rules, training
feature_engineering/ extractor + feature_config.json
dashboard/           Streamlit app, theme, charts
models/              phishguard_rf.pkl, metrics.json
data/                synthetic dataset + generator + sample batch CSV
docs/  train.py
```
See `docs/architecture.md` and `docs/interview_questions.md`.

## Safety & limitations
* No network access to submitted URLs. URLs are HTML-escaped and never rendered as links; CSV exports neutralise formula injection.
* Lexical analysis only — no WHOIS, certificates, reputation feeds or page content. Not a substitute for a production security product.
* Load only pickles you trust. If the scikit-learn version differs, the model retrains automatically.
