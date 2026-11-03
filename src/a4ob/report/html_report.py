"""Self-contained HTML eval reports with Plotly charts (CDN).

Requires network once to load Plotly from cdn.plot.ly unless the browser has it
cached. Documented in README; no Python plotly dependency.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.27.0.min.js"


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.floating, float)):
        x = float(obj)
        return None if not np.isfinite(x) else x
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if obj is None or isinstance(obj, (str, bool)):
        return obj
    if pd.isna(obj):
        return None
    return str(obj)


def _df_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].astype(str)
    return _json_safe(out.to_dict(orient="records"))


def _escape(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_pack_html_report(
    path: str | Path,
    *,
    meta: dict[str, Any],
    mean_by_symbol: pd.DataFrame,
    calendar_split: pd.DataFrame,
    layering_mean: pd.DataFrame | None = None,
    layering_note: str = "",
) -> Path:
    """Pack eval HTML: IC decay, heatmap, train/test bars, quantile layering."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "meta": _json_safe(
            {
                k: meta.get(k)
                for k in (
                    "symbols",
                    "start_date",
                    "end_date",
                    "train_dates",
                    "test_dates",
                    "factor_names",
                    "dt_seconds",
                    "top_k",
                    "n_quantiles",
                    "layering_method",
                    "built_at_utc",
                    "elapsed_seconds",
                    "n_detail_rows",
                    "n_failures",
                )
                if k in meta or k in ("n_quantiles", "layering_method")
            }
        ),
        "mean_by_symbol": _df_records(mean_by_symbol),
        "calendar_split": _df_records(calendar_split),
        "layering_mean": _df_records(layering_mean) if layering_mean is not None else [],
        "layering_note": layering_note,
    }
    data_json = json.dumps(payload, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>a4ob factor pack eval</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  :root {{
    --bg: #f7f5f1;
    --ink: #1c1a17;
    --muted: #5c574e;
    --card: #fffefb;
    --line: #ddd6c8;
    --accent: #0b6e4f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 24px 28px 64px;
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
    background: radial-gradient(1200px 600px at 10% -10%, #e8f2ec 0%, transparent 55%),
                linear-gradient(180deg, #f3efe6, var(--bg));
    color: var(--ink);
  }}
  h1 {{ font-size: 1.85rem; margin: 0 0 0.25rem; letter-spacing: -0.02em; }}
  h2 {{ font-size: 1.2rem; margin: 1.6rem 0 0.5rem; color: var(--accent); }}
  .sub {{ color: var(--muted); margin-bottom: 1.2rem; }}
  .meta {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 8px 16px; padding: 14px 16px; background: var(--card);
    border: 1px solid var(--line); border-radius: 10px; margin-bottom: 18px;
    font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.86rem;
  }}
  .meta div span {{ color: var(--muted); display: block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; }}
  .chart {{
    background: var(--card); border: 1px solid var(--line); border-radius: 10px;
    padding: 8px 8px 4px; margin: 10px 0 18px; min-height: 360px;
  }}
  .note {{
    font-family: ui-sans-serif, system-ui, sans-serif; font-size: 0.9rem;
    color: var(--muted); border-left: 3px solid var(--accent); padding: 6px 12px;
    background: rgba(11,110,79,0.06); margin: 8px 0 16px;
  }}
  .row2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  @media (max-width: 960px) {{ .row2 {{ grid-template-columns: 1fr; }} }}
  footer {{ margin-top: 28px; color: var(--muted); font-size: 0.85rem; }}
</style>
</head>
<body>
  <h1>Factor pack eval</h1>
  <p class="sub">Rank IC + time-series quantile layering (分层收益). Depth L3/L5 ≠ IC quintiles.</p>
  <div class="meta" id="meta"></div>

  <h2>IC × horizon decay</h2>
  <p class="note">横轴：前瞻周期（等距类别 1s…300s，非 log）。纵轴：Mean Rank IC（Spearman，无量纲）。</p>
  <div class="chart" id="decay"></div>

  <div class="row2">
    <div>
      <h2>Heatmap — factor × horizon (mean IC)</h2>
      <div class="chart" id="heat"></div>
    </div>
    <div>
      <h2>Train vs test IC</h2>
      <p class="note">Calendar split means of per-day Rank ICs (default key horizons 1s / 5s / 60s).</p>
      <div class="chart" id="split"></div>
    </div>
  </div>

  <h2>Quantile layering (分层) — mean forward mid return</h2>
  <p class="note" id="layer-note"></p>
  <div class="chart" id="layer"></div>
  <p class="note">Long−Short 纵轴为 mid 收益比例（非 USDC）；图上刻度单位 μ=10⁻⁶。横轴前瞻周期等距类别。</p>
  <div class="chart" id="ls"></div>

  <footer>Generated by <code>python -m a4ob.cli run-eval-pack</code>. Charts: Plotly CDN.</footer>
<script>
const DATA = {data_json};

/** Equal-spaced categorical horizon labels (not log). */
function horizonCats(rows, key='horizon_s') {{
  return [...new Set((rows||[]).map(r => +r[key]).filter(x => Number.isFinite(x)))]
    .sort((a,b)=>a-b).map(h => h + 's');
}}
function hLabel(h) {{ return (+h) + 's'; }}
const X_HORIZON = {{
  title: {{text: '前瞻周期 horizon', font: {{size: 13}}}},
  type: 'category',
  categoryorder: 'array',
}};
const Y_RANK_IC = {{
  title: {{text: 'Mean Rank IC（Spearman，无量纲）', font: {{size: 13}}}},
}};
const Y_LS_MU = {{
  title: {{
    text: 'Long−Short mid return（μ）\\n无量纲比例；图上 μ = 10⁻⁶（非 USDC）',
    font: {{size: 12}},
  }},
}};
const Y_Q_MU = {{
  title: {{
    text: 'Mean forward mid return（μ）\\n无量纲比例；图上 μ = 10⁻⁶（非 USDC）',
    font: {{size: 12}},
  }},
}};

function metaHtml() {{
  const m = DATA.meta || {{}};
  const keys = ['symbols','start_date','end_date','factor_names','train_dates','test_dates',
                'n_quantiles','layering_method','dt_seconds','top_k','elapsed_seconds','built_at_utc'];
  const el = document.getElementById('meta');
  el.innerHTML = keys.filter(k => m[k] !== undefined && m[k] !== null).map(k =>
    `<div><span>${{k}}</span><strong>${{Array.isArray(m[k]) ? m[k].join(', ') : m[k]}}</strong></div>`
  ).join('');
}}

function plotDecay() {{
  const rows = DATA.mean_by_symbol || [];
  const cats = horizonCats(rows);
  const factors = [...new Set(rows.map(r => r.factor))];
  const symbols = [...new Set(rows.map(r => r.symbol))];
  const traces = [];
  const palette = ['#0b6e4f','#1d3557','#9a3412','#7c3aed','#0e7490','#b45309'];
  factors.forEach((f, fi) => {{
    symbols.forEach((s, si) => {{
      const pts = rows.filter(r => r.factor === f && r.symbol === s)
        .sort((a,b) => a.horizon_s - b.horizon_s);
      traces.push({{
        x: pts.map(p => hLabel(p.horizon_s)),
        y: pts.map(p => p.rank_ic),
        mode: 'lines+markers',
        name: f + ' · ' + s,
        line: {{ width: 2, color: palette[(fi*symbols.length + si) % palette.length] }},
      }});
    }});
  }});
  Plotly.newPlot('decay', traces, {{
    margin: {{t: 24, r: 16, b: 64, l: 72}},
    xaxis: {{...X_HORIZON, categoryarray: cats}},
    yaxis: Y_RANK_IC,
    legend: {{orientation: 'h', y: -0.28}},
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  }}, {{responsive: true, displayModeBar: false}});
}}

function plotHeat() {{
  const rows = DATA.mean_by_symbol || [];
  const map = {{}};
  rows.forEach(r => {{
    const k = r.factor + '||' + r.horizon_s;
    if (!map[k]) map[k] = {{factor: r.factor, horizon_s: r.horizon_s, sum: 0, n: 0}};
    if (r.rank_ic !== null && r.rank_ic !== undefined) {{ map[k].sum += r.rank_ic; map[k].n += 1; }}
  }});
  const agg = Object.values(map).map(x => ({{...x, ic: x.n ? x.sum/x.n : null}}));
  const factors = [...new Set(agg.map(a => a.factor))];
  const horizons = [...new Set(agg.map(a => a.horizon_s))].sort((a,b)=>a-b);
  const cats = horizons.map(hLabel);
  const z = factors.map(f => horizons.map(h => {{
    const hit = agg.find(a => a.factor === f && a.horizon_s === h);
    return hit ? hit.ic : null;
  }}));
  Plotly.newPlot('heat', [{{
    z, x: cats, y: factors, type: 'heatmap',
    colorscale: 'RdBu', zmid: 0, hoverongaps: false,
    colorbar: {{title: 'Rank IC'}},
  }}], {{
    margin: {{t: 24, r: 16, b: 64, l: 120}},
    xaxis: {{...X_HORIZON, categoryarray: cats, type: 'category'}},
    yaxis: {{title: {{text: 'factor', font: {{size: 13}}}}}},
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  }}, {{responsive: true, displayModeBar: false}});
}}

function plotSplit() {{
  const keyH = [1,5,60];
  let use = (DATA.calendar_split || []).filter(r => keyH.includes(r.horizon_s));
  if (!use.length) use = DATA.calendar_split || [];
  const factors = [...new Set(use.map(r => r.factor))];
  const train = {{ x: [], y: [], name: 'train', type: 'bar', marker: {{color: '#0b6e4f'}} }};
  const test = {{ x: [], y: [], name: 'test', type: 'bar', marker: {{color: '#9a3412'}} }};
  factors.forEach(f => {{
    const hs = [...new Set(use.filter(r => r.factor===f).map(r => r.horizon_s))].sort((a,b)=>a-b);
    hs.forEach(h => {{
      const label = f + ' @' + hLabel(h);
      train.x.push(label); test.x.push(label);
      const tr = use.find(r => r.factor===f && r.horizon_s===h && r.split==='train');
      const te = use.find(r => r.factor===f && r.horizon_s===h && r.split==='test');
      train.y.push(tr ? tr.mean_rank_ic : null);
      test.y.push(te ? te.mean_rank_ic : null);
    }});
  }});
  Plotly.newPlot('split', [train, test], {{
    barmode: 'group',
    margin: {{t: 24, r: 16, b: 90, l: 72}},
    xaxis: {{title: {{text: 'factor @ 前瞻周期', font: {{size: 13}}}}, type: 'category'}},
    yaxis: Y_RANK_IC,
    legend: {{orientation: 'h'}},
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  }}, {{responsive: true, displayModeBar: false}});
}}

function plotLayering() {{
  document.getElementById('layer-note').textContent = DATA.layering_note ||
    'TS quantiles within each symbol-day; values are equal-day means of per-day bucket returns. 收益为 mid 无量纲比例（非 USDC）；图上 μ=10⁻⁶。';
  const rows = (DATA.layering_mean || []).filter(r => r.quantile !== 'LS' && r.quantile !== null);
  const lsRows = (DATA.layering_mean || []).filter(r => r.quantile === 'LS');
  if (!rows.length) {{
    document.getElementById('layer').innerHTML = '<p class="note">No layering rows.</p>';
    document.getElementById('ls').innerHTML = '';
    return;
  }}
  const hFocus = 1;
  const factors = [...new Set(rows.map(r => r.factor))];
  const qs = [...new Set(rows.map(r => r.quantile))].filter(q => typeof q === 'number' || !isNaN(+q)).map(Number).sort((a,b)=>a-b);
  const traces = qs.map(q => {{
    const y = factors.map(f => {{
      const hits = rows.filter(r => r.factor===f && +r.quantile===q && +r.horizon_s===hFocus);
      let v = null;
      if (hits.length) {{
        v = hits.reduce((a,b)=>a+(b.mean_ret||0),0) / hits.length;
      }} else {{
        const any = rows.filter(r => r.factor===f && +r.quantile===q);
        if (any.length) v = any.reduce((a,b)=>a+(b.mean_ret||0),0) / any.length;
      }}
      return v === null ? null : v * 1e6;  // display in μ
    }});
    return {{ x: factors, y, name: 'Q'+q, type: 'bar' }};
  }});
  Plotly.newPlot('layer', traces, {{
    barmode: 'group',
    title: {{text: '分位 mean forward mid return @1s（跨币等权日均；纵轴 μ）', font: {{size: 13}}}},
    margin: {{t: 40, r: 16, b: 60, l: 72}},
    xaxis: {{title: {{text: 'factor', font: {{size: 13}}}}}},
    yaxis: Y_Q_MU,
    legend: {{orientation: 'h'}},
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  }}, {{responsive: true, displayModeBar: false}});

  const cats = horizonCats(lsRows);
  const symbols = [...new Set(lsRows.map(r => r.symbol))];
  const lsTraces = [];
  const palette = ['#0b6e4f','#1d3557','#9a3412','#7c3aed'];
  factors.forEach((f, fi) => {{
    symbols.forEach((s, si) => {{
      const pts = lsRows.filter(r => r.factor===f && r.symbol===s).sort((a,b)=>a.horizon_s-b.horizon_s);
      if (!pts.length) return;
      lsTraces.push({{
        x: pts.map(p => hLabel(p.horizon_s)),
        y: pts.map(p => (p.mean_ret == null ? null : p.mean_ret * 1e6)),
        mode: 'lines+markers',
        name: f + ' LS · ' + s,
        line: {{color: palette[(fi+si)%palette.length]}},
      }});
    }});
  }});
  Plotly.newPlot('ls', lsTraces, {{
    title: {{text: 'Long−Short Q_high − Q_low vs 前瞻周期（纵轴 μ）', font: {{size: 13}}}},
    margin: {{t: 40, r: 16, b: 64, l: 72}},
    xaxis: {{...X_HORIZON, categoryarray: cats}},
    yaxis: Y_LS_MU,
    legend: {{orientation: 'h', y: -0.28}},
    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
  }}, {{responsive: true, displayModeBar: false}});
}}

metaHtml();
plotDecay();
plotHeat();
plotSplit();
plotLayering();
</script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def write_eval_html_report(
    path: str | Path,
    *,
    meta: dict[str, Any],
    suite: dict[str, Any],
    layering_detail: pd.DataFrame | None = None,
    layering_note: str = "",
) -> Path:
    """Single-run HTML: IC decay + optional layering bars."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ic_decay = suite.get("ic_decay")
    rank_ic = suite.get("rank_ic")
    time_split = suite.get("time_split")

    # Flatten rank_ic matrix to records
    ic_records: list[dict[str, Any]] = []
    if isinstance(rank_ic, pd.DataFrame) and not rank_ic.empty:
        ic = rank_ic.reset_index()
        factor_col = "factor" if "factor" in ic.columns else ic.columns[0]
        for _, row in ic.iterrows():
            f = row[factor_col]
            for c in ic.columns:
                if c == factor_col or c.endswith("__n"):
                    continue
                # label like ret_fwd_1s
                h = None
                if isinstance(c, str) and c.startswith("ret_fwd_") and c.endswith("s"):
                    try:
                        h = int(c[len("ret_fwd_") : -1])
                    except ValueError:
                        h = None
                ic_records.append(
                    {
                        "factor": f,
                        "label": c,
                        "horizon_s": h,
                        "rank_ic": row[c],
                    }
                )

    payload = {
        "meta": _json_safe(meta),
        "ic_records": _json_safe(ic_records),
        "ic_decay": _df_records(ic_decay) if isinstance(ic_decay, pd.DataFrame) else [],
        "time_split": _df_records(time_split) if isinstance(time_split, pd.DataFrame) else [],
        "layering": _df_records(layering_detail) if layering_detail is not None else [],
        "layering_note": layering_note,
        "title": _escape(str(meta.get("factor") or meta.get("factor_spec") or "eval")),
    }
    data_json = json.dumps(payload, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>a4ob eval — {payload['title']}</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  body {{ margin:0; padding:24px; font-family: Georgia, serif; background:#f7f5f1; color:#1c1a17; }}
  h1 {{ margin-top:0; }} .note {{ color:#5c574e; border-left:3px solid #0b6e4f; padding:6px 10px; }}
  .chart {{ background:#fffefb; border:1px solid #ddd6c8; border-radius:10px; margin:12px 0; min-height:320px; padding:8px; }}
</style>
</head>
<body>
  <h1>Factor eval</h1>
  <p class="note" id="meta"></p>
  <h2>IC decay</h2>
  <div class="chart" id="decay"></div>
  <h2>Rank IC heatmap</h2>
  <div class="chart" id="heat"></div>
  <h2>Quantile layering (TS within day)</h2>
  <p class="note" id="layer-note"></p>
  <div class="chart" id="layer"></div>
  <div class="chart" id="ls"></div>
  <footer>Plotly CDN · <code>run-eval</code></footer>
<script>
const DATA = {data_json};
function hLabel(h) {{ return (+h) + 's'; }}
function horizonCats(rows, key='horizon_s') {{
  return [...new Set((rows||[]).map(r => +r[key]).filter(x => Number.isFinite(x)))]
    .sort((a,b)=>a-b).map(h => h + 's');
}}
const X_HORIZON = {{
  title: {{text: '前瞻周期 horizon', font: {{size: 13}}}},
  type: 'category', categoryorder: 'array',
}};
document.getElementById('meta').textContent =
  JSON.stringify(DATA.meta, null, 0).slice(0, 400);
document.getElementById('layer-note').textContent =
  (DATA.layering_note || '') + ' 收益为 mid 无量纲比例（非 USDC）；图上 μ=10⁻⁶。';

(function() {{
  const d = (DATA.ic_decay || []).slice().sort((a,b)=>a.horizon_s-b.horizon_s);
  const cats = horizonCats(d);
  Plotly.newPlot('decay', [{{
    x: d.map(r => hLabel(r.horizon_s)), y: d.map(r => r.rank_ic),
    mode: 'lines+markers', name: 'rank_ic', line: {{color:'#0b6e4f'}}
  }}], {{
    margin:{{t:20,b:64,l:72}},
    xaxis: {{...X_HORIZON, categoryarray: cats}},
    yaxis: {{title: {{text: 'Mean Rank IC（Spearman，无量纲）', font: {{size: 13}}}}}},
    paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)'
  }}, {{responsive:true, displayModeBar:false}});
}})();

(function() {{
  const rows = (DATA.ic_records || []).filter(r => r.horizon_s != null);
  const factors = [...new Set(rows.map(r => r.factor))];
  const horizons = [...new Set(rows.map(r => r.horizon_s))].sort((a,b)=>a-b);
  const cats = horizons.map(hLabel);
  const z = factors.map(f => horizons.map(h => {{
    const hit = rows.find(r => r.factor===f && r.horizon_s===h);
    return hit ? hit.rank_ic : null;
  }}));
  Plotly.newPlot('heat', [{{
    z, x: cats, y: factors, type:'heatmap', colorscale:'RdBu', zmid:0,
    colorbar: {{title: 'Rank IC'}},
  }}], {{
    margin:{{t:20,b:64,l:100}},
    xaxis: {{...X_HORIZON, categoryarray: cats}},
    yaxis: {{title: {{text: 'factor'}}}},
    paper_bgcolor:'rgba(0,0,0,0)'
  }}, {{responsive:true, displayModeBar:false}});
}})();

(function() {{
  const rows = (DATA.layering || []).filter(r => r.quantile !== 'LS');
  const lsRows = (DATA.layering || []).filter(r => r.quantile === 'LS')
    .slice().sort((a,b)=>a.horizon_s-b.horizon_s);
  if (!rows.length) {{ document.getElementById('layer').innerHTML = '<p>No layering.</p>'; return; }}
  const factors = [...new Set(rows.map(r => r.factor))];
  const qs = [...new Set(rows.map(r => +r.quantile))].sort((a,b)=>a-b);
  const h = 1;
  const traces = qs.map(q => ({{
    x: factors,
    y: factors.map(f => {{
      const hit = rows.find(r => r.factor===f && +r.quantile===q && +r.horizon_s===h);
      return hit && hit.mean_ret != null ? hit.mean_ret * 1e6 : null;
    }}),
    name: 'Q'+q, type: 'bar'
  }}));
  Plotly.newPlot('layer', traces, {{
    barmode:'group', margin:{{t:20,l:72}},
    yaxis: {{title: {{text: 'Mean forward mid return（μ）\\n无量纲比例；图上 μ = 10⁻⁶（非 USDC）', font: {{size: 12}}}}}},
    paper_bgcolor:'rgba(0,0,0,0)'
  }}, {{responsive:true, displayModeBar:false}});

  if (lsRows.length) {{
    const cats = horizonCats(lsRows);
    Plotly.newPlot('ls', [{{
      x: lsRows.map(r => hLabel(r.horizon_s)),
      y: lsRows.map(r => r.mean_ret == null ? null : r.mean_ret * 1e6),
      mode: 'lines+markers', name: 'LS', line: {{color:'#9a3412'}},
    }}], {{
      title: {{text: 'Long−Short Q_high − Q_low vs 前瞻周期（纵轴 μ）', font: {{size: 13}}}},
      margin: {{t:40,b:64,l:72}},
      xaxis: {{...X_HORIZON, categoryarray: cats}},
      yaxis: {{title: {{text: 'Long−Short mid return（μ）\\n无量纲比例；图上 μ = 10⁻⁶（非 USDC）', font: {{size: 12}}}}}},
      paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
    }}, {{responsive:true, displayModeBar:false}});
  }}
}})();
</script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path
