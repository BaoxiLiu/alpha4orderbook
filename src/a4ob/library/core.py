"""build-core: correlation clustering → Core library v0."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .cluster import greedy_abs_corr_clusters
from .html_leaderboard import write_leaderboard_html
from .score import load_scoring


def build_core(
    *,
    ranking_csv: str | Path | None = None,
    corr_csv: str | Path | None = None,
    scoring_path: str | Path | None = None,
    out_dir: str | Path | None = None,
    corr_threshold: float | None = None,
) -> dict[str, Any]:
    repo = Path(__file__).resolve().parents[3]
    cfg = load_scoring(scoring_path)
    cl_cfg = cfg.get("clustering") or {}
    threshold = float(
        corr_threshold if corr_threshold is not None else cl_cfg.get("corr_threshold", 0.70)
    )

    snap = repo / "library" / "universe_latest"
    ranking_path = Path(ranking_csv) if ranking_csv else snap / "universe_ranking.csv"
    corr_path = Path(corr_csv) if corr_csv else snap / "factor_corr_avg.csv"
    if not ranking_path.is_file():
        raise FileNotFoundError(f"ranking not found: {ranking_path}; run rank-universe first")
    if not corr_path.is_file():
        raise FileNotFoundError(f"corr matrix not found: {corr_path}; run rank-universe first")

    ranking = pd.read_csv(ranking_path)
    corr = pd.read_csv(corr_path, index_col=0)
    scores = {str(r.factor): float(r.score) for r in ranking.itertuples()}
    # align corr columns
    cols = [c for c in ranking["factor"].tolist() if c in corr.columns]
    corr = corr.reindex(index=cols, columns=cols)
    clusters = greedy_abs_corr_clusters(corr, scores, threshold=threshold)
    reps = [c["representative"] for c in clusters]

    out = Path(out_dir) if out_dir else repo / "library"
    out.mkdir(parents=True, exist_ok=True)

    core_doc = {
        "schema_version": 1,
        "library": "core",
        "version": "v0",
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": cl_cfg.get("method", "greedy_abs_corr"),
        "corr_threshold": threshold,
        "n_universe": len(ranking),
        "n_clusters": len(clusters),
        "n_core": len(reps),
        "representatives": reps,
        "clusters": clusters,
        "notes": [
            "Core v0 from Phase-1 Universe on BTC/ETH/SOL × 2026-08-01..07 panels.",
            "Representative = highest composite score in each |ρ| cluster.",
            "Not production-certified; mid-return IC only (no fees/markout).",
        ],
    }
    core_yaml = out / "core_v0.yaml"
    core_yaml.write_text(yaml.safe_dump(core_doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (out / "core_v0.json").write_text(json.dumps(core_doc, indent=2, default=str), encoding="utf-8")

    # refresh leaderboard with core highlight
    meta = {
        "n_universe": len(ranking),
        "n_core": len(reps),
        "corr_threshold": threshold,
        "built_at_utc": core_doc["built_at_utc"],
    }
    html = write_leaderboard_html(
        out / "universe_leaderboard.html",
        ranking=ranking,
        meta=meta,
        core_reps=reps,
    )
    # also update latest snapshot
    snap.mkdir(parents=True, exist_ok=True)
    write_leaderboard_html(snap / "universe_leaderboard.html", ranking=ranking, meta=meta, core_reps=reps)

    summary_lines = [
        f"# Core library v0",
        "",
        f"- clusters: **{len(clusters)}** (threshold |ρ|≥{threshold})",
        f"- universe size: **{len(ranking)}**",
        f"- representatives: {', '.join(f'`{r}`' for r in reps)}",
        "",
        "## Clusters",
        "",
    ]
    for c in clusters:
        members = ", ".join(c["members"])
        summary_lines.append(
            f"- **C{c['cluster_id']}** rep=`{c['representative']}` score={c['score']:.4f} · members: {members}"
        )
    summary_path = out / "core_v0_summary.md"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    return {
        "core_yaml": str(core_yaml),
        "summary_md": str(summary_path),
        "leaderboard_html": str(html),
        "representatives": reps,
        "n_clusters": len(clusters),
        "corr_threshold": threshold,
    }
