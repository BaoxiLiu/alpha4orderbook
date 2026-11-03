"""CLI: ``python -m a4ob.cli smoke|eval``."""

from __future__ import annotations

import argparse
import json
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
    )
    print(json.dumps(result, indent=2, default=str))
    print(f"\nReport: {result['report_path']}", file=sys.stderr)
    return 0


def _cmd_eval(args: argparse.Namespace) -> int:
    """
    Eval stub: if ``--panel`` given, score baseline imbalance on that panel;
    otherwise delegates to smoke (builds panel then metrics).
    """
    import pandas as pd

    from .config import default_config_path, load_config
    from .eval.metrics import rank_ic_table
    from .factors.baseline import imbalance
    from .labels.forward import mid_forward_returns
    from .smoke import run_smoke

    if args.panel is None:
        result = run_smoke(config_path=args.config, out_dir=args.out)
        print(json.dumps({"mode": "smoke-backed-eval", **result}, indent=2, default=str))
        return 0

    cfg = load_config(args.config or default_config_path())
    panel = pd.read_parquet(args.panel)
    top_k = int(cfg["panel"]["top_k"])
    dt_s = int(cfg["panel"]["dt_seconds"])
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
    out = Path(args.out) if args.out else Path(args.panel).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    ic_path = out / "rank_ic_eval.csv"
    ic.to_csv(ic_path)
    print(json.dumps({"mode": "panel-eval", "ic_path": str(ic_path), "ic": ic.to_dict()}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="a4ob", description="alpha4orderbook CLI")
    sub = p.add_subparsers(dest="command", required=True)

    smoke = sub.add_parser("smoke", help="L0→L1→baseline IC smoke on one hour")
    smoke.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/sealed.yaml)",
    )
    smoke.add_argument("--symbol", default=None)
    smoke.add_argument("--date", default=None, help="YYYY-MM-DD")
    smoke.add_argument("--hour", default=None, help="HH")
    smoke.add_argument("--out", default=None, help="Output experiment directory")
    smoke.set_defaults(func=_cmd_smoke)

    ev = sub.add_parser("eval", help="Eval stub (panel IC or smoke-backed)")
    ev.add_argument(
        "--config",
        default=None,
        help="Path to YAML config (default: configs/sealed.yaml)",
    )
    ev.add_argument("--panel", default=None, help="Existing panel parquet")
    ev.add_argument("--out", default=None)
    ev.set_defaults(func=_cmd_eval)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
