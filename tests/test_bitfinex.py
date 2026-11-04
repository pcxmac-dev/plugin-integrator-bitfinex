"""The Bitfinex plugin, run against the app installed beside it: its symbols and candle requests, and
the app loading it from this package with its own version and the facts it had as a built-in."""
from __future__ import annotations

from datetime import datetime, timezone
from importlib.metadata import version

import pytest

from liminal_lib import composite, freshness
from liminal_lib.config import load_settings
from liminal_lib.freshness import Delay
from liminal_lib.sources import is_archive, markets, provider, rate_window, registry, supports
from liminal_lib.sources.archive import CryptoVenuePlugin
from liminal_lib.sources.http import PublicClient
from liminal_lib.symbols import resolve

import liminal_plugin_bitfinex
from liminal_plugin_bitfinex import BASE_URL, PER_DAY, PER_RUN, TIER, BitfinexPlugin, BitfinexSource, bitfinex_symbol

from .conftest import FakeResponse, FakeSession


def _client(responses):
    session = FakeSession(responses)
    return PublicClient("https://x.test/api", session=session, sleep=lambda s: None), session


def test_bitfinex_symbols_longer_than_three_letters_take_a_colon():
    assert bitfinex_symbol("BTC", "USD") == "tBTCUSD"
    assert bitfinex_symbol("DOGE", "USD") == "tDOGE:USD" and bitfinex_symbol("LINK", "USD") == "tLINK:USD"
    assert bitfinex_symbol("BCH", "USD") == "tBCHN:USD"


def test_it_asks_for_candles_by_frame_and_pages_by_time():
    t0 = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
    lo, hi = datetime.fromtimestamp(t0, timezone.utc), datetime.fromtimestamp(t0 + 3600, timezone.utc)
    client, session = _client([FakeResponse(200, [])])
    assert list(BitfinexSource(client).bar_pages("X:BTCUSD", lo, hi, "minute", 5)) == [[]]
    url, params, headers = session.calls[0]
    assert "/candles/trade:5m:tBTCUSD/hist" in url and params["sort"] == 1 and "liminal" in headers["User-Agent"]
    # a full page is followed by the next, from the last candle on; the window's bounds are kept
    ms = t0 * 1000
    rows = [[ms + i * 60_000, 1.0, 1.5, 2.0, 0.5, 10.0] for i in range(3)]
    client, session = _client([FakeResponse(200, rows), FakeResponse(200, [[ms + 3 * 60_000, 1, 1, 1, 1, 1]])])
    src = BitfinexSource(client)
    src.PAGE = 3
    pages = list(src.bar_pages("X:BTCUSD", lo, hi, "minute", 1))
    assert [b["t"] for b in pages[0]] == [ms, ms + 60_000, ms + 120_000] and pages[0][0] == {
        "t": ms, "o": 1.0, "c": 1.5, "h": 2.0, "l": 0.5, "v": 10.0, "vw": None, "n": None}
    assert session.calls[1][1]["start"] == ms + 120_001 and len(pages) == 2
    with pytest.raises(ValueError):
        list(BitfinexSource(client).bar_pages("X:BTCUSD", lo, hi, "minute", 3))  # not a Bitfinex frame
    assert BitfinexSource(client).native_frames("crypto") == (("minute", 5), ("hour", 1))
    inst = BitfinexSource(client).instrument("X:ETHUSD")
    assert inst.ticker == "ETHUSD" and inst.details["venue"] == "Bitfinex"


def test_the_app_loads_it_from_this_package_with_its_own_version():
    registry.reload()
    p = provider("bitfinex")
    assert p is not None, dict(registry.errors())
    assert p.origin in {"package: liminal-plugin-bitfinex (liminal_plugin_bitfinex:PLUGIN)", "plugins/liminal-plugin-bitfinex (liminal_plugin_bitfinex:PLUGIN)"}  # its package, or its checkout in the workspace\'s plugin directory
    assert p.version == version("liminal-plugin-bitfinex") and liminal_plugin_bitfinex.PLUGIN.version == ""
    assert registry.api_refusal(p.api) is None
    assert not [why for where, why in registry.errors() if "bitfinex" in where or "bitfinex" in why]
    row = {r["name"]: r for r in registry.menu()}["bitfinex"]
    assert (row["version"], row["api"]) == (version("liminal-plugin-bitfinex"), "2.0")


def test_it_keeps_the_facts_it_had_built_in():
    registry.reload()
    s = load_settings(env={}, env_file=None)
    view = s.for_source("bitfinex")
    assert (view.tier, view.max_requests_per_run, view.max_requests_per_day) == (TIER, PER_RUN, PER_DAY)
    assert rate_window("bitfinex", s) == (20, 60.0)
    limited = load_settings(env={"CRYPTO_VENUE_DAYS": "30"}, env_file=None).for_source("bitfinex")
    assert limited.tier.history_days == 30 and limited.tier.history_start == TIER.history_start
    assert not is_archive("bitfinex") and markets("bitfinex", s) == {"crypto": "bitfinex"}
    assert supports("bitfinex", resolve("BTCUSD")) and not supports("bitfinex", resolve("AAPL"))
    assert composite.feed_kind("bitfinex", "crypto") == "exchange"


def test_it_is_a_class_on_the_contract_and_the_app_loads_it_as_one():
    p = liminal_plugin_bitfinex.PLUGIN
    assert isinstance(p, BitfinexPlugin) and isinstance(p, CryptoVenuePlugin) and p.api == "2.0" and not p.is_record
    assert p.assets == frozenset({"crypto"}) and p.kind == "exchange"  # a crypto venue's, from its base
    assert p.gives("build") and p.gives("view") and p.gives("carries")
    assert not p.has_scan and not p.has_settings and not p.gives("rate") and not p.gives("markets")
    assert p.delays == {"bitfinex-public": {"crypto": Delay("delay")}} and p.hours == {}
    loaded = registry.reload()["bitfinex"]
    assert type(loaded) is BitfinexPlugin and (loaded.version, loaded.api) == (version("liminal-plugin-bitfinex"), "2.0")
    assert not [why for where, why in registry.errors() if "bitfinex" in where or "bitfinex" in why]
    src = loaded.build(load_settings(env={}, env_file=None), 5)  # its base's build: its source on the public client
    assert isinstance(src, BitfinexSource) and isinstance(src.client, PublicClient) and src.client.base_url == BASE_URL
    assert freshness.plan_delay(TIER, "crypto").kind == "delay"  # its own rule (BitfinexPlugin.delays; the library's too)
    moved = p.with_(order=1)  # a changed copy (the registry's version and origin come this way)
    assert type(moved) is BitfinexPlugin and moved.order == 1 and p.order == 40
