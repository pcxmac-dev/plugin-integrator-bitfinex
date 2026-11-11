# plugin-integrator-bitfinex

Bitfinex for [Liminal](https://github.com/pcxmac-dev/liminal-charts): the exchange's crypto minute and day
bars from 2013 (its public candles API, up to 10,000 a request). No key. An exchange of its own:
its history is a market apart from the other exchanges', never closed; `CRYPTO_VENUE_DAYS` in the
app limits how far back it is asked.

A Liminal provider plugin released on its own. The app finds it through the entry point group
`liminal.providers` and lists it on the Plugins view and in `liminal-charts plugins`
as `package: plugin-integrator-bitfinex`, with this package's version.

## Its API

It attaches to Bitfinex's [public REST API v2](https://docs.bitfinex.com/docs/rest-public)
(`https://api-pub.bitfinex.com/v2`, no key); its page in every app shows it (`PLUGIN.apis`), with every part of it, the
call it makes among the rest, and what its client learned (`PLUGIN.api_facts()`):

- the [candles](https://docs.bitfinex.com/reference/rest-public-candles) (`GET /candles/trade:{frame}:{pair}/hist`,
  10,000 a request) for the minute and day bars;
- its [limits](https://docs.bitfinex.com/docs/requirements-and-limitations): 10 to 90 requests a minute per IP by
  endpoint (candles 30), an IP over it blocked for 60 seconds; it keeps 20 a minute;
- Bitfinex's [API Terms of Service](https://www.bitfinex.com/legal/general/api-terms/) and its
  [status](https://bitfinex.statuspage.io).

## Install

Into the app's environment, from the app's folder:

```powershell
.venv\Scripts\python.exe -m pip install "plugin-integrator-bitfinex @ git+https://github.com/pcxmac-dev/plugin-integrator-bitfinex@v0.3.0"
```

or with the app's plugins (`pip install -e ".[plugins]"` in liminal-charts). The app loads it on its next
start.

## Compatibility

It is written for plugin API 2.2 (`PLUGIN.api`: the class contract, `BitfinexPlugin` a
`CryptoVenuePlugin` of liminal-libs 1.49.0 or later, declaring what it attaches to, `apis`). An app offering 2.2 or a
later 2.x loads it; an app of another major, or one older than 2.2, leaves it out and says why on the Plugins view.

## Develop

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install "liminal-libs @ git+https://github.com/pcxmac-dev/liminal-libs@main"
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
```

Tests never send requests (a fake session answers) and never read your keys.
