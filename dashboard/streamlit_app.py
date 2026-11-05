"""PhishGuard - link safety checker (Streamlit).

Run from the project root:  streamlit run dashboard/streamlit_app.py

Two views: a home page (enter a link, batch scan, history, about) and a separate
result page that opens after a scan. Only URL *strings* are analysed; nothing is
ever fetched, opened or rendered as a clickable link.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from app.analyzer import get_analyzer  # noqa: E402
from app.config import APP_VERSION  # noqa: E402
from dashboard import charts, theme  # noqa: E402
from dashboard.utils import MAX_BATCH_ROWS, read_urls_from_csv, results_to_frame, to_csv_bytes  # noqa: E402
from feature_engineering.extractor import InvalidURLError, load_config  # noqa: E402

st.set_page_config(page_title="PhishGuard", page_icon="\U0001F6E1️", layout="wide", initial_sidebar_state="collapsed")

DEMO_TARGETS = {
    "Try a safe link": "https://www.wikipedia.org/wiki/Computer_security",
    "Try a suspicious link": "http://bit.ly/3xYzAb9",
    "Try a phishing link": "http://paypal.secure-verify.account-update.tk/login.php?session=8f3a2c",
}
SAMPLE_CSV = ROOT / "data" / "sample_batch.csv"

st.markdown(theme.CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading model...")
def load_engine():
    return get_analyzer()


# ---- session state ----------------------------------------------------------
for key, default in (("history", []), ("result", None), ("error", None), ("url_input", ""), ("batch", None), ("view", "home")):
    st.session_state.setdefault(key, default)


def _scan(url: str) -> bool:
    """Analyse ``url``; on success store the result and switch to the result page."""
    try:
        res = load_engine().analyze(url)
    except InvalidURLError as exc:
        st.session_state["error"], st.session_state["result"] = str(exc), None
        return False
    st.session_state["error"], st.session_state["result"], st.session_state["view"] = None, res, "result"
    st.session_state["history"].insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"), "url": res["url"], "verdict": res["verdict"],
        "risk_score": res["risk_score"], "ml_confidence_pct": round(res["ml_confidence"] * 100, 1),
        "rule_score": res["rule_score"],
    })
    del st.session_state["history"][200:]
    return True


def _load_demo(url: str) -> None:
    st.session_state["url_input"] = url
    st.session_state["pending_scan"] = True


def _go_home() -> None:
    st.session_state["view"] = "home"
    st.session_state["error"] = None


def show_chart(fig, key: str) -> None:
    st.plotly_chart(fig, theme=None, key=key, config={"displayModeBar": False})


try:
    engine = load_engine()
    model_ready = True
except Exception as exc:  # noqa: BLE001
    engine, model_ready = None, False
    st.markdown(theme.alert(f"The model failed to load: {exc}"), unsafe_allow_html=True)

# a demo button was pressed on the previous run
if st.session_state.pop("pending_scan", False) and model_ready:
    _scan(st.session_state["url_input"])


# =============================================================================
# RESULT PAGE
# =============================================================================
def render_result_page(res: dict) -> None:
    with st.container(key="back"):
        st.button("← Scan another link", on_click=_go_home, key="back_btn")

    c1, c2 = st.columns([1, 1.5], gap="medium")
    with c1:
        show_chart(charts.risk_gauge(res), "gauge")
    with c2:
        st.markdown(theme.result_summary(res), unsafe_allow_html=True)

    n = len(res["indicators"])
    st.markdown(theme.section("Why this result", f"{n} warning sign{'s' if n != 1 else ''} found" if n else "nothing suspicious"),
                unsafe_allow_html=True)
    st.markdown(theme.reason_cards(res), unsafe_allow_html=True)

    st.markdown(theme.section("How the score was decided"), unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        show_chart(charts.score_breakdown(res), "score_breakdown")
    with b:
        st.markdown(theme.ml_panel(res), unsafe_allow_html=True)

    st.markdown(theme.section("Link details"), unsafe_allow_html=True)
    d1, d2 = st.columns(2, gap="medium")
    with d1:
        show_chart(charts.indicator_points(res), "indicator_points")
    with d2:
        show_chart(charts.threat_radar(res), "threat_radar")

    with st.expander("All extracted features"):
        st.markdown(theme.feature_table(res["features"], load_config()["feature_descriptions"]), unsafe_allow_html=True)

    st.download_button("Download report (JSON)", data=json.dumps(res, indent=2), file_name="phishguard_report.json",
                       mime="application/json", key="dl_report")


# =============================================================================
# HOME PAGE
# =============================================================================
def render_home_page() -> None:
    st.markdown(theme.hero(), unsafe_allow_html=True)
    st.markdown(theme.status_strip(model_ready), unsafe_allow_html=True)

    tab_scan, tab_batch, tab_hist, tab_about = st.tabs(["Scan a link", "Batch scan", "History", "About"])

    with tab_scan:
        _, mid, _ = st.columns([1, 4, 1])
        with mid:
            st.write("")
            with st.form("scan_form", border=False):
                st.text_input("Link to check", key="url_input", placeholder="Paste a link, e.g. https://example.com/login",
                              label_visibility="collapsed")
                submitted = st.form_submit_button("Scan link", disabled=not model_ready)
            if submitted:
                if _scan(st.session_state["url_input"]):
                    st.rerun()
            if st.session_state["error"]:
                st.markdown(theme.alert(f"Could not scan that link: {st.session_state['error']}"), unsafe_allow_html=True)
            st.markdown('<div class="pg-hint">Or try an example &mdash; these are made-up links, analysed as text and never opened.</div>',
                        unsafe_allow_html=True)
            with st.container(key="chips"):
                for col, (label, url) in zip(st.columns(3), DEMO_TARGETS.items()):
                    col.button(label, key=f"demo_{label}", on_click=_load_demo, args=(url,), disabled=not model_ready)
            if st.session_state["history"]:
                st.write("")
                if st.button("View last result", key="last_result"):
                    st.session_state["view"] = "result"
                    st.rerun()

    with tab_batch:
        st.markdown(theme.section("Batch scan"), unsafe_allow_html=True)
        st.markdown(theme.note(
            f"Upload a CSV with a <b>url</b> column (or one link per line). Up to {MAX_BATCH_ROWS:,} rows are analysed as text only "
            "&mdash; no link is opened."), unsafe_allow_html=True)
        st.write("")
        left, right = st.columns([3, 1], gap="medium")
        with left:
            upload = st.file_uploader("CSV file", type=["csv", "txt"], label_visibility="collapsed", key="batch_file")
        with right:
            if SAMPLE_CSV.exists():
                st.download_button("Sample CSV", data=SAMPLE_CSV.read_bytes(), file_name="sample_batch.csv", mime="text/csv", key="dl_sample")
        if upload is not None and model_ready:
            if st.button("Run batch scan", key="run_batch"):
                try:
                    urls = read_urls_from_csv(upload)[:MAX_BATCH_ROWS]
                except Exception as exc:  # noqa: BLE001
                    urls = []
                    st.markdown(theme.alert(f"Could not read the file: {exc}"), unsafe_allow_html=True)
                if urls:
                    bar = st.progress(0.0, text="Scanning...")
                    results: list = []
                    chunk = 250
                    for i in range(0, len(urls), chunk):
                        results += engine.analyze_many(urls[i:i + chunk])
                        bar.progress(min(1.0, (i + chunk) / len(urls)), text=f"Scanning... {min(i + chunk, len(urls))}/{len(urls)}")
                    bar.empty()
                    st.session_state["batch"] = {"summary": results_to_frame(urls, results),
                                                 "full": results_to_frame(urls, results, include_features=True)}
                else:
                    st.markdown(theme.alert("No links found in the uploaded file."), unsafe_allow_html=True)

        batch = st.session_state["batch"]
        if batch is None:
            st.markdown(theme.empty_state("No batch yet — upload a CSV to scan many links at once."), unsafe_allow_html=True)
        else:
            df = batch["summary"]
            counts = df["verdict"].value_counts()
            st.markdown(theme.section("Batch results"), unsafe_allow_html=True)
            st.markdown(theme.stat_tiles([
                ("Links", len(df), ""),
                ("High risk", int(counts.get("HIGH RISK", 0)), "lvl-high"),
                ("Suspicious", int(counts.get("SUSPICIOUS", 0)), "lvl-sus"),
                ("Low risk", int(counts.get("LOW RISK", 0)), "lvl-low"),
                ("Invalid", int(counts.get("INVALID", 0)), ""),
            ]), unsafe_allow_html=True)
            scored = df[df["verdict"] != "INVALID"]
            if not scored.empty:
                st.write("")
                b1, b2 = st.columns(2, gap="medium")
                with b1:
                    show_chart(charts.verdict_donut(scored), "batch_donut")
                with b2:
                    show_chart(charts.score_histogram(scored), "batch_hist")
            st.dataframe(df, hide_index=True, height=360, column_config={
                "risk_score": st.column_config.ProgressColumn("risk_score", min_value=0, max_value=100, format="%d"),
                "ml_confidence_pct": st.column_config.NumberColumn("ml_conf %", format="%.1f"),
                "url": st.column_config.TextColumn("url", width="large"),
                "indicators": st.column_config.TextColumn("indicators", width="large")})
            d1, d2, _ = st.columns([1.3, 1.5, 1.2])
            d1.download_button("Download results", data=to_csv_bytes(batch["summary"]), file_name="phishguard_results.csv",
                               mime="text/csv", key="dl_batch")
            d2.download_button("Results + features", data=to_csv_bytes(batch["full"]), file_name="phishguard_results_features.csv",
                               mime="text/csv", key="dl_batch_full")

    with tab_hist:
        st.markdown(theme.section("Scan history"), unsafe_allow_html=True)
        hist = st.session_state["history"]
        if not hist:
            st.markdown(theme.empty_state("No scans yet this session."), unsafe_allow_html=True)
        else:
            show_chart(charts.history_trend(hist), "history_trend")
            st.dataframe(pd.DataFrame(hist), hide_index=True, height=320, column_config={
                "risk_score": st.column_config.ProgressColumn("risk_score", min_value=0, max_value=100, format="%d"),
                "url": st.column_config.TextColumn("url", width="large")})
            h1, h2, _ = st.columns([1.3, 1.1, 1.6])
            h1.download_button("Download history", data=to_csv_bytes(pd.DataFrame(hist)), file_name="phishguard_history.csv",
                               mime="text/csv", key="dl_hist")
            if h2.button("Clear history", key="clear_hist"):
                st.session_state["history"] = []
                st.rerun()
            st.caption("History lives in this browser session only and is cleared when the page is reloaded.")

    with tab_about:
        st.markdown(theme.section("How it works"), unsafe_allow_html=True)
        sc = load_config()["scoring"]
        st.markdown(theme.note(
            "<b>1. Read the link as text.</b> PhishGuard measures things like length, subdomains, hyphens, keywords, and look-alike tricks. "
            "It never opens the link.<br><b>2. Two checks.</b> A RandomForest model gives a phishing probability, and a rule engine looks for known "
            "tricks (IP address as the host, brand names on the wrong domain, the <code>@</code> trick, odd domain endings).<br>"
            f"<b>3. One score.</b> Risk = {sc['ml_weight']:.2f} &times; ML score + {sc['rule_weight']:.2f} &times; rule score. "
            f"Below {sc['suspicious_min']} is low risk, {sc['suspicious_min']}&ndash;{sc['high_min'] - 1} is suspicious, "
            f"{sc['high_min']} and above is high risk."), unsafe_allow_html=True)
        if engine is not None:
            info = engine.model_info()
            m, meta = info["metrics"], info["meta"]
            st.markdown(theme.section("The model"), unsafe_allow_html=True)
            st.markdown(theme.stat_tiles([
                ("Algorithm", "Random Forest", ""),
                ("Trees", meta.get("n_estimators", "-"), ""),
                ("Training links", f'{meta.get("n_samples", 0):,}', ""),
                ("Hold-out F1", m.get("f1", "-"), ""),
                ("ROC AUC", m.get("roc_auc", "-"), ""),
            ]), unsafe_allow_html=True)
            if meta.get("dataset_is_synthetic", True):
                st.write("")
                st.markdown(theme.note(
                    "<b>Synthetic demo data.</b> The model was trained on machine-generated links, so the near-perfect scores show how well it "
                    "learned that generator &mdash; <b>not</b> real-world accuracy. Retrain on real data (for example PhishTank and Tranco) "
                    "before relying on it."), unsafe_allow_html=True)
            st.write("")
            show_chart(charts.feature_importance(info["feature_importances"]), "importance")
        st.markdown(theme.section("Privacy"), unsafe_allow_html=True)
        st.markdown(theme.note(
            "PhishGuard does <b>static text analysis only</b>. It never opens, fetches, resolves or runs a link, and links are shown as "
            "plain text, never as clickable links."), unsafe_allow_html=True)


# ---- router -----------------------------------------------------------------
if st.session_state["view"] == "result" and st.session_state["result"] is not None:
    render_result_page(st.session_state["result"])
else:
    st.session_state["view"] = "home"
    render_home_page()

st.markdown(theme.footer(APP_VERSION), unsafe_allow_html=True)
