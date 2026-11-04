"""Universe leaderboard HTML — fully self-contained, static table (no CDN / no JS required)."""

from __future__ import annotations

import html as html_lib
from pathlib import Path
from typing import Any

import pandas as pd


def _fmt(v: Any) -> str:
    if v is None or (isinstance(v, float) and (v != v)):  # NaN
        return ""
    if isinstance(v, bool):
        return "yes" if v else ""
    if isinstance(v, (int,)):
        return str(v)
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def write_leaderboard_html(
    path: str | Path,
    *,
    ranking: pd.DataFrame,
    meta: dict[str, Any],
    core_reps: list[str] | None = None,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    core_set = set(core_reps or [])
    rows = ranking.copy().reset_index(drop=True)
    if "score" in rows.columns:
        rows = rows.sort_values("score", ascending=False).reset_index(drop=True)
    if "rank" not in rows.columns:
        rows.insert(0, "rank", range(1, len(rows) + 1))
    else:
        rows["rank"] = range(1, len(rows) + 1)

    cols = [
        c
        for c in [
            "rank",
            "factor",
            "score",
            "mean_ic_primary",
            "mean_ls_primary",
            "cross_sign_agree",
            "train_ic_primary",
            "test_ic_primary",
            "coverage",
        ]
        if c in rows.columns
    ]
    # ensure factor/score present
    for need in ("rank", "factor", "score"):
        if need not in cols and need in rows.columns:
            cols.insert(0 if need == "rank" else len(cols), need)

    max_score = float(rows["score"].max()) if len(rows) and "score" in rows.columns else 1.0
    if not (max_score > 0):
        max_score = 1.0

    # static bar chart (top 20)
    bar_rows = []
    for _, r in rows.head(20).iterrows():
        factor = str(r.get("factor", ""))
        score = float(r.get("score", 0) or 0)
        is_core = factor in core_set
        width = 100.0 * score / max_score
        bar_rows.append(
            f'<div class="bar-row">'
            f'<div class="bar-label" title="{html_lib.escape(factor)}">{html_lib.escape(factor)}</div>'
            f'<div class="bar-track"><div class="bar-fill{" core" if is_core else ""}" style="width:{width:.2f}%"></div></div>'
            f'<div class="bar-val">{score:.3f}</div></div>'
        )

    # static table body
    th = "".join(f"<th>{html_lib.escape(c)}</th>" for c in cols + ["in_core"])
    trs = []
    for _, r in rows.iterrows():
        factor = str(r.get("factor", ""))
        is_core = factor in core_set
        cls = ' class="core"' if is_core else ""
        cells = "".join(f"<td>{html_lib.escape(_fmt(r.get(c)))}</td>" for c in cols)
        cells += f"<td>{'yes' if is_core else ''}</td>"
        trs.append(f"<tr{cls}>{cells}</tr>")

    meta_lines = []
    for k, v in (meta or {}).items():
        meta_lines.append(f"{k}: {v}")
    meta_txt = html_lib.escape("\n".join(meta_lines))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>a4ob Universe leaderboard</title>
<style>
  :root {{
    --ink:#1c1a17; --muted:#5c574e; --line:#ddd6c8; --paper:#fffefb;
    --bg:#f4f1ea; --core:#0b6e4f; --bar:#1d3557; --th:#e8f2ec;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:24px; font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Songti SC", serif;
         background: linear-gradient(165deg, #f7f3ea 0%, #ebe4d6 45%, #e4ece7 100%); color:var(--ink); }}
  h1 {{ margin:0 0 8px; font-size:1.75rem; letter-spacing:-0.02em; }}
  .note {{ color:var(--muted); margin:0 0 16px; font-size:0.95rem; max-width:72ch; }}
  .meta {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:0.78rem;
           background:var(--paper); border:1px solid var(--line); padding:10px 12px; border-radius:8px;
           white-space:pre-wrap; word-break:break-word; margin-bottom:16px; }}
  .chart-wrap {{ background:var(--paper); border:1px solid var(--line); border-radius:10px;
                 padding:16px 16px 8px; margin:0 0 20px; }}
  .chart-title {{ font-size:0.9rem; color:var(--muted); margin:0 0 12px; }}
  .bars {{ display:flex; flex-direction:column; gap:6px; }}
  .bar-row {{ display:grid; grid-template-columns: minmax(140px, 220px) 1fr 64px; gap:10px; align-items:center; }}
  .bar-label {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.78rem;
                overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .bar-track {{ height:14px; background:#efe9dc; border-radius:4px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:4px; background:var(--bar); min-width:2px; }}
  .bar-fill.core {{ background:var(--core); }}
  .bar-val {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.75rem; text-align:right; }}
  .legend {{ font-size:0.8rem; color:var(--muted); margin-top:10px; }}
  .legend span.core {{ color:var(--core); font-weight:600; }}
  table {{ border-collapse:collapse; width:100%; background:var(--paper);
           font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.82rem; }}
  th, td {{ border:1px solid var(--line); padding:6px 8px; text-align:right; }}
  th {{ background:var(--th); text-align:left; position:sticky; top:0; }}
  td:nth-child(1), td:nth-child(2), th:nth-child(1), th:nth-child(2) {{ text-align:left; }}
  tr.core {{ background:#e7f6ef; }}
  .scroll {{ max-height:70vh; overflow:auto; border:1px solid var(--line); border-radius:8px; }}
</style>
</head>
<body>
  <h1>Universe leaderboard</h1>
  <p class="note">One Universe table (Core ⊆ Universe). Column <code>in_core</code> = <strong>yes</strong> for Core v0 representatives; blank otherwise. Green rows = Core. Composite from IC / decay / cross-symbol / train−test / layering LS / coverage. <strong>Static HTML</strong> — no CDN / no JS.</p>
  <div class="meta">{meta_txt}</div>
  <div class="chart-wrap">
    <p class="chart-title">Top-20 composite score</p>
    <div class="bars">
{chr(10).join(bar_rows)}
    </div>
    <p class="legend"><span class="core">■ Core</span> · ■ Universe-only</p>
  </div>
  <div class="scroll">
    <table>
      <thead><tr>{th}</tr></thead>
      <tbody>
{chr(10).join(trs)}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def write_core_leaderboard_html(
    path: str | Path,
    *,
    ranking: pd.DataFrame,
    meta: dict[str, Any],
    core_reps: list[str] | None = None,
) -> Path:
    """Core-only static leaderboard (subset of Universe, ranked by score)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = ranking.copy().reset_index(drop=True)
    if core_reps:
        core_set = set(core_reps)
        rows = rows[rows["factor"].astype(str).isin(core_set)].copy()
    elif "in_core" in rows.columns:
        rows = rows[rows["in_core"].astype(str).str.lower().isin(["yes", "true", "1"])].copy()
    else:
        raise ValueError("write_core_leaderboard_html needs core_reps or ranking.in_core")

    if "score" in rows.columns:
        rows = rows.sort_values("score", ascending=False).reset_index(drop=True)
    rows["rank"] = range(1, len(rows) + 1)
    rows["universe_rank"] = (
        ranking.set_index("factor")["rank"].reindex(rows["factor"]).to_numpy()
        if "rank" in ranking.columns
        else [""] * len(rows)
    )

    cols = [
        c
        for c in [
            "rank",
            "factor",
            "score",
            "mean_ic_primary",
            "mean_ls_primary",
            "cross_sign_agree",
            "train_ic_primary",
            "test_ic_primary",
            "coverage",
            "universe_rank",
        ]
        if c in rows.columns
    ]

    max_score = float(rows["score"].max()) if len(rows) and "score" in rows.columns else 1.0
    if not (max_score > 0):
        max_score = 1.0

    bar_rows = []
    for _, r in rows.head(min(20, len(rows))).iterrows():
        factor = str(r.get("factor", ""))
        score = float(r.get("score", 0) or 0)
        width = 100.0 * score / max_score
        bar_rows.append(
            f'<div class="bar-row">'
            f'<div class="bar-label" title="{html_lib.escape(factor)}">{html_lib.escape(factor)}</div>'
            f'<div class="bar-track"><div class="bar-fill core" style="width:{width:.2f}%"></div></div>'
            f'<div class="bar-val">{score:.3f}</div></div>'
        )

    th = "".join(f"<th>{html_lib.escape(c)}</th>" for c in cols)
    trs = []
    for _, r in rows.iterrows():
        cells = "".join(f"<td>{html_lib.escape(_fmt(r.get(c)))}</td>" for c in cols)
        trs.append(f'<tr class="core">{cells}</tr>')

    meta_lines = [f"{k}: {v}" for k, v in (meta or {}).items()]
    meta_txt = html_lib.escape("\n".join(meta_lines))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>a4ob Core leaderboard</title>
<style>
  :root {{
    --ink:#1c1a17; --muted:#5c574e; --line:#ddd6c8; --paper:#fffefb;
    --bg:#f4f1ea; --core:#0b6e4f; --bar:#1d3557; --th:#e8f2ec;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:24px; font-family: "Iowan Old Style", "Palatino Linotype", Palatino, "Songti SC", serif;
         background: linear-gradient(165deg, #eef6f1 0%, #ebe4d6 45%, #f7f3ea 100%); color:var(--ink); }}
  h1 {{ margin:0 0 8px; font-size:1.75rem; letter-spacing:-0.02em; }}
  .note {{ color:var(--muted); margin:0 0 16px; font-size:0.95rem; max-width:72ch; }}
  .meta {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size:0.78rem;
           background:var(--paper); border:1px solid var(--line); padding:10px 12px; border-radius:8px;
           white-space:pre-wrap; word-break:break-word; margin-bottom:16px; }}
  .chart-wrap {{ background:var(--paper); border:1px solid var(--line); border-radius:10px;
                 padding:16px 16px 8px; margin:0 0 20px; }}
  .chart-title {{ font-size:0.9rem; color:var(--muted); margin:0 0 12px; }}
  .bars {{ display:flex; flex-direction:column; gap:6px; }}
  .bar-row {{ display:grid; grid-template-columns: minmax(140px, 220px) 1fr 64px; gap:10px; align-items:center; }}
  .bar-label {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.78rem;
                overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .bar-track {{ height:14px; background:#efe9dc; border-radius:4px; overflow:hidden; }}
  .bar-fill {{ height:100%; border-radius:4px; background:var(--bar); min-width:2px; }}
  .bar-fill.core {{ background:var(--core); }}
  .bar-val {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.75rem; text-align:right; }}
  .legend {{ font-size:0.8rem; color:var(--muted); margin-top:10px; }}
  .legend span.core {{ color:var(--core); font-weight:600; }}
  table {{ border-collapse:collapse; width:100%; background:var(--paper);
           font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.82rem; }}
  th, td {{ border:1px solid var(--line); padding:6px 8px; text-align:right; }}
  th {{ background:var(--th); text-align:left; position:sticky; top:0; }}
  td:nth-child(1), td:nth-child(2), th:nth-child(1), th:nth-child(2) {{ text-align:left; }}
  tr.core {{ background:#e7f6ef; }}
  .scroll {{ max-height:70vh; overflow:auto; border:1px solid var(--line); border-radius:8px; }}
</style>
</head>
<body>
  <h1>Core leaderboard</h1>
  <p class="note">Core v0 representatives only (orthogonal subset of Universe, |ρ|≥threshold). Rows ranked by Universe composite score. <code>universe_rank</code> is the factor's rank in the full Universe table. <strong>Static HTML</strong> — no CDN / no JS.</p>
  <div class="meta">{meta_txt}</div>
  <div class="chart-wrap">
    <p class="chart-title">Top-{min(20, len(rows))} Core composite score</p>
    <div class="bars">
{chr(10).join(bar_rows)}
    </div>
    <p class="legend"><span class="core">■ Core representatives</span></p>
  </div>
  <div class="scroll">
    <table>
      <thead><tr>{th}</tr></thead>
      <tbody>
{chr(10).join(trs)}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path
