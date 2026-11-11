"""What the plugin attaches to (plugin API 2.2): Bitfinex's public REST API v2 as Bitfinex's pages describe it, the call
it says it makes being the one its source really sends, what its client learned said without a request, and
(LIMINAL_VENDOR_PAGES=1 only) every page it names still answering. Nothing else is sent; no ledger or key is touched."""
from __future__ import annotations

import gc
import os
import re
from datetime import datetime, timezone

import pytest

from liminal_libs.config import load_settings
from liminal_libs.sources.apis import dead_links, problems, urls
from liminal_libs.sources.http import PublicClient

import plugin_integrator_bitfinex as bitfinex
from plugin_integrator_bitfinex import BASE_URL, BitfinexSource
from plugin_integrator_bitfinex.apis import NAME, PUBLIC_REST
from plugin_integrator_bitfinex.facts import NOTES

from .conftest import FakeResponse, FakeSession

CANDLES = re.compile(r"^/candles/trade:(1m|5m|1h|1D):t[A-Z0-9:]+/(hist|last)$")


@pytest.fixture(autouse=True)
def fresh_notes():
    NOTES.clear()
    yield
    NOTES.clear()


def test_it_declares_bitfinexs_public_api_soundly_with_every_part_and_what_it_does_with_each():
    assert bitfinex.PLUGIN.apis == (PUBLIC_REST,) and problems(bitfinex.PLUGIN.apis) == [] and PUBLIC_REST.name == NAME
    assert PUBLIC_REST.base == BASE_URL and PUBLIC_REST.docs.endswith("/docs/rest-public")  # the card's address is the client's
    assert len(PUBLIC_REST.areas) == 16 and [a.name for a in PUBLIC_REST.covered] == ["Candles"]
    assert len(PUBLIC_REST.calls) == 20 and {c.area for c in PUBLIC_REST.calls} <= {a.name for a in PUBLIC_REST.areas}
    assert not any(c.writes or c.costs for c in PUBLIC_REST.used)  # what it makes only reads
    assert {c.name for c in PUBLIC_REST.calls if c.costs} == {"POST /auth/w/order/submit", "POST /auth/w/withdraw"}
    assert "candles 30" in PUBLIC_REST.limits and "blocked for 60 seconds" in PUBLIC_REST.limits
    assert PUBLIC_REST.verified == "2026-11-11" and all(u.startswith("https://") for u in urls(bitfinex.PLUGIN.apis))


def test_the_call_it_says_it_makes_is_the_one_its_source_sends():
    t0 = int(datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    session = FakeSession([FakeResponse(200, [[t0, 10.0, 10.5, 11.0, 9.0, 3.0]])])
    src = BitfinexSource(PublicClient(BASE_URL, session=session, sleep=lambda s: None))
    list(src.bar_pages("BTCUSD", datetime.fromtimestamp(t0 / 1000, timezone.utc),
                       datetime.fromtimestamp(t0 / 1000 + 120, timezone.utc), "minute"))
    paths = {url.removeprefix(BASE_URL) for url, _, _ in session.calls}
    assert paths and all(CANDLES.match(p) for p in paths)
    assert {c.name for c in PUBLIC_REST.used} == {"GET /candles/{candle}/{section}"}


def test_api_facts_say_what_its_client_learned_and_ask_nothing():
    assert bitfinex.PLUGIN.api_facts() == {}  # nothing built here yet: nothing known, nothing asked
    built = bitfinex.PLUGIN.build(load_settings(env={}, env_file=None), 5)  # its build notes its client (no request)
    assert bitfinex.PLUGIN.api_facts()[NAME]["Requests"] == "0 so far (of 5 allowed)" and built.client.requests_made == 0
    del built
    gc.collect()
    assert bitfinex.PLUGIN.api_facts()[NAME]["Run began"].endswith("(ended)")
    # a run's client as Bitfinex answers it (fakes, no ledger): the requests and the server's clock
    session = FakeSession([FakeResponse(200, [], {"Date": "Wed, 11 Nov 2026 12:00:00 GMT"})])
    src = BitfinexSource(PublicClient(BASE_URL, session=session, sleep=lambda s: None))
    NOTES.note(NAME, src.client)
    list(src.bar_pages("BTCUSD", datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, 0, 2, tzinfo=timezone.utc),
                       "minute"))
    said = bitfinex.PLUGIN.api_facts()[NAME]
    assert said["Requests"] == "1 so far" and said["Last answer (server's clock)"] == "Wed, 11 Nov 2026 12:00:00 GMT"


@pytest.mark.skipif(os.environ.get("LIMINAL_VENDOR_PAGES") != "1", reason="asks Bitfinex's pages: set LIMINAL_VENDOR_PAGES=1")
def test_every_page_it_names_answers():
    assert dead_links(bitfinex.PLUGIN.apis) == []
