"""PhishGuard theme: soft dark-sage styling + small HTML component builders.

All dynamic text is passed through ``html.escape`` - submitted URLs are
untrusted strings and must never be rendered as live markup or links.
"""
from __future__ import annotations

from html import escape
from typing import Any

# ---- palette (shared with charts.py) ---------------------------------------
BG = "#0f1512"
SURFACE = "#161e1a"
SURFACE2 = "#1b2520"
BORDER = "#26332c"
BORDER_HI = "#34463c"
TEXT = "#e6ece8"
DIM = "#8c9a92"
GREEN = "#7fcf9b"
GREEN_DEEP = "#4f9a6c"
GREEN_DARK = "#2d5a40"
AMBER = "#e0b25a"
RED = "#e07b7b"

LEVEL_COLORS = {"LOW RISK": GREEN, "SUSPICIOUS": AMBER, "HIGH RISK": RED}
LEVEL_CLASS = {"LOW RISK": "lvl-low", "SUSPICIOUS": "lvl-sus", "HIGH RISK": "lvl-high"}
SEVERITY_CLASS = {"low": "lvl-low", "medium": "lvl-sus", "high": "lvl-high"}
VERDICT_TEXT = {
    "LOW RISK": "No strong warning signs were found in this link.",
    "SUSPICIOUS": "This link has some warning signs. Be careful before opening it.",
    "HIGH RISK": "This link looks like phishing. Do not enter any details on it.",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --bg:#0f1512; --surface:#161e1a; --surface2:#1b2520; --border:#26332c; --border2:#34463c;
  --text:#e6ece8; --dim:#8c9a92; --green:#7fcf9b; --green-deep:#4f9a6c; --green-dark:#2d5a40;
  --amber:#e0b25a; --red:#e07b7b;
  --sans:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,Consolas,monospace;
}

/* ---------- shell ---------- */
html, body, .stApp{ background:var(--bg); color:var(--text); font-family:var(--sans); }
.stApp{ background:radial-gradient(900px 420px at 50% -10%, rgba(127,207,155,.07), transparent 65%), var(--bg); }
header[data-testid="stHeader"]{ background:transparent; }
[data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer{ display:none !important; }
.block-container{ max-width:980px; padding-top:2rem; padding-bottom:3rem; }
h1,h2,h3,h4,p,li,span,label,div{ font-family:var(--sans); }
::selection{ background:rgba(127,207,155,.28); }
* { scrollbar-width:thin; scrollbar-color:var(--border2) var(--bg); }

/* ---------- hero ---------- */
.pg-hero{ text-align:center; padding:46px 0 10px; }
.pg-logo{ font-size:clamp(34px,6vw,50px); font-weight:700; letter-spacing:-.02em; color:var(--text); line-height:1.1; }
.pg-logo span{ color:var(--green); }
.pg-tag{ margin-top:12px; font-size:16px; color:var(--dim); }
.pg-status{ display:flex; flex-wrap:wrap; justify-content:center; gap:6px 22px; margin:18px 0 6px; font-size:12.5px; color:var(--dim); }
.pg-dot{ display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--green); margin-right:7px; vertical-align:middle; opacity:.9; }
.pg-dot.off{ background:var(--red); }
.pg-hint{ text-align:center; font-size:12.5px; color:var(--dim); margin:16px 0 8px; }

/* ---------- inputs ---------- */
[data-testid="stTextInputRootElement"], div[data-testid="stTextInput"] div[data-baseweb="input"], div[data-testid="stTextInput"] div[data-baseweb="base-input"]{
  background:var(--surface) !important; border-radius:12px !important; }
[data-testid="stTextInputRootElement"], div[data-testid="stTextInput"] div[data-baseweb="input"]{
  border:1px solid var(--border2) !important; transition:border-color .2s ease, box-shadow .2s ease; }
[data-testid="stTextInputRootElement"]:focus-within, div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within{
  border-color:var(--green-deep) !important; box-shadow:0 0 0 3px rgba(127,207,155,.12) !important; }
[data-testid="stTextInputField"], div[data-testid="stTextInput"] input{ font-family:var(--mono) !important; font-size:14.5px !important;
  color:var(--text) !important; caret-color:var(--green); padding:14px 16px !important; background:transparent !important; }
[data-testid="stTextInputField"]::placeholder, div[data-testid="stTextInput"] input::placeholder{ color:#5c6b63 !important; opacity:1; }
[data-testid="InputInstructions"]{ display:none !important; }
[data-testid="stForm"]{ border:none !important; padding:0 !important; background:transparent !important; }

/* ---------- buttons ---------- */
.stButton > button, [data-testid="stFormSubmitButton"] > button, [data-testid="stDownloadButton"] > button{
  font-family:var(--sans) !important; font-weight:600 !important; font-size:14px !important; color:var(--text) !important;
  background:var(--surface2) !important; border:1px solid var(--border2) !important; border-radius:10px !important;
  padding:.6rem 1.4rem !important; transition:all .18s ease; }
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover{
  border-color:var(--green-deep) !important; background:#202c26 !important; transform:translateY(-1px); }
[data-testid="stFormSubmitButton"] > button{ background:var(--green-deep) !important; border-color:var(--green-deep) !important; color:#f4fbf6 !important; }
[data-testid="stFormSubmitButton"] > button:hover{ background:#5aab7a !important; border-color:#5aab7a !important; box-shadow:0 6px 18px rgba(79,154,108,.28); transform:translateY(-1px); }
[data-testid="stElementContainer"]:has([data-testid="stFormSubmitButton"]), .element-container:has([data-testid="stFormSubmitButton"]){ width:100% !important; }
[data-testid="stFormSubmitButton"]{ display:flex; width:100%; }
[data-testid="stFormSubmitButton"] > button{ width:100%; }
.st-key-chips [data-testid="stElementContainer"], .st-key-chips .element-container, .st-key-chips [data-testid="stButton"], .st-key-chips .stButton{ width:100% !important; }
.st-key-chips .stButton > button, .st-key-chips [data-testid="stButton"] > button{ width:100%; font-size:12.5px !important; font-weight:500 !important;
  color:var(--dim) !important; background:transparent !important; padding:.4rem .5rem !important; white-space:nowrap; }
.st-key-chips .stButton > button:hover{ color:var(--text) !important; }
.st-key-back .stButton > button{ background:transparent !important; border-color:var(--border) !important; color:var(--dim) !important; padding:.45rem 1rem !important; }
.st-key-back .stButton > button:hover{ color:var(--text) !important; border-color:var(--border2) !important; }

/* ---------- tabs ---------- */
[data-baseweb="tab-list"]{ gap:4px; border-bottom:1px solid var(--border); justify-content:center; }
button[data-baseweb="tab"]{ font-family:var(--sans) !important; color:var(--dim) !important; background:transparent !important; padding:10px 18px !important; transition:color .15s ease; }
button[data-baseweb="tab"]:hover{ color:var(--text) !important; }
button[data-baseweb="tab"][aria-selected="true"]{ color:var(--green) !important; }
button[data-baseweb="tab"] p{ font-size:14px; font-weight:500; color:inherit !important; }
[data-baseweb="tab-highlight"]{ background:var(--green) !important; height:2px !important; }
[data-baseweb="tab-border"]{ background:transparent !important; }

/* ---------- section heading ---------- */
.pg-h{ margin:34px 0 14px; font-size:17px; font-weight:600; color:var(--text); }
.pg-h small{ font-size:13px; font-weight:400; color:var(--dim); margin-left:8px; }

/* ---------- cards ---------- */
.pg-card{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:20px 22px; transition:border-color .2s ease; }
.pg-card:hover{ border-color:var(--border2); }
.pg-label{ font-size:12px; color:var(--dim); margin-bottom:5px; }
.pg-value{ font-size:26px; font-weight:600; color:var(--text); line-height:1.2; }
.pg-value small{ font-size:14px; color:var(--dim); font-weight:400; }
.pg-grid{ display:grid; gap:14px; }
.pg-g2{ grid-template-columns:repeat(2,minmax(0,1fr)); }
.pg-g3{ grid-template-columns:repeat(3,minmax(0,1fr)); }
.pg-g4{ grid-template-columns:repeat(4,minmax(0,1fr)); }
.pg-g5{ grid-template-columns:repeat(5,minmax(0,1fr)); }
@media (max-width:820px){ .pg-g3,.pg-g4,.pg-g5{ grid-template-columns:repeat(2,minmax(0,1fr)); } .pg-g2{ grid-template-columns:1fr; } }
.lvl-low{ --lvl:var(--green); } .lvl-sus{ --lvl:var(--amber); } .lvl-high{ --lvl:var(--red); }
.pg-badge{ display:inline-flex; align-items:center; gap:8px; font-weight:600; font-size:13px; color:var(--lvl);
  background:color-mix(in srgb, var(--lvl) 12%, transparent); border:1px solid color-mix(in srgb, var(--lvl) 35%, transparent);
  padding:5px 13px; border-radius:999px; }
.pg-badge::before{ content:''; width:7px; height:7px; border-radius:50%; background:var(--lvl); }
.pg-value.lvl-text{ color:var(--lvl); }

/* ---------- result summary ---------- */
.pg-summary h2{ margin:14px 0 6px; font-size:24px; font-weight:600; color:var(--text); line-height:1.3; }
.pg-summary p{ margin:0 0 18px; color:var(--dim); font-size:14.5px; }
.pg-url{ font-family:var(--mono); font-size:13px; color:var(--text); word-break:break-all; padding:11px 14px; background:var(--bg);
  border:1px solid var(--border); border-radius:10px; margin-bottom:6px; }
.pg-mini{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-top:6px; }
.pg-mini > div{ background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:11px 14px; }
.pg-mini .pg-value{ font-size:20px; }

/* ---------- reason cards ---------- */
.pg-reasons{ display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:12px; }
.pg-reason{ display:flex; gap:13px; align-items:flex-start; padding:15px 16px; background:var(--surface); border:1px solid var(--border);
  border-radius:12px; transition:all .18s ease; }
.pg-reason:hover{ border-color:color-mix(in srgb, var(--lvl) 45%, var(--border)); transform:translateY(-1px); }
.pg-reason .dot{ width:9px; height:9px; border-radius:50%; background:var(--lvl); margin-top:6px; flex:none; }
.pg-reason .ttl{ font-weight:600; font-size:14px; color:var(--text); }
.pg-reason .dsc{ color:var(--dim); font-size:13px; margin-top:3px; word-break:break-word; }
.pg-reason .pts{ margin-left:auto; font-size:12px; color:var(--lvl); background:color-mix(in srgb, var(--lvl) 12%, transparent); padding:2px 9px; border-radius:999px; white-space:nowrap; align-self:flex-start; }

/* ---------- ML drivers ---------- */
.pg-drv{ display:grid; grid-template-columns:190px 1fr 52px; gap:12px; align-items:center; font-size:12.5px; padding:6px 0; }
.pg-drv .n{ color:var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-family:var(--mono); font-size:12px; }
.pg-drv .b{ height:7px; background:var(--surface2); border-radius:999px; position:relative; overflow:hidden; }
.pg-drv .b > i{ position:absolute; left:0; top:0; bottom:0; background:var(--c); border-radius:999px; }
.pg-drv .p{ text-align:right; color:var(--c); font-weight:600; }

/* ---------- tables ---------- */
.pg-table{ width:100%; border-collapse:collapse; font-size:13px; }
.pg-table th{ text-align:left; font-weight:500; font-size:12px; color:var(--dim); padding:6px 10px 10px; border-bottom:1px solid var(--border2); }
.pg-table td{ padding:8px 10px; border-bottom:1px solid var(--border); vertical-align:top; }
.pg-table tr:hover td{ background:rgba(127,207,155,.04); }
.pg-table td.k{ font-family:var(--mono); font-size:12px; white-space:nowrap; }
.pg-table td.v{ color:var(--green); text-align:right; font-weight:600; white-space:nowrap; }
.pg-table td.v.flag{ color:var(--amber); }
.pg-table td.d{ color:var(--dim); font-size:12px; }
.pg-table-wrap{ overflow-x:auto; }

/* ---------- notices ---------- */
.pg-alert{ border:1px solid color-mix(in srgb, var(--red) 40%, transparent); background:color-mix(in srgb, var(--red) 8%, transparent);
  color:#f3d3d3; padding:12px 16px; border-radius:10px; font-size:14px; margin:14px 0; }
.pg-note{ border:1px solid var(--border); background:var(--surface); color:var(--dim); padding:14px 18px; border-radius:12px; font-size:13.5px; line-height:1.65; }
.pg-note b{ color:var(--text); font-weight:600; }
.pg-note code{ font-family:var(--mono); font-size:12px; color:var(--green); }
.pg-empty{ text-align:center; color:var(--dim); font-size:14px; padding:38px 0; border:1px dashed var(--border2); border-radius:14px; margin-top:26px; }
.pg-foot{ margin-top:50px; padding-top:16px; border-top:1px solid var(--border); text-align:center; color:#5f6e66; font-size:12px; }

/* ---------- streamlit widget polish ---------- */
[data-testid="stFileUploaderDropzone"]{ background:var(--surface) !important; border:1px dashed var(--border2) !important; border-radius:12px !important; }
[data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--green-deep) !important; }
[data-testid="stDataFrame"]{ border:1px solid var(--border); border-radius:12px; overflow:hidden; }
[data-testid="stPlotlyChart"]{ border:1px solid var(--border); background:var(--surface); padding:6px 8px; border-radius:14px; }
[data-testid="stExpander"]{ border:1px solid var(--border) !important; border-radius:12px !important; background:var(--surface); }
[data-testid="stExpander"] summary p{ font-weight:500; }
[data-testid="stCaptionContainer"], .stCaption{ color:var(--dim) !important; font-size:12.5px !important; }
[data-testid="stAlert"]{ border-radius:10px; }
label, [data-testid="stWidgetLabel"] p{ color:var(--dim) !important; font-size:13px !important; }

@media (prefers-reduced-motion: reduce){ *{ animation:none !important; transition:none !important; } }
</style>
"""


def h(markup: str) -> str:
    """Collapse indentation/newlines so Markdown never treats the HTML as a code block."""
    return "".join(line.strip() for line in markup.strip().splitlines())


def esc(value: Any) -> str:
    return escape(str(value), quote=True)


def level_class(verdict: str) -> str:
    return LEVEL_CLASS.get(verdict, "lvl-low")


def _fmt(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:.3f}".rstrip("0").rstrip(".")


# ---- components ------------------------------------------------------------
def hero() -> str:
    return h("""
    <div class="pg-hero">
      <div class="pg-logo">Phish<span>Guard</span></div>
      <div class="pg-tag">Check a link before you click it.</div>
    </div>""")


def status_strip(model_ready: bool = True) -> str:
    on = "" if model_ready else " off"
    items = [("Engine", "online"), ("Model", "ready"), ("Scanner", "ready")] if model_ready else \
            [("Engine", "offline"), ("Model", "not loaded"), ("Scanner", "unavailable")]
    cells = "".join(f'<div><span class="pg-dot{on}"></span>{k} {v}</div>' for k, v in items)
    return f'<div class="pg-status">{cells}</div>'


def section(title: str, sub: str = "") -> str:
    small = f"<small>{esc(sub)}</small>" if sub else ""
    return f'<div class="pg-h">{esc(title)}{small}</div>'


def result_summary(res: dict[str, Any]) -> str:
    v = res["verdict"]
    return h(f"""
    <div class="pg-card pg-summary {level_class(v)}">
      <div class="pg-label">Link scanned</div>
      <div class="pg-url">{esc(res["url"])}</div>
      <span class="pg-badge">{esc(v.title())}</span>
      <h2>{esc(VERDICT_TEXT[v])}</h2>
      <p>The score combines a machine-learning prediction with a set of security rules. Only the text of the link was analysed &mdash; it was never opened.</p>
      <div class="pg-mini">
        <div><div class="pg-label">ML prediction</div><div class="pg-value">{esc(res["ml_prediction"].title())}</div></div>
        <div><div class="pg-label">ML confidence</div><div class="pg-value">{res["ml_confidence"] * 100:.1f}<small>%</small></div></div>
        <div><div class="pg-label">Rule score</div><div class="pg-value">{res["rule_score"]}<small> / 100</small></div></div>
      </div>
    </div>""")


def reason_cards(res: dict[str, Any]) -> str:
    if not res["indicators"]:
        return h("""<div class="pg-reasons"><div class="pg-reason lvl-low"><div class="dot"></div>
        <div><div class="ttl">No warning signs</div><div class="dsc">None of the monitored phishing signals were found in this link.</div></div></div></div>""")
    cards = "".join(
        f'<div class="pg-reason {SEVERITY_CLASS[i["severity"]]}"><div class="dot"></div>'
        f'<div><div class="ttl">{esc(i["title"])}</div><div class="dsc">{esc(i["detail"])}</div></div>'
        f'<div class="pts">+{i["points"]}</div></div>' for i in res["indicators"])
    return f'<div class="pg-reasons">{cards}</div>'


def ml_panel(res: dict[str, Any]) -> str:
    drivers = res.get("ml_drivers", [])
    top = max((abs(d["impact"]) for d in drivers), default=1) or 1
    rows = ""
    for d in drivers:
        color = "var(--red)" if d["impact"] > 0 else "var(--green)"
        val = d["value"]
        val = int(val) if float(val).is_integer() else round(val, 2)
        rows += (f'<div class="pg-drv" style="--c:{color}"><div class="n" title="{esc(d["feature"])}">{esc(d["feature"])} = {esc(val)}</div>'
                 f'<div class="b"><i style="width:{abs(d["impact"]) / top * 100:.0f}%"></i></div>'
                 f'<div class="p">{d["impact"]:+.1f}</div></div>')
    if not rows:
        rows = '<div style="color:var(--dim);font-size:13px">No single feature moves the model output noticeably.</div>'
    return h(f"""
    <div class="pg-card">
      <div class="pg-label">What influenced the model most</div>
      <div style="color:var(--dim);font-size:12.5px;margin:2px 0 12px">Red pushes toward phishing, green toward safe (percentage points).</div>
      {rows}
    </div>""")


_FLAG_FEATURES = {"has_ip_domain", "has_at_symbol", "suspicious_tld", "is_shortener", "has_punycode", "has_port",
                  "double_slash_in_path", "brand_in_host", "brand_in_path"}


def feature_table(features: dict[str, float], descriptions: dict[str, str]) -> str:
    def flagged(k: str, v: float) -> bool:
        return bool((k in _FLAG_FEATURES and v) or (k == "has_https" and not v) or (k == "num_suspicious_keywords" and v))

    items = list(features.items())
    half = (len(items) + 1) // 2

    def table(chunk: list[tuple[str, float]]) -> str:
        rows = "".join(
            f'<tr><td class="k">{esc(k)}</td><td class="v{" flag" if flagged(k, v) else ""}">{esc(_fmt(v))}</td>'
            f'<td class="d">{esc(descriptions.get(k, ""))}</td></tr>' for k, v in chunk)
        return (f'<div class="pg-card pg-table-wrap"><table class="pg-table"><thead><tr><th>Feature</th><th style="text-align:right">Value</th>'
                f'<th>Meaning</th></tr></thead><tbody>{rows}</tbody></table></div>')

    return f'<div class="pg-grid pg-g2">{table(items[:half])}{table(items[half:])}</div>'


def stat_tiles(stats: list[tuple[str, Any, str]]) -> str:
    """stats: (label, value, level_class or '')."""
    n = len(stats)
    cells = "".join(
        f'<div class="pg-card {cls}"><div class="pg-label">{esc(lbl)}</div>'
        f'<div class="pg-value{" lvl-text" if cls else ""}">{esc(val)}</div></div>' for lbl, val, cls in stats)
    return f'<div class="pg-grid pg-g{min(n, 5)}">{cells}</div>'


def alert(message: str) -> str:
    return f'<div class="pg-alert">{esc(message)}</div>'


def note(markup_safe: str) -> str:
    """``markup_safe`` must already be escaped / trusted static HTML."""
    return f'<div class="pg-note">{markup_safe}</div>'


def empty_state(text: str) -> str:
    return f'<div class="pg-empty">{esc(text)}</div>'


def footer(version: str) -> str:
    return (f'<div class="pg-foot">PhishGuard v{esc(version)} &nbsp;&middot;&nbsp; Analyses the text of a URL only &nbsp;&middot;&nbsp; '
            f'Nothing is ever opened or fetched</div>')
