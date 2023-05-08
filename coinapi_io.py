import requests
import json
from sql_interaction import sql_cnxn
from datetime import date, datetime

key = ""


def get_symbols(exchange="BINANCE"):
    prms = {
        "filter_exchange_id": exchange
    }
    r = requests.get("https://rest.coinapi.io/v1/symbols", headers={"X-CoinAPI-Key": key})
    print(r.status_code)
    if len(r.content) != 0:
        with open("coinapi_io_symbols.json", 'w', encoding="utf-8") as wf:
            wf.write(json.dumps(r.json(), indent=4))


def get_exchanges():
    hdrs = {"X-CoinAPI-Key": key}
    r = requests.get("https://rest.coinapi.io/v1/exchanges/icons/32", headers=hdrs)
    print(r.status_code)
    if len(r.content) != 0:
        with open("coinapi_io_exchanges_32.json", 'w', encoding="utf-8") as wf:
            wf.write(json.dumps(r.json(), indent=4))


def get_assets():
    headers = {"X-CoinAPI-Key": key}
    r = requests.get("https://rest.coinapi.io/v1/assets", headers=headers)
    print(r.status_code)
    if len(r.content) != 0:
        with open("coinapi_io_assets.json", 'w', encoding="utf-8") as wf:
            wf.write(json.dumps(r.json(), indent=4))


def get_quotes():
    hdrs = {"X-CoinAPI-Key": key}
    r = requests.get("https://rest.coinapi.io/v1/quotes/latest", headers=hdrs)
    print(r.status_code)
    if len(r.content) != 0:
        with open("coinapi_io_quotes.json", 'w', encoding="utf-8") as wf:
            wf.write(json.dumps(r.json(), indent=4))


def convert_date_str(date_str):
    if date_str is None:
        return
    if date_str.find('T') != -1 and date_str.find('Z') != -1:
        return datetime.strptime(date_str[0:-2], "%Y-%m-%dT%H:%M:%S.%f")
    else:
        return date(int(date_str[0:4]), int(date_str[5:7]), int(date_str[8:10]))


class CoinapiTable:
    def __init__(self, date_headers=tuple(), datetime_headers=tuple(), currency_headers=tuple(), other_headers=tuple(),
                 table_name=None, primary_key=None):
        self.date_headers = date_headers
        self.datetime_headers = datetime_headers
        self.currency_headers = currency_headers
        self.other_headers = other_headers
        self.primary_key = primary_key
        self.table_name = table_name
        self.all_headers = self.date_headers + self.datetime_headers + self.currency_headers + self.other_headers

    def json_to_sql(self, json_data, cursor):
        for row in json_data:
            date_and_datetimes = [None for _ in self.date_headers + self.datetime_headers]
            for i, k in enumerate(self.date_headers + self.datetime_headers):
                if k in row:
                    date_and_datetimes[i] = convert_date_str(row[k])

            currencies = [None for _ in self.currency_headers]
            for i, k in enumerate(self.currency_headers):
                if k in row and row[k] is not None:
                    currencies[i] = int(row[k] + 100)

            others = [None for _ in self.other_headers]
            for i, k in enumerate(self.other_headers):
                if k in row:
                    others[i] = row[k]
            try:
                cursor.execute("insert into %s (%s) values (%s)" %
                               (self.table_name, ','.join(self.all_headers), ','.join(['?' for _ in self.all_headers])),
                               date_and_datetimes + currencies + others)
            except OverflowError as e:
                pass
                # input('>')
                # print(others)


class CoinapiAssets(CoinapiTable):
    def __init__(self):
        CoinapiTable.__init__(
            self,
            date_headers=("data_start", "data_end"),
            datetime_headers=("data_quote_start", "data_quote_end", "data_orderbook_start", "data_orderbook_end",
                              "data_trade_start", "data_trade_end"),
            other_headers=("asset_id", "name", "type_is_crypto", "price_usd", "data_symbols_count", "volume_1hrs_usd",
                           "volume_1day_usd", "volume_1mth_usd"),
            table_name="CoinapiAssets",
            primary_key="asset_id"
        )


class CoinapiExchanges(CoinapiTable):
    def __init__(self):
        CoinapiTable.__init__(
            self,
            other_headers=("exchange_id", "url"),
            table_name="CoinapiExchanges",
            primary_key="exchange_id"
        )


class CoinapiSymbols(CoinapiTable):
    def __init__(self):
        CoinapiTable.__init__(
            self,
            date_headers=("data_start", "data_end"),
            datetime_headers=("data_quote_start", "data_quote_end", "option_expiration_time", "data_trade_start",
                              "data_trade_end", "data_orderbook_start", "data_orderbook_end", "future_delivery_time",
                              "contract_delivery_time"),
            other_headers=("symbol_id", "exchange_id", "symbol_type", "asset_id_base", "asset_id_quote",
                           "asset_id_base_exchange", "asset_id_quote_exchange", "symbol_id_exchange",
                           "index_display_description", "option_exercise_style", "data_start", "data_end",
                           "option_type_is_call", "price_precision", "option_contract_unit", "size_precision",
                           "option_strike_price", "volume_1day", "volume_1day_usd", "volume_1mth", "volume_1mth_usd",
                           "price", "contract_unit", "index_id", "future_contract_unit",
                           "contract_display_description", "index_display_name", "volume_1hrs",
                           "future_contract_unit_asset", "contract_display_name", "contract_id",
                           "asset_id_unit", "volume_1hrs_usd"),
            table_name="CoinapiSymbols",
            primary_key="symbol_id"
        )


class CMCListings(CoinapiTable):
    def __init__(self):
        CoinapiTable.__init__(self,
                              datetime_headers=("date_added", "last_updated"),
                              other_headers=(
                                  "id", "name", "symbol", "slug", "num_market_pairs", "max_supply",
                                  "circulating_supply", "total_supply", "infinite_supply", "cmc_rank",
                                  "self_reported_circulating_supply", "self_reported_market_cap", "tvl_ratio",
                              ),
                              table_name="CMCQuotes",
                              primary_key="id")
        self.quote_other = ("price", "volume_24h", "volume_change_24h", "percent_change_1h",
                            "percent_change_24h", "percent_change_7d", "percent_change_30d", "percent_change_60d",
                            "percent_change_90d", "market_cap", "market_cap_dominance",
                            "fully_diluted_market_cap", "tvl")

    def get_data(self):
        headers = {
            "X-CMC_PRO_API_KEY": "",
            "Accept": "application/json"
        }
        params = {
            "start": 1,
            "limit": 5000
        }
        r = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",
                         headers=headers, params=params)
        print(r.status_code)
        return r.json()

    @staticmethod
    def get_datetime_values(json_data, keys):
        return_list = [None for _ in keys]
        for i, k in enumerate(keys):
            if k in json_data:
                if json_data[k] is not None:
                    return_list[i] = datetime.strptime(json_data[k], "%Y-%m-%dT%H:%M:%S.000Z")
        return return_list

    def add_quote_data(self, json_data, cursor, asset_id):
        quote_datetimes = CMCListings.get_datetime_values(json_data, ("last_updated",))
        cursor.execute("select 1 from CMCQuotes where CMCAsset = ? and last_updated = ?",
                       (asset_id, quote_datetimes[0]))
        res = cursor.fetchone()
        if res is None:
            row_template = [None for _ in self.quote_other]
            for i, k in enumerate(self.quote_other):
                if k in json_data:
                    row_template[i] = json_data[k]
            insert_headers = ("CMCAsset", "last_updated") + self.quote_other
            cursor.execute("insert into CMCQuotes (%s) values (%s)" %
                           (','.join(insert_headers), ','.join(['?' for _ in insert_headers])),
                           [asset_id] + quote_datetimes + row_template)

    def json_to_sql(self, json_data, cursor):
        for row in json_data["data"]:
            cursor.execute("select 1 from CMCAssets where id = ?", (row["id"],))
            if cursor.fetchone() is not None:
                continue
            asset_id = row[self.primary_key]
            datetimes = CMCListings.get_datetime_values(row, self.datetime_headers)
            others = [None for _ in self.other_headers]
            for i, k in enumerate(self.other_headers):
                if k in row:
                    others[i] = row[k]
            if "quote" in row and "USD" in row["quote"]:
                self.add_quote_data(row["quote"]["USD"], cursor, asset_id)
            if "tags" in row:
                cursor.execute("delete from CMCAssetsToTags where CMCAsset = ?", (asset_id,))
                for t in row["tags"]:
                    cursor.execute("select PK from CMCTags where tagname = ?", (t,))
                    res = cursor.fetchone()
                    if res is None:
                        cursor.execute("insert into CMCTags (tagname) values (?)", (t,))
                        cursor.execute("insert into CMCAssetsToTags (CMCAsset, CMCTag) values (?, ?)",
                                       (asset_id, cursor.lastrowid))
                    else:
                        cursor.execute("insert into CMCAssetsToTags (CMCAsset, CMCTag) values (?, ?)",
                                       (asset_id, res[0]))
            try:
                cursor.execute("insert into CMCAssets (%s) values (%s)" %
                               (','.join(self.all_headers), ','.join(['?' for _ in self.all_headers])),
                               datetimes + others)
            except OverflowError:
                for i, k in enumerate(self.other_headers):
                    if k in row and (isinstance(row[k], int) or isinstance(row[k], float)):
                        others[i] = None
                cursor.execute("insert into CMCAssets (%s) values (%s)" %
                               (','.join(self.all_headers), ','.join(['?' for _ in self.all_headers])),
                               datetimes + others)





# with sql_cnxn() as cnxn:
#     crsr = cnxn.cursor()
#     with open("listings_latest.json", 'r', encoding="utf-8") as rf:
#         content = json.loads(rf.read())
#         c = CMCListings()
#         c.json_to_sql(content, crsr)
#     cnxn.commit()


# with sql_cnxn() as cnxn:
#     crsr = cnxn.cursor()
#     c = CoinapiSymbols()
#     with open("coinapi_io_symbols.json", 'r', encoding="utf-8") as rf:
#         content = json.loads(rf.read())
#         c.json_to_sql(content, crsr)
#     cnxn.commit()

# with open("coinapi_io_symbols.json", 'r', encoding="utf-8") as rf:
#     content = json.loads(rf.read())
#     hdrs = set()
#     for row in content:
#         for k in row.keys():
#             hdrs.add(k)
#     for k in hdrs:
#         print(k)

