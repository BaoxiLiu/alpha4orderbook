"""In-memory L2 MBP book (snapshot + level updates). MIT-friendly slim API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass
class TopLevel:
    price: float
    qty: float


class L2Book:
    """
    Multi-level bid/ask maps keyed by price.

    Semantics (Binance-style L2 MBP):
    - quantity == 0 deletes the level
    - snapshot replaces the entire book
    """

    __slots__ = ("bids", "asks", "last_update_id", "ready")

    def __init__(self) -> None:
        self.bids: dict[float, float] = {}
        self.asks: dict[float, float] = {}
        self.last_update_id: int | None = None
        self.ready: bool = False

    def copy(self) -> "L2Book":
        other = L2Book()
        other.bids = dict(self.bids)
        other.asks = dict(self.asks)
        other.last_update_id = self.last_update_id
        other.ready = self.ready
        return other

    def clear(self) -> None:
        self.bids.clear()
        self.asks.clear()
        self.last_update_id = None
        self.ready = False

    def apply_snapshot(
        self,
        levels: Iterable[tuple[str, float, float]],
        *,
        last_update_id: int | None,
    ) -> None:
        """Replace book. ``levels`` are ``(side, price, qty)`` with side in {bid, ask}."""
        self.bids.clear()
        self.asks.clear()
        for side, price, qty in levels:
            if not np.isfinite(price) or not np.isfinite(qty) or qty <= 0:
                continue
            book = self.bids if side == "bid" else self.asks
            book[float(price)] = float(qty)
        self.last_update_id = int(last_update_id) if last_update_id is not None else None
        self.ready = bool(self.bids and self.asks)

    def apply_level(self, side: str, price: float, qty: float) -> None:
        if not np.isfinite(price):
            return
        book = self.bids if side == "bid" else self.asks
        price_f = float(price)
        if (not np.isfinite(qty)) or qty <= 0:
            book.pop(price_f, None)
        else:
            book[price_f] = float(qty)

    def best_bid(self) -> TopLevel | None:
        if not self.bids:
            return None
        p = max(self.bids)
        return TopLevel(p, self.bids[p])

    def best_ask(self) -> TopLevel | None:
        if not self.asks:
            return None
        p = min(self.asks)
        return TopLevel(p, self.asks[p])

    def mid(self) -> float | None:
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return 0.5 * (bb.price + ba.price)

    def spread(self) -> float | None:
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return ba.price - bb.price

    def top_k(self, k: int) -> dict[str, float]:
        """Flat dict: bid_px_0..k-1, bid_sz_0.., ask_px_0.., ask_sz_0.. plus mid/spread."""
        out: dict[str, float] = {}
        bid_prices = sorted(self.bids.keys(), reverse=True)[:k]
        ask_prices = sorted(self.asks.keys())[:k]
        for i in range(k):
            if i < len(bid_prices):
                p = bid_prices[i]
                out[f"bid_px_{i}"] = p
                out[f"bid_sz_{i}"] = self.bids[p]
            else:
                out[f"bid_px_{i}"] = np.nan
                out[f"bid_sz_{i}"] = np.nan
            if i < len(ask_prices):
                p = ask_prices[i]
                out[f"ask_px_{i}"] = p
                out[f"ask_sz_{i}"] = self.asks[p]
            else:
                out[f"ask_px_{i}"] = np.nan
                out[f"ask_sz_{i}"] = np.nan
        m = self.mid()
        s = self.spread()
        out["mid"] = m if m is not None else np.nan
        out["spread"] = s if s is not None else np.nan
        bb, ba = self.best_bid(), self.best_ask()
        out["best_bid"] = bb.price if bb else np.nan
        out["best_ask"] = ba.price if ba else np.nan
        out["best_bid_sz"] = bb.qty if bb else np.nan
        out["best_ask_sz"] = ba.qty if ba else np.nan
        return out
