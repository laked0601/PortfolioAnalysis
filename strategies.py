from sql_interaction import sql_cnxn
from statistics import mean, stdev
from math import sqrt
from datetime import timedelta, datetime
import csv


class priceres:
    def __init__(self, timed):
        self.timed = timed
        self.prices = []
        self.dates = []
        self.min_dates = 0.8 * self.timed.days
        self.mean = None
        self.volatility = None
        self.change = None

    def add_price(self, price, date):
        for dt in self.dates.copy():
            if date - dt >= self.timed:
                self.prices.pop(0)
                self.dates.pop(0)
            else:
                break
        self.prices.append(price)
        self.dates.append(date)
        dates_count = len(self.dates)
        if dates_count > self.min_dates:
            self.mean = mean(self.prices)
            self.volatility = stdev(self.prices) * sqrt(dates_count)
            self.change = self.prices[-1] / self.prices[0] - 1
        else:
            self.mean = None
            self.volatility = None
            self.change = None


def buy_low_volatility():
    # Purchase a selection of investments with a low 45d volatility
    # Sell at a stop loss of 50% or 2.5x price
    with sql_cnxn() as cnxn:
        crsr = cnxn.cursor()
        crsr.execute("select distinct CMCAsset from CoinCodexData")
        assets = [x[0] for x in crsr.fetchall()]
        start = False
        for asset_id in assets:
            if asset_id == 22289:
                start = True
            if not start:
                continue
            print(asset_id)
            crsr.execute("delete from CoinCodexData_Stats "
                         "where CCDPK in (select PK from CoinCodexData where CMCAsset = ?)", (asset_id,))
            crsr.execute("select PK, time_end, price_close_usd from CoinCodexData "
                         "where CMCAsset = ? order by time_end", (asset_id,))
            _7d = priceres(timedelta(days=7))
            _30d = priceres(timedelta(days=30))
            _60d = priceres(timedelta(days=60))
            _90d = priceres(timedelta(days=90))
            rows = crsr.fetchall()
            for cdd_pk, time_end, price_close_usd in rows:
                time_end = datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S")
                _7d.add_price(price_close_usd, time_end)
                _30d.add_price(price_close_usd, time_end)
                _60d.add_price(price_close_usd, time_end)
                _90d.add_price(price_close_usd, time_end)
                crsr.execute("insert into CoinCodexData_Stats (CCDPK, `7d_price_change`, `30d_price_change`, "
                             "`60d_price_change`, `90d_price_change`, `7d_volatility`, `30d_volatility`, "
                             "`60d_volatility`, `90d_volatility`, `7d_price_average`, `30d_price_average`, "
                             "`60d_price_average`, `90d_price_average`) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (cdd_pk, _7d.change, _30d.change, _60d.change, _90d.change, _7d.volatility,
                              _30d.volatility, _60d.volatility, _90d.volatility, _7d.mean, _30d.mean, _60d.mean,
                              _90d.mean))
            cnxn.commit()
            # break

# buy_low_volatility()

def memestock_strat():
    with sql_cnxn() as cnxn:
        crsr = cnxn.cursor()
        crsr.execute("select na.CMCAsset from NewlyAddedCryptoCurrencies na "
                     "where na.CMCAsset not in ("
                     "select ast.id "
                     "from CMCAssets ast "
                     "left join CMCAssetsToTags ast_tg on ast_tg.CMCAsset = ast.id "
                     "left join CMCTags tg on ast_tg.CMCTag = tg.PK "
                     "where tagname = 'stablecoin')",)
        rows = crsr.fetchall()
        returns = []
        for i, (asset_id,) in enumerate(rows):
            print(asset_id)
            return_percent = 0
            crsr.execute("select time_end, price_close_usd from CoinCodexData "
                         "where CMCAsset = ? order by time_end asc", (asset_id,))
            res = crsr.fetchone()
            buy_date = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
            buy_price = res[1]
            while True:
                res = crsr.fetchone()
                if res is None:
                    break
                new_date = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S")
                new_price = res[1]
                if new_price == 0:
                    continue
                if new_price < buy_price * 0.5:
                    return_percent += new_price / buy_price - 1
                    break
                if new_price > buy_price * 5:
                    return_percent += new_price / buy_price - 1
                    break
                if new_date - buy_date > timedelta(days=15) and new_price > buy_price * 1.2:
                    return_percent += new_price / buy_price - 1
                    break
                if new_date - buy_date > timedelta(days=30) and new_price > buy_price * 1.5:
                    return_percent += new_price / buy_price - 1
                    break
                if new_date - buy_date > timedelta(days=45) and new_price > buy_price * 1.75:
                    return_percent += new_price / buy_price - 1
                    break
                if new_date - buy_date > timedelta(days=60) and new_price > buy_price * 2:
                    return_percent += new_price / buy_price - 1
                    break
                if new_date - buy_date > timedelta(days=90):
                    return_percent += new_price / buy_price - 1
                    break
            returns.append((asset_id, return_percent))
            if i > 100:
                break
    with open("memestock_opening_strat3.csv", 'w', encoding="utf-8", newline="") as wf:
        writer = csv.writer(wf, delimiter=',', quotechar='"')
        writer.writerows(returns)
        x = 1000
        for y in returns:
            x *= y[1] + 1
        print(x)
        # print(sum([x[1] for x in returns]))

memestock_strat()

