import requests
import json
from datetime import datetime

class Investment:
    def __init__(self, name, ticker, market_cap, type_name, market_sector):
        self.name = name
        self.ticker = ticker
        self.market_cap = market_cap
        self.type_name = type_name
        self.market_sector = market_sector
        self.data_date = datetime.today()

    def json(self):
        return {
            "name": self.name,
            "ticker": self.ticker,
            "market_cap": self.market_cap,
            "type_name": self.type_name,
            "market_sector": self.market_sector,
            "data_date": self.data_date.isoformat()
        }


class InvestmentConfig:
    def __init__(self, name, get_endpoint, post_endpoint, post_payload):
        self.name = name
        self.get_endpoint = get_endpoint
        self.post_endpoint = post_endpoint
        self.post_payload = post_payload

    def get_data(self, save_to_file=False):
        post_url = self.post_endpoint  # america/scan
        get_url = self.get_endpoint
        return_list = []
        with requests.session() as s:
            r = s.get(self.get_endpoint)
            print(get_url, r.status_code, r.reason)
            r = s.post(self.post_endpoint, json=self.post_payload)
            print(post_url, r.status_code, r.reason)
            json_reponse = r.json()
            for row in json_reponse["data"]:
                row_data = row["d"]
                inv = Investment(
                    name=row_data[1], ticker=row_data[0], market_cap=row_data[17], market_sector=self.name,
                    type_name=row_data[4]
                )
                return_list.append(inv)
        if save_to_file:
            with open("output.json", 'w', encoding="utf-8") as wf:
                wf.write(json.dumps(json_reponse, indent=4))
        return return_list


SortOrderName = {"sortBy": "name", "sortOrder": "asc"}
SortOrderMarketCap = {"sortBy": "market_cap_basic", "sortOrder": "desc"}

USAFinance = InvestmentConfig(
    name="Finance",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/finance/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov",
            "fractional", "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded",
            "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm",
            "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Finance"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)
temp = {
    "filter": [
        {"left": "name", "operation": "equal", "right": "health-services"}
    ],
    "columns": [
        "basic_elements", "market_cap_basic", "volume", "dividend_yield_recent", "change", "Perf.1M", "Perf.Y",
        "Perf.YTD"
    ],
    "range": [0, 1000],
    "symbols": {"query": {"types": ["sector"]}},
    "sort": SortOrderMarketCap
}

USAHealthServices = InvestmentConfig(
    name="Health Services",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/health-services/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "filter": [
            {"left": "name", "operation": "equal", "right": "health-services"}
        ],
        "columns": [
            "basic_elements", "market_cap_basic", "volume", "dividend_yield_recent", "change", "Perf.1M", "Perf.Y",
            "Perf.YTD"
        ],
        "range": [0, 1000],
        "symbols": {"query": {"types": ["sector"]}}
    }
)

USACommercialServices = InvestmentConfig(
    name="Commercial Services",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/commercial-services/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Commercial Services"},
            {"left": "exchange", "operation": "in_range",
             "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False, "options": {"lang": "en"}, "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USATechnologyServices = InvestmentConfig(
    name="Technology Services",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/technology-services/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov",
            "fractional", "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded",
            "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm",
            "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Technology Services"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False, "options": {"lang": "en"}, "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USAHealthTechnology = InvestmentConfig(
    name="Health Technology",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/health-technology/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Health Technology"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USAEnergyMinerals = InvestmentConfig(
    name="Energy Minerals",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/energy-minerals/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Energy Minerals"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0,1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USAConsumerServices = InvestmentConfig(
    name="Consumer Services",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/consumer-services/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Consumer Services"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USAProducerManufacturing = InvestmentConfig(
    name="Producer Manufacturing",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/producer-manufacturing/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Producer Manufacturing"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USAUtilities = InvestmentConfig(
    name="Utilities",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/utilities`/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Utilities"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

USATransportation = InvestmentConfig(
    name="Transportation",
    get_endpoint="https://www.tradingview.com/markets/stocks-usa/sectorandindustry-sector/transportation/",
    post_endpoint="https://scanner.tradingview.com/america/scan",
    post_payload={
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional",
            "minmove2", "currency", "change", "change_abs", "Recommend.All", "volume", "Value.Traded", "market_cap_basic",
            "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_basic_ttm", "number_of_employees"
        ],
        "filter": [
            {"left": "name", "operation": "nempty"},
            {"left": "typespecs", "operation": "has_none_of", "right": "preferred"},
            {"left": "sector", "operation": "equal", "right": "Transportation"},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 1000],
        "sort": SortOrderMarketCap,
        "markets": ["america"]
    }
)

