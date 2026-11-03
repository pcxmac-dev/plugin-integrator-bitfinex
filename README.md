# liminal-plugin-bitfinex

Bitfinex for [Liminal](https://github.com/pcxmac-dev/liminal-app): the exchange's crypto minute and day
bars from 2013 (its public candles API, up to 10,000 a request). No key. An exchange of its own:
its history is a market apart from the other exchanges', never closed; `CRYPTO_VENUE_DAYS` in the
app limits how far back it is asked.

A Liminal provider plugin released on its own. The app finds it through the entry point group
`liminal.providers` and lists it on the Plugins view and in `liminal plugins`
as `package: liminal-plugin-bitfinex`, with this package's version.

## Install

Into the app's environment, from the app's folder:

```powershell
.venv\Scripts\python.exe -m pip install "liminal-plugin-bitfinex @ git+https://github.com/pcxmac-dev/liminal-plugin-bitfinex@v1.2.1"
```

or with the app's plugins (`pip install -e ".[plugins]"` in liminal-app). The app loads it on its next
start.

## Compatibility

It is written for plugin API 1.6 (`PLUGIN.api`). An app offering 1.6 or a later 1.x loads it; an
app of another major, or one older than 1.6, leaves it out and says why on the Plugins view.

## Develop

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install "liminal-lib @ git+https://github.com/pcxmac-dev/liminal-lib@main"
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest -q
```

Tests never send requests (a fake session answers) and never read your keys.
