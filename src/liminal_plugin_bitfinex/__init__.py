"""Bitfinex (bitfinex.com) for Liminal: crypto minute and day bars from 2013, no key.

A Liminal plugin released on its own (liminal.sources.registry: Provider), registered under the
entry point group `liminal.providers` as `bitfinex`. It relies on plugin API 1.6 and nothing of the
app outside it (docs/ARCHITECTURE.md in liminal: "Providers are plugins"); its version is this
distribution's (pyproject.toml), so PLUGIN.version is left empty.
"""
from __future__ import annotations

from datetime import date
from typing import Iterator

from liminal.config import Tier
from liminal.models import Instrument
from liminal.sources.archive import CRYPTO_PAIRS, EXCHANGE_FRAMES, Archive as _Archive, bounds as _bounds, crypto_pair as _pair
from liminal.sources.archive import venue_view
from liminal.sources.registry import Provider, public_client

BASE_URL = "https://api-pub.bitfinex.com/v2"
# Its plan and caps (once the app's config.PUBLIC_FEEDS["bitfinex"]): all the history it holds, unless
# CRYPTO_VENUE_DAYS limits it (venue_view). Bitfinex allows about 30 candle requests a minute.
TIER = Tier("bitfinex-public", requests_per_minute=20, history_years=None, history_start=date(2013, 4, 1))
PER_RUN, PER_DAY = 300, 2000

BITFINEX_CODES = {"BCH": "BCHN"}  # Bitfinex's own names for a few coins


def bitfinex_symbol(base: str, quote: str) -> str:
    """Bitfinex's trading pair: tBTCUSD, but tDOGE:USD where a code is longer than three letters."""
    base, quote = BITFINEX_CODES.get(base, base), BITFINEX_CODES.get(quote, quote)
    return f"t{base}:{quote}" if len(base) > 3 or len(quote) > 3 else f"t{base}{quote}"


class BitfinexSource(_Archive):
    """Bitfinex public candles: up to 10,000 per request ([ms, open, close, high, low, volume]).
    Prices carry 5 significant digits (whole dollars for Bitcoin)."""

    name = "bitfinex"
    assets = ("crypto",)
    archival = False
    PAGE = 10000
    FRAMES = {("minute", 1): ("1m", 60_000), ("minute", 5): ("5m", 300_000), ("hour", 1): ("1h", 3_600_000),
              ("day", 1): ("1D", 86_400_000)}

    def resolutions(self, asset: str) -> tuple[str, ...]:
        return ("minute",) if asset == "crypto" else ()

    def native_frames(self, asset: str) -> tuple[tuple[str, int], ...]:
        return EXCHANGE_FRAMES if asset == "crypto" else ()

    def covers(self, ticker: str) -> bool:
        return ticker.upper().removeprefix("X:") in CRYPTO_PAIRS

    def bar_pages(self, ticker, start, end, timespan, multiplier=1, descending=False, asset="crypto",
                  limit: int | None = None) -> Iterator[list[dict]]:
        if (timespan, multiplier) not in self.FRAMES:
            raise ValueError(f"Bitfinex frames: {tuple(self.FRAMES)}")
        base, quote = _pair(ticker)
        frame, step = self.FRAMES[(timespan, multiplier)]
        a, b = _bounds(start, end)
        hi = b - 1
        lo = a
        while lo <= hi:
            params = {"start": lo, "end": hi, "limit": limit or self.PAGE, "sort": -1 if descending else 1}
            rows = self.client.get(f"/candles/trade:{frame}:{bitfinex_symbol(base, quote)}/hist", params) or []
            bars = [{"t": int(r[0]), "o": float(r[1]), "c": float(r[2]), "h": float(r[3]), "l": float(r[4]),
                     "v": float(r[5]), "vw": None, "n": None} for r in rows if a <= int(r[0]) < b]
            yield bars
            if limit or len(rows) < (limit or self.PAGE):
                return
            stamps = [int(r[0]) for r in rows]
            if descending:
                hi = min(stamps) - 1
            else:
                lo = max(stamps) + 1

    def instrument(self, ticker: str, resolve_exchange: bool = True) -> Instrument:
        base, quote = _pair(ticker)
        return Instrument(ticker=base + quote, name=f"{base}/{quote} on Bitfinex", details={"venue": "Bitfinex"})


PLUGIN = Provider(
    api="1.6",  # the contract it needs (its client in it: sources.archive); its version: the distribution's
    name="bitfinex", title="Bitfinex",
    build=lambda settings, budget: BitfinexSource(public_client("bitfinex", BASE_URL, settings, budget)),
    assets=frozenset({"crypto"}), order=40, about="crypto minute and day bars from 2013 (no key)",
    tier=TIER, per_run=PER_RUN, per_day=PER_DAY, limits="about 30 candle requests per minute", kind="exchange",
    per_request={"day": BitfinexSource.PAGE, "minute": BitfinexSource.PAGE},
    view=venue_view("bitfinex"),
    carries=lambda spec: spec.ticker.upper() in CRYPTO_PAIRS,
)
