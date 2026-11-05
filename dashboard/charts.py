"""Plotly figures styled for the soft dark-sage PhishGuard theme."""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from dashboard.theme import (AMBER, BORDER, BORDER_HI, DIM, GREEN, GREEN_DARK, GREEN_DEEP, LEVEL_COLORS, RED, SURFACE2, TEXT)
from feature_engineering.extractor import load_config

FONT = "Inter, system-ui, sans-serif"
GRID = "#1f2b25"
SEV_COLORS = {"low": GREEN, "medium": AMBER, "high": RED}
FILLS = {GREEN: "rgba(127,207,155,0.16)", AMBER: "rgba(224,178,90,0.16)", RED: "rgba(224,123,123,0.18)"}


def _style(fig: go.Figure, title: str = "", height: int = 300, legend: bool = False) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left", font=dict(family=FONT, size=14, color=TEXT)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        font=dict(family=FONT, color=TEXT, size=12), showlegend=legend,
        margin=dict(l=14, r=34, t=48, b=16),
        hoverlabel=dict(bgcolor=SURFACE2, bordercolor=BORDER_HI, font=dict(family=FONT, color=TEXT, size=12)),
        legend=dict(font=dict(color=DIM, size=12), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=BORDER_HI, linecolor=BORDER, tickfont=dict(color=DIM, size=11), automargin=True)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=BORDER_HI, linecolor=BORDER, tickfont=dict(color=DIM, size=11), automargin=True)
    return fig


def risk_gauge(res: dict[str, Any]) -> go.Figure:
    sb = res["score_breakdown"]
    color = LEVEL_COLORS[res["verdict"]]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=res["risk_score"],
        number=dict(font=dict(family=FONT, size=64, color=color), suffix=""),
        gauge=dict(
            axis=dict(range=[0, 100], tickvals=[0, sb["suspicious_min"], sb["high_min"], 100], tickfont=dict(color=DIM, size=11), tickcolor=BORDER_HI),
            bar=dict(color=color, thickness=0.28), bgcolor="rgba(0,0,0,0)", borderwidth=0,
            steps=[dict(range=[0, sb["suspicious_min"]], color="rgba(127,207,155,0.10)"),
                   dict(range=[sb["suspicious_min"], sb["high_min"]], color="rgba(224,178,90,0.10)"),
                   dict(range=[sb["high_min"], 100], color="rgba(224,123,123,0.12)")])))
    fig.add_annotation(text="risk score out of 100", x=0.5, y=0.12, xref="paper", yref="paper", showarrow=False,
                       font=dict(family=FONT, size=12, color=DIM))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=290, margin=dict(l=24, r=24, t=30, b=10), font=dict(family=FONT, color=TEXT))
    return fig


def score_breakdown(res: dict[str, Any]) -> go.Figure:
    sb = res["score_breakdown"]
    color = LEVEL_COLORS[res["verdict"]]
    labels = ["Final risk", "Rule engine", "ML model"]
    values = [res["risk_score"], sb["rule_score"], sb["ml_score"]]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", marker=dict(color=[color, GREEN_DARK, GREEN_DEEP], cornerradius=6),
        text=[f"{v:.0f}" for v in values], textposition="outside", textfont=dict(color=TEXT, family=FONT),
        hovertemplate="%{y}: %{x:.1f}/100<extra></extra>"))
    for x, lab in ((sb["suspicious_min"], "Suspicious"), (sb["high_min"], "High")):
        fig.add_vline(x=x, line=dict(color=BORDER_HI, width=1, dash="dot"), annotation_text=lab,
                      annotation_font=dict(color=DIM, size=10), annotation_position="top")
    _style(fig, "How the score is built", 290)
    fig.update_layout(bargap=0.4)
    fig.update_xaxes(range=[0, 112], title=None)
    fig.update_yaxes(autorange="reversed")
    return fig


def indicator_points(res: dict[str, Any]) -> go.Figure:
    inds = res["indicators"]
    fig = go.Figure()
    if inds:
        inds = sorted(inds, key=lambda i: i["points"])
        fig.add_trace(go.Bar(
            x=[i["points"] for i in inds], y=[i["title"] for i in inds], orientation="h",
            marker=dict(color=[SEV_COLORS[i["severity"]] for i in inds], cornerradius=6),
            text=[f'+{i["points"]}' for i in inds], textposition="outside", textfont=dict(color=TEXT, family=FONT),
            hovertext=[i["detail"] for i in inds], hovertemplate="%{y}<br>%{hovertext}<extra></extra>"))
        fig.update_xaxes(range=[0, max(i["points"] for i in inds) * 1.25])
    else:
        fig.add_annotation(text="No warning signs found", showarrow=False, font=dict(color=GREEN, size=14, family=FONT))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
    _style(fig, "Points added by each warning sign", max(260, 80 + 36 * max(len(inds), 1)))
    fig.update_layout(bargap=0.4)
    return fig


def threat_radar(res: dict[str, Any]) -> go.Figure:
    caps = load_config()["radar_caps"]
    f = res["features"]
    axes = list(caps)
    vals = [min(f[a] / caps[a], 1.0) for a in axes]
    labels = [a.replace("num_", "").replace("_", " ") for a in axes]
    color = LEVEL_COLORS[res["verdict"]]
    fig = go.Figure(go.Scatterpolar(
        r=vals + vals[:1], theta=labels + labels[:1], fill="toself", line=dict(color=color, width=2), fillcolor=FILLS[color],
        hovertemplate="%{theta}: %{r:.0%} of alert level<extra></extra>"))
    fig.update_layout(polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0, 1], showticklabels=False, gridcolor=GRID, linecolor=BORDER),
        angularaxis=dict(gridcolor=GRID, linecolor=BORDER, tickfont=dict(color=DIM, size=11, family=FONT))))
    return _style(fig, "URL feature profile", 340)


def feature_importance(importances: dict[str, float], top: int = 12) -> go.Figure:
    items = sorted(importances.items(), key=lambda kv: kv[1])[-top:]
    fig = go.Figure(go.Bar(
        x=[v for _, v in items], y=[k for k, _ in items], orientation="h",
        marker=dict(color=GREEN_DEEP, cornerradius=5), hovertemplate="%{y}: %{x:.3f}<extra></extra>"))
    _style(fig, "Which features the model relies on most", 400)
    fig.update_layout(bargap=0.35)
    return fig


def verdict_donut(df: pd.DataFrame) -> go.Figure:
    order = ["LOW RISK", "SUSPICIOUS", "HIGH RISK"]
    names = ["Low risk", "Suspicious", "High risk"]
    counts = [int((df["verdict"] == v).sum()) for v in order]
    fig = go.Figure(go.Pie(
        labels=names, values=counts, hole=0.64, sort=False, marker=dict(colors=[GREEN, AMBER, RED], line=dict(color="#0f1512", width=3)),
        textinfo="value", textfont=dict(color="#0f1512", family=FONT, size=13),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>"))
    fig.add_annotation(text=f"{sum(counts)}<br><span style='font-size:11px;color:{DIM}'>links</span>", showarrow=False,
                       font=dict(size=24, color=TEXT, family=FONT))
    return _style(fig, "Verdicts", 320, legend=True)


def score_histogram(df: pd.DataFrame) -> go.Figure:
    scores = df["risk_score"].dropna()
    fig = go.Figure(go.Histogram(x=scores, xbins=dict(start=0, end=100, size=5), marker=dict(color=GREEN_DEEP, cornerradius=4),
                                 hovertemplate="score %{x}: %{y} links<extra></extra>"))
    cfg = load_config()["scoring"]
    for x in (cfg["suspicious_min"], cfg["high_min"]):
        fig.add_vline(x=x, line=dict(color=BORDER_HI, width=1, dash="dot"))
    _style(fig, "Risk score distribution", 320)
    fig.update_layout(bargap=0.12)
    fig.update_xaxes(range=[0, 100])
    return fig


def history_trend(history: list[dict[str, Any]]) -> go.Figure:
    df = pd.DataFrame(history).iloc[::-1].reset_index(drop=True)
    fig = go.Figure(go.Scatter(
        x=list(range(1, len(df) + 1)), y=df["risk_score"], mode="lines+markers",
        line=dict(color=GREEN_DARK, width=2), marker=dict(size=11, color=[LEVEL_COLORS[v] for v in df["verdict"]], line=dict(color="#0f1512", width=2)),
        text=df["url"], hovertemplate="scan #%{x}: %{y}/100<br>%{text}<extra></extra>"))
    cfg = load_config()["scoring"]
    for y in (cfg["suspicious_min"], cfg["high_min"]):
        fig.add_hline(y=y, line=dict(color=BORDER_HI, width=1, dash="dot"))
    _style(fig, "Risk score per scan", 300)
    fig.update_yaxes(range=[0, 105])
    fig.update_xaxes(title=None, dtick=1)
    return fig
