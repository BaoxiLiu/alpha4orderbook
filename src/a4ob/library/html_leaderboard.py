"""Universe leaderboard HTML (Plotly CDN)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ..report.html_report import PLOTLY_CDN, _json_safe


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
    rows = ranking.copy()
    if "factor" in rows.columns:
        rows["in_core"] = rows["factor"].isin(core_set)
    payload = {
        "meta": _json_safe(meta),
        "ranking": _json_safe(rows.to_dict(orient="records")),
        "core": list(core_set),
    }
    data = json.dumps(payload, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>a4ob Universe leaderboard</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  body {{ margin:0; padding:24px; font-family: Georgia, "Songti SC", serif; background:#f4f1ea; color:#1c1a17; }}
  h1 {{ margin:0 0 8px; }} .note {{ color:#5c574e; margin-bottom:16px; }}
  table {{ border-collapse: collapse; width:100%; background:#fffefb; font-family: ui-sans-serif, system-ui, sans-serif; font-size:0.85rem; }}
  th, td {{ border:1px solid #ddd6c8; padding:6px 8px; text-align:right; }}
  th {{ background:#e8f2ec; text-align:left; }} td:first-child, th:first-child {{ text-align:left; }}
  tr.core {{ background:#e7f6ef; }}
  .chart {{ background:#fffefb; border:1px solid #ddd6c8; border-radius:10px; margin:16px 0; min-height:420px; }}
</style>
</head>
<body>
  <h1>Universe leaderboard</h1>
  <p class="note">Dual-library Phase 1 · composite score from IC / decay / cross-symbol / train−test / layering LS / coverage. Core reps highlighted.</p>
  <div id="meta" class="note"></div>
  <div class="chart" id="bar"></div>
  <table id="tbl"></table>
<script>
const DATA = {data};
document.getElementById('meta').textContent = JSON.stringify(DATA.meta);
const rows = (DATA.ranking||[]).slice().sort((a,b)=>(b.score||0)-(a.score||0));
const top = rows.slice(0, 20);
Plotly.newPlot('bar', [{{
  x: top.map(r => r.factor),
  y: top.map(r => r.score),
  type: 'bar',
  marker: {{ color: top.map(r => (DATA.core||[]).includes(r.factor) ? '#0b6e4f' : '#1d3557') }},
}}], {{
  margin: {{t:24,b:100,l:56}},
  yaxis: {{title: 'composite score'}},
  xaxis: {{title: 'factor', tickangle: -35}},
  paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
}}, {{responsive:true, displayModeBar:false}});

const cols = ['rank','factor','score','mean_ic_primary','mean_ls_primary','cross_sign_agree','train_ic_primary','test_ic_primary','in_core'];
let h = '<tr>'+cols.map(c=>'<th>'+c+'</th>').join('')+'</tr>';
rows.forEach((r,i) => {{
  const cls = (DATA.core||[]).includes(r.factor) ? ' class="core"' : '';
  h += '<tr'+cls+'>' + cols.map(c => {{
    let v = c==='rank' ? (i+1) : r[c];
    if (typeof v === 'number') v = Number.isFinite(v) ? v.toPrecision(4) : '';
    return '<td>'+(v??'')+'</td>';
  }}).join('') + '</tr>';
}});
document.getElementById('tbl').innerHTML = h;
</script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path
