# Changelog

## 0.2.0 (2026-11-03)

Renamed `plugin-integrator-bitfinex` (the package `plugin_integrator_bitfinex`; it was `liminal-plugin-bitfinex`) on 2026-11-03: the naming by system (plugins are `plugin-<app>-<name>`), on liminal-libs 1.4.0 (`liminal_libs`, the library renamed with it).

- A class on plugin API 2.0 (liminal-libs 1.3.0; the user: "all the plugins under liminal should basically
  follow inheritance/oop paradigm"): `BitfinexPlugin(CryptoVenuePlugin)`, a crypto exchange's plugin of
  `liminal_libs.sources.archive` (its `assets` and `kind`; its source built on the contract's public client at
  `base_url`; its `view`, the plan and caps with all the history it holds unless `CRYPTO_VENUE_DAYS` limits
  it, once `venue_view`), what the `Provider` record declared as class attributes and its callback as a
  method (`carries`), `PLUGIN` its instance.
- It declares its publication delay itself (`delays`: each minute once it closes, the row the library held
  for the `bitfinex-public` plan).
- Every behaviour, limit and string as in 1.2.1. Versioned 0.2.0 with every Liminal distribution of the
  release (its `release/0.2.0` branch; CI against the library's).

## 1.2.1 (2026-11-02)

The plugin imports the library as `liminal_libs` and depends on liminal-libs (the app, renamed liminal-charts, is no longer needed to run the tests; the user, 2026-11-02: "lets rename the app to liminal-charts").

## 1.2.0 (2026-11-01)

- Released as its own package, `plugin-integrator-bitfinex`, registered under the entry point group
  `liminal.providers`; its version is the distribution's.
- Its plan and request caps are in it (`TIER`, `PER_RUN`, `PER_DAY`), no longer in the app's
  `config.PUBLIC_FEEDS`; the app's `CRYPTO_VENUE_DAYS` still limits its history (`venue_view`).
- Plugin API 1.6.

## 1.1.0 (2026-10-31)

- Built into the app (then massive-collate): its source class and client in its module (plugin
  API 1.6).

## 1.0.0

- Built into the app (then massive-collate); see the app's history.
