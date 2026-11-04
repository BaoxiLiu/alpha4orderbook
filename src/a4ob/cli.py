"""CLI: ``python -m a4ob.cli smoke|eval|build-panel|build-panel-range|run-eval|run-eval-pack``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path


def _cmd_smoke(args: argparse.Namespace) -> int:
    from .smoke import run_smoke

    result = run_smoke(
        config_path=args.config,
        symbol=args.symbol,
        date=args.date,
        hour=args.hour,
        out_dir=args.out,
        panel=args.panel,
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nReport: {result['report_path']}", file=sys.stderr)
    return 0


def _cmd_eval(args: argparse.Namespace) -> int:
    """
    Eval stub: score baseline imbalance on a panel path, day panel, or smoke.
    """
    import pandas as pd

    from .config import default_config_path, load_config
    from .eval.metrics import rank_ic_table
    from .factors.baseline import imbalance
    from .labels.forward import mid_forward_returns
    from .panel.build import resolve_day_panel
    from .smoke import run_smoke

    cfg = load_config(args.config or default_config_path())
    top_k = int(cfg["panel"]["top_k"])
    dt_s = int(cfg["panel"]["dt_seconds"])

    panel_path = args.panel
    if panel_path is None and args.symbol and args.date:
        found = resolve_day_panel(
            symbol=args.symbol, date=args.date, dt_seconds=dt_s, top_k=top_k
        )
        if found is not None:
            panel_path = str(found)

    if panel_path is None:
        result = run_smoke(config_path=args.config, out_dir=args.out)
        print(json.dumps({"mode": "smoke-backed-eval", **result}, indent=2, default=str))
        return 0

    panel = pd.read_parquet(panel_path)
    horizons = list(cfg["labels"]["horizons_seconds"])
    min_obs = int(cfg.get("eval", {}).get("min_obs", 30))

    if "imb_1" not in panel.columns:
        panel["imb_1"] = imbalance(panel, levels=1)
    if "imb_5" not in panel.columns:
        panel["imb_5"] = imbalance(panel, levels=min(5, top_k))
    label_cols = [f"ret_fwd_{h}s" for h in horizons]
    if any(c not in panel.columns for c in label_cols):
        labels = mid_forward_returns(panel, horizons, dt_seconds=dt_s)
        panel = pd.concat([panel, labels], axis=1)

    ic = rank_ic_table(panel, ["imb_1", "imb_5"], label_cols, min_obs=min_obs)
    out = Path(args.out) if args.out else Path(panel_path).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    ic_path = out / "rank_ic_eval.csv"
    ic.to_csv(ic_path)
    print(
        json.dumps(
            {
                "mode": "panel-eval",
                "panel_path": str(panel_path),
                "ic_path": str(ic_path),
                "n_rows": len(panel),
                "ic": ic.to_dict(),
            },
            indent=2,
        )
    )
    return 0


def _cmd_build_panel(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    from .panel.day import build_day_panel

    result = build_day_panel(
        symbol=args.symbol,
        date=args.date,
        config_path=args.config,
        hour=args.hour,
        panels_root=args.out,
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nPanel: {result['panel_path']}", file=sys.stderr)
    print(f"Manifest: {result['manifest_path']}", file=sys.stderr)
    return 0


def _cmd_run_eval(args: argparse.Namespace) -> int:
    from .eval.run_eval import run_eval

    result = run_eval(
        factor_spec=args.factor,
        symbol=args.symbol,
        date=args.date,
        config_path=args.config,
        panel_path=args.panel,
        out_dir=args.out,
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nReport: {result['report_path']}", file=sys.stderr)
    if result.get("html_report_path"):
        print(f"HTML: {result['html_report_path']}", file=sys.stderr)
    return 0


def _cmd_build_panel_range(args: argparse.Namespace) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    from .panel.range import build_panel_range

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    result = build_panel_range(
        symbols=symbols,
        start_date=args.start,
        end_date=args.end,
        config_path=args.config,
        panels_root=args.out,
        workers=args.workers,
        skip_fresh=not args.force,
    )
    # Compact stdout (omit huge hour_logs inside nested results)
    compact = {k: v for k, v in result.items() if k != "results"}
    compact["results"] = [
        {
            "symbol": r.get("symbol"),
            "date": r.get("date"),
            "status": r.get("status"),
            "n_rows": r.get("n_rows"),
            "elapsed_seconds": r.get("elapsed_seconds"),
            "error": r.get("error"),
        }
        for r in result.get("results", [])
    ]
    print(json.dumps(compact, indent=2, default=str))
    return 0 if result.get("n_error", 0) == 0 else 1


def _cmd_run_eval_pack(args: argparse.Namespace) -> int:
    from .eval.pack import run_eval_pack

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    factors = [f.strip() for f in args.factors.split(",") if f.strip()]
    result = run_eval_pack(
        factor_specs=factors,
        symbols=symbols,
        start_date=args.start,
        end_date=args.end,
        config_path=args.config,
        panels_root=args.panels_root,
        out_dir=args.out,
        train_days=args.train_days,
        test_days=args.test_days,
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nReport: {result['report_path']}", file=sys.stderr)
    if result.get("html_report_path"):
        print(f"HTML: {result['html_report_path']}", file=sys.stderr)
    return 0


def _cmd_rank_universe(args: argparse.Namespace) -> int:
    from .library.rank import rank_universe

    symbols = (
        [s.strip() for s in args.symbols.split(",") if s.strip()]
        if args.symbols
        else None
    )
    factors = (
        [f.strip() for f in args.factors.split(",") if f.strip()]
        if args.factors
        else None
    )
    result = rank_universe(
        factors=factors,
        symbols=symbols,
        start_date=args.start,
        end_date=args.end,
        scoring_path=args.scoring,
        panels_root=args.panels_root,
        out_dir=args.out,
        train_days=args.train_days,
        test_days=args.test_days,
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nLeaderboard: {result['leaderboard_html']}", file=sys.stderr)
    return 0


def _cmd_build_core(args: argparse.Namespace) -> int:
    from .library.core import build_core

    result = build_core(
        ranking_csv=args.ranking,
        corr_csv=args.corr,
        scoring_path=args.scoring,
        out_dir=args.out,
        corr_threshold=args.corr_threshold,
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nCore: {result['core_yaml']}", file=sys.stderr)
    return 0


def _cmd_enrich_trades(args: argparse.Namespace) -> int:
    """Join CryptoHFTData trades onto existing day panels → trades_features.parquet."""
    from .factors.nh_features import enrich_day_trades_features
    from .panel.range import iter_dates

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    dates = list(iter_dates(args.start, args.end))
    rows = []
    for sym in symbols:
        for d in dates:
            rows.append(
                enrich_day_trades_features(
                    symbol=sym,
                    date=d,
                    panels_root=args.panels_root,
                    data_root=args.data_root,
                    config_path=args.config,
                    force=bool(args.force),
                )
            )
            print(json.dumps(rows[-1], default=str), flush=True)
    ok = sum(1 for r in rows if r.get("status") in ("ok", "exists"))
    print(json.dumps({"n": len(rows), "ok": ok}, indent=2), file=sys.stderr)
    return 0 if ok == len(rows) else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="a4ob", description="alpha4orderbook CLI")
    sub = p.add_subparsers(dest="command", required=True)

    smoke = sub.add_parser("smoke", help="L0→L1→baseline IC smoke (hour or day panel)")
    smoke.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/sealed.yaml)",
    )
    smoke.add_argument("--symbol", default=None)
    smoke.add_argument("--date", default=None, help="YYYY-MM-DD")
    smoke.add_argument("--hour", default=None, help="HH (force hour rebuild)")
    smoke.add_argument("--panel", default=None, help="Existing panel parquet to score")
    smoke.add_argument("--out", default=None, help="Output experiment directory")
    smoke.set_defaults(func=_cmd_smoke)

    ev = sub.add_parser("eval", help="Eval stub (panel IC / day panel / smoke-backed)")
    ev.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/sealed.yaml)",
    )
    ev.add_argument("--panel", default=None, help="Existing panel parquet")
    ev.add_argument("--symbol", default=None, help="Resolve day panel under panels/")
    ev.add_argument("--date", default=None, help="YYYY-MM-DD with --symbol")
    ev.add_argument("--out", default=None)
    ev.set_defaults(func=_cmd_eval)

    bp = sub.add_parser(
        "build-panel",
        help="Build (symbol, day) 1s top-K research panel + manifest",
    )
    bp.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/sealed.yaml)",
    )
    bp.add_argument("--symbol", required=True)
    bp.add_argument("--date", required=True, help="YYYY-MM-DD UTC")
    bp.add_argument(
        "--hour",
        default=None,
        help="Optional HH — debug single-hour build instead of full day",
    )
    bp.add_argument(
        "--out",
        default=None,
        help="Panels root (default: repo panels/)",
    )
    bp.set_defaults(func=_cmd_build_panel)

    re_ = sub.add_parser(
        "run-eval",
        help="Factor Spec → day panel → Rank IC report (M3)",
    )
    re_.add_argument(
        "--config",
        default=None,
        help="Path to YAML run config (default: configs/sealed.yaml)",
    )
    re_.add_argument(
        "--factor",
        required=True,
        help="Factor Spec YAML (e.g. configs/factors/imbalance.yaml)",
    )
    re_.add_argument("--symbol", required=True)
    re_.add_argument("--date", required=True, help="YYYY-MM-DD UTC")
    re_.add_argument(
        "--panel",
        default=None,
        help="Optional panel parquet (default: resolve day panel under panels/)",
    )
    re_.add_argument("--out", default=None, help="Experiment output directory")
    re_.set_defaults(func=_cmd_run_eval)

    bpr = sub.add_parser(
        "build-panel-range",
        help="Parallel (symbol, day) panel builds over a date range (M4)",
    )
    bpr.add_argument("--config", default=None)
    bpr.add_argument(
        "--symbols",
        required=True,
        help="Comma-separated symbols, e.g. BTCUSDC,ETHUSDC,SOLUSDC",
    )
    bpr.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    bpr.add_argument("--end", required=True, help="YYYY-MM-DD inclusive")
    bpr.add_argument("--workers", type=int, default=3)
    bpr.add_argument(
        "--force",
        action="store_true",
        help="Rebuild even when manifest config_hash matches",
    )
    bpr.add_argument("--out", default=None, help="Panels root (default: repo panels/)")
    bpr.set_defaults(func=_cmd_build_panel_range)

    pack = sub.add_parser(
        "run-eval-pack",
        help="Factor pack IC matrix across symbols × days (M4)",
    )
    pack.add_argument("--config", default=None)
    pack.add_argument(
        "--factors",
        required=True,
        help="Comma-separated Factor Spec paths",
    )
    pack.add_argument(
        "--symbols",
        required=True,
        help="Comma-separated symbols",
    )
    pack.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    pack.add_argument("--end", required=True, help="YYYY-MM-DD inclusive")
    pack.add_argument("--train-days", type=int, default=5)
    pack.add_argument("--test-days", type=int, default=2)
    pack.add_argument("--panels-root", default=None)
    pack.add_argument("--out", default=None, help="Experiment output directory")
    pack.set_defaults(func=_cmd_run_eval_pack)

    ru = sub.add_parser(
        "rank-universe",
        help="Dual-library Phase 1: score/rank Universe factors on day panels",
    )
    ru.add_argument("--scoring", default=None, help="configs/scoring.yaml")
    ru.add_argument(
        "--factors",
        default=None,
        help="Comma-separated Spec paths (default: configs/factors/universe/*.yaml)",
    )
    ru.add_argument("--symbols", default=None, help="Comma-separated symbols")
    ru.add_argument("--start", default=None, help="YYYY-MM-DD inclusive")
    ru.add_argument("--end", default=None, help="YYYY-MM-DD inclusive")
    ru.add_argument("--train-days", type=int, default=None)
    ru.add_argument("--test-days", type=int, default=None)
    ru.add_argument("--panels-root", default=None)
    ru.add_argument("--out", default=None, help="Output directory under library/runs/")
    ru.set_defaults(func=_cmd_rank_universe)

    bc = sub.add_parser(
        "build-core",
        help="Dual-library Phase 1: cluster Universe → Core v0 representatives",
    )
    bc.add_argument("--scoring", default=None)
    bc.add_argument("--ranking", default=None, help="universe_ranking.csv")
    bc.add_argument("--corr", default=None, help="factor_corr_avg.csv")
    bc.add_argument("--corr-threshold", type=float, default=None)
    bc.add_argument("--out", default=None, help="default: library/")
    bc.set_defaults(func=_cmd_build_core)

    et = sub.add_parser(
        "enrich-trades",
        help="Add NH trades features sidecar next to existing day panels (no book rebuild)",
    )
    et.add_argument("--config", default=None)
    et.add_argument("--symbols", required=True, help="Comma-separated")
    et.add_argument("--start", required=True)
    et.add_argument("--end", required=True)
    et.add_argument("--panels-root", default=None)
    et.add_argument("--data-root", default=None, help="CryptoHFTData raw root")
    et.add_argument("--force", action="store_true")
    et.set_defaults(func=_cmd_enrich_trades)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
