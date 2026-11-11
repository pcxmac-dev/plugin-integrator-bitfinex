"""What the plugin attaches to (plugin API 2.2, liminal_libs.sources.apis): Bitfinex's public REST API v2, for its
candles. Every address below was read on Bitfinex's own pages on 2026-11-11 (its documentation's index llms.txt; each
reference page read as Markdown, `.md` appended, with its OpenAPI definition and its rate limit; the requirements and
limitations; the API terms, fees and status pages by their titles). Nothing is asked to show it."""
from __future__ import annotations

from liminal_libs.sources.apis import Api, Area, Call, Link

VERIFIED = "2026-11-11"
NAME = "Bitfinex public REST API v2"
DOCS = "https://docs.bitfinex.com"
REF = f"{DOCS}/reference"

STATUS = "Platform status"
TICKERS = "Tickers"
TRADES = "Trades"
BOOKS = "Books"
STATS = "Stats"
CANDLES = "Candles"
CONFIGS = "Configs"
DERIVS = "Derivatives status"
LIQUIDATIONS = "Liquidations"
LEADERBOARDS = "Leaderboards"
FUNDING = "Funding statistics"
CALCULATIONS = "Calculations"
VASPS = "Virtual asset service providers"
AUTHENTICATED = "Authenticated endpoints (api.bitfinex.com, keyed)"
WS_PUBLIC = "WebSocket public channels"
WS_AUTH = "WebSocket authenticated channels and inputs"

PUBLIC_REST = Api(
    name=NAME,
    maker="Bitfinex",
    about=("Bitfinex's public REST API: the exchange's market data without a key (platform status, tickers and their "
           "history, trades, order books, stats, candles, configs, derivatives status, liquidations, leaderboards, "
           "funding statistics, and two calculations), as JSON arrays from api-pub.bitfinex.com. Its keyed "
           "counterpart, for accounts, orders and funding, is on api.bitfinex.com."),
    kind="rest",
    base="https://api-pub.bitfinex.com/v2",
    version="v2 (its reference's OpenAPI definitions; changelog to v2024-10-16)",
    auth="none for the public endpoints; the authenticated ones sign each request with an API key and a nonce",
    limits=("per IP, between 10 and 90 requests a minute by endpoint (candles 30, trades and stats 15, liquidations 3); "
            "an IP over it is blocked for 60 seconds (\"ERR_RATE_LIMIT\"); a candles request answers 10,000 at most "
            "(kept at 20 a minute here). Its use is bound by Bitfinex's API Terms of Service"),
    costs="",
    links=(
        Link("Public endpoints", f"{DOCS}/docs/rest-public", "docs"),
        Link("Candles (reference)", f"{REF}/rest-public-candles", "reference"),
        Link("Requirements and limitations (rate limits)", f"{DOCS}/docs/requirements-and-limitations", "limits"),
        Link("Changelog", f"{DOCS}/docs/changelog", "changelog"),
        Link("Bitfinex status", "https://bitfinex.statuspage.io", "status"),
        Link("Fees", "https://www.bitfinex.com/fees/", "pricing"),
        Link("API Terms of Service", "https://www.bitfinex.com/legal/general/api-terms/", "terms"),
        Link("Authenticated endpoints", f"{DOCS}/docs/rest-auth", "guide"),
        Link("API keys (account settings)", "https://setting.bitfinex.com/api", "console"),
        Link("Index for AI tools (llms.txt)", f"{DOCS}/llms.txt", "docs"),
    ),
    areas=(
        Area(STATUS, "whether the platform is operative or in maintenance", f"{REF}/rest-public-platform-status"),
        Area(TICKERS, "the tickers of pairs and funding currencies, one ticker, their history", f"{REF}/rest-public-tickers"),
        Area(TRADES, "a symbol's past public trades", f"{REF}/rest-public-trades"),
        Area(BOOKS, "a symbol's order book at a precision, or raw", f"{REF}/rest-public-book"),
        Area(STATS, "statistics on a pair or funding currency (positions, volume, funding)", f"{REF}/rest-public-stats"),
        Area(CANDLES, "OCHL and volume of a pair or funding currency at 1m to 1M, the last or the history",
             f"{REF}/rest-public-candles", covered="trading pairs' candles: minute and day bars (1m, 5m, 1h, 1D), "
                                                    "10,000 a request"),
        Area(CONFIGS, "the site's configuration: pairs, currencies, their names, limits and margins", f"{REF}/rest-public-conf"),
        Area(DERIVS, "derivatives' status (mark price, funding) and its history", f"{REF}/rest-public-derivatives-status"),
        Area(LIQUIDATIONS, "the latest liquidations, or a span of them", f"{REF}/rest-public-liquidations"),
        Area(LEADERBOARDS, "leaderboards by profit and volume", f"{REF}/rest-public-rankings"),
        Area(FUNDING, "a funding currency's recent funding data", f"{REF}/rest-public-funding-stats"),
        Area(CALCULATIONS, "the average execution price of an amount, a foreign exchange rate",
             f"{REF}/rest-public-market-average-price"),
        Area(VASPS, "the travel rule's virtual asset service providers (on api.bitfinex.com)",
             f"{REF}/virtual-asset-service-providers"),
        Area(AUTHENTICATED, "wallets, orders, positions, funding offers and loans, ledgers, movements, deposits, "
                            "withdrawals, alerts and settings (an API key)", f"{DOCS}/docs/rest-auth"),
        Area(WS_PUBLIC, "wss://api-pub.bitfinex.com/ws/2: ticker, trades, books, raw books, candles, status",
             f"{REF}/ws-public-candles"),
        Area(WS_AUTH, "the account's channels (orders, positions, wallets, funding, notifications) and inputs (new and "
                      "updated orders) on the wss://api.bitfinex.com domain (an API key)",
             f"{REF}/ws-auth-notifications"),
    ),
    calls=(
        Call("GET /candles/{candle}/{section}", "a candle key's (trade:1m:tBTCUSD) last candle or its history: limit "
             "(10,000 at most), start, end, sort", CANDLES,
             used="minute and day bars (trade:{1m,5m,1h,1D}:{pair}/hist), 10,000 a request", docs=f"{REF}/rest-public-candles"),
        Call("GET /platform/status", "1 operative, 0 in maintenance (30 a minute)", STATUS,
             docs=f"{REF}/rest-public-platform-status"),
        Call("GET /tickers", "the tickers of the symbols named (30 a minute)", TICKERS, docs=f"{REF}/rest-public-tickers"),
        Call("GET /ticker/{symbol}", "one symbol's ticker (90 a minute)", TICKERS, docs=f"{REF}/rest-public-ticker"),
        Call("GET /tickers/hist", "the tickers' history", TICKERS, docs=f"{REF}/rest-public-tickers-history"),
        Call("GET /trades/{symbol}/hist", "a symbol's past trades (15 a minute)", TRADES, docs=f"{REF}/rest-public-trades"),
        Call("GET /book/{symbol}/{precision}", "a symbol's order book (240 a minute)", BOOKS, docs=f"{REF}/rest-public-book"),
        Call("GET /stats1/{key}:{size}:{sym_platform}:{side_pair}/{section}", "a statistic (15 a minute)", STATS,
             docs=f"{REF}/rest-public-stats"),
        Call("GET /conf/pub:{Action}:{Object}:{Detail}", "a piece of the site's configuration", CONFIGS,
             docs=f"{REF}/rest-public-conf"),
        Call("GET /status/deriv", "derivatives' status (90 a minute)", DERIVS, docs=f"{REF}/rest-public-derivatives-status"),
        Call("GET /status/deriv/{key}/hist", "a derivative's status history (90 a minute)", DERIVS,
             docs=f"{REF}/rest-public-derivatives-status-history"),
        Call("GET /liquidations/hist", "liquidations (3 a minute)", LIQUIDATIONS, docs=f"{REF}/rest-public-liquidations"),
        Call("GET /rankings/{Key}:{Time_Frame}:{Symbol}/{Section}", "a leaderboard", LEADERBOARDS,
             docs=f"{REF}/rest-public-rankings"),
        Call("GET /funding/stats/{symbol}/hist", "a funding currency's statistics", FUNDING,
             docs=f"{REF}/rest-public-funding-stats"),
        Call("POST /calc/trade/avg", "the average execution price of an amount (90 a minute)", CALCULATIONS,
             docs=f"{REF}/rest-public-market-average-price"),
        Call("POST /calc/fx", "a foreign exchange rate (90 a minute)", CALCULATIONS,
             docs=f"{REF}/rest-public-foreign-exchange-rate"),
        Call("GET /ext/vasps", "the virtual asset service providers (on api.bitfinex.com)", VASPS,
             docs=f"{REF}/virtual-asset-service-providers"),
        Call("POST /auth/r/wallets", "the account's wallets (keyed, on api.bitfinex.com)", AUTHENTICATED,
             docs=f"{REF}/rest-auth-wallets"),
        Call("POST /auth/w/order/submit", "places an order (keyed)", AUTHENTICATED, docs=f"{REF}/rest-auth-submit-order",
             writes=True, costs=True),
        Call("POST /auth/w/withdraw", "a withdrawal (keyed)", AUTHENTICATED, docs=f"{REF}/rest-auth-withdraw",
             writes=True, costs=True),
    ),
    verified=VERIFIED,
)

APIS = (PUBLIC_REST,)
