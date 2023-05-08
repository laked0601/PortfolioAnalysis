import sqlite3
from contextlib import contextmanager
import os
from datetime import datetime, timedelta
import json
import csv
from time import sleep
import requests
# from ticker_info.main import Investment, USAFinance, USACommercialServices, USATechnologyServices, \
#     USAHealthTechnology, USAEnergyMinerals, USAConsumerServices, USAProducerManufacturing, USAUtilities, \
#     USATransportation
import report_generator
import random
import matplotlib.pyplot as plt
from sql_interaction import sql_cnxn


def html_to_pdf(html_file_path, output_pdf_path):
    if output_pdf_path[-5:] == ".html":
        output_pdf_path = output_pdf_path[0:-5] + ".pdf"
    elif output_pdf_path[-4:] == ".htm":
        output_pdf_path = output_pdf_path[0:-4] + ".pdf"
    cmd_str = ("chrome.exe --headless --print-to-pdf=\"%s\" --print-to-pdf-no-header \"%s\"" %
              (output_pdf_path.replace('\\', '/'), html_file_path.replace('\\', '/')))
    with open("generate_pdf.bat", 'w', encoding="utf-8") as wf:
        wf.write(cmd_str)


def get_prices(ticker):
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "apikey": API_KEY,
        "symbol": ticker,
        "outputsize": "full"
    }
    r = requests.get("https://www.alphavantage.co/query", params=params)
    print(r.status_code, r.reason)
    content = r.json()
    if "Note" in content:
        print(json.dumps(content, indent=4))
        print("sleeping 1 minute...")
        sleep(65)
        r = requests.get("https://www.alphavantage.co/query", params=params)
        print(r.status_code, r.reason)
        content = r.json()
        if "Note" in content:
            print("Limit reached. Shutting down.")
            raise Exception
    return content


def add_prices(row_limit=100, time_limit=None):
    with sql_cnxn() as cnxn:
        crsr = cnxn.cursor()
        crsr.execute(
            "select `Investment PK`, Symbol from Overview "
            "where `Investment PK` not in (select distinct `Investment PK` from Prices)"
            "order by MarketCapitalization desc limit %d" % (row_limit, )
        )
        for row in crsr.fetchall():
            inv_pk, ticker = row[0], row[1]
            print(ticker, end=" ")
            insert_data = []
            price_data = get_prices(ticker)
            if "Time Series (Daily)" not in price_data:
                # crsr.execute("delete from Investments where ticker = ?", (ticker,))
                # cnxn.commit()
                # print(json.dumps(price_data, indent=4))
                continue
            for date_str, price_dict in price_data["Time Series (Daily)"].items():
                crsr_params = (
                    inv_pk, datetime.strptime(date_str, "%Y-%m-%d"),
                    price_dict["1. open"], price_dict["2. high"], price_dict["3. low"], price_dict["4. close"],
                    price_dict["5. adjusted close"], price_dict["6. volume"], price_dict["7. dividend amount"],
                    price_dict["8. split coefficient"]
                )
                insert_data.append(crsr_params)
            crsr.executemany(
                "insert into `Prices` (`Investment PK`, `price date`, open, high, low, close, `adjusted close`, "
                "volume, `dividend amount`, `split coefficient`) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                insert_data
            )
            cnxn.commit()
            print(len(insert_data))


def get_company_overview(ticker):
    params = {
        "function": "OVERVIEW",
        "apikey": API_KEY,
        "symbol": ticker,
    }
    r = requests.get("https://www.alphavantage.co/query", params=params)
    print(r.status_code, r.reason)
    content = r.json()
    if "Note" in content:
        print(json.dumps(content, indent=4))
        print("sleeping 1 minute...")
        sleep(65)
        r = requests.get("https://www.alphavantage.co/query", params=params)
        print(r.status_code, r.reason)
        content = r.json()
        if "Note" in content:
            print("Limit reached. Shutting down.")
            raise Exception
    for k in ('LatestQuarter', 'DividendDate', 'ExDividendDate'):
        if k in content:
            if content[k] == "None":
                content[k] = None
            elif content[k] == "0000-00-00":
                content[k] = datetime(1, 1, 1)
            else:
                content[k] = datetime.strptime(content[k], "%Y-%m-%d")
    for k in ('MarketCapitalization', 'EBITDA', 'RevenueTTM', 'GrossProfitTTM', 'SharesOutstanding'):
        if k in content:
            if content[k] in ("None", '-'):
                content[k] = None
            else:
                content[k] = int(content[k])
    for k in (
        'PERatio', 'PEGRatio', 'BookValue', 'DividendPerShare', 'DividendYield', 'EPS', 'RevenuePerShareTTM',
        'ProfitMargin', 'OperatingMarginTTM', 'ReturnOnAssetsTTM', 'ReturnOnEquityTTM', 'DilutedEPSTTM',
        'QuarterlyEarningsGrowthYOY', 'QuarterlyRevenueGrowthYOY', 'AnalystTargetPrice', 'TrailingPE',
        'ForwardPE', 'PriceToSalesRatioTTM', 'PriceToBookRatio', 'EVToRevenue', 'EVToEBITDA', 'Beta',
        '52WeekHigh', '52WeekLow', '50DayMovingAverage', '200DayMovingAverage'
    ):
        if k in content:
            if content[k] in ("None", '-'):
                content[k] = None
            else:
                content[k] = float(content[k])
    return content


def add_overviews(row_limit=100, sql_parameters=''):
    keys = (
        'Symbol', 'AssetType', 'Name', 'Description', 'CIK', 'Exchange', 'Currency', 'Country', 'Sector', 'Industry', 'Address',
        'FiscalYearEnd', 'LatestQuarter', 'MarketCapitalization', 'EBITDA', 'PERatio', 'PEGRatio', 'BookValue',
        'DividendPerShare', 'DividendYield', 'EPS', 'RevenuePerShareTTM', 'ProfitMargin', 'OperatingMarginTTM',
        'ReturnOnAssetsTTM', 'ReturnOnEquityTTM', 'RevenueTTM', 'GrossProfitTTM', 'DilutedEPSTTM',
        'QuarterlyEarningsGrowthYOY', 'QuarterlyRevenueGrowthYOY', 'AnalystTargetPrice', 'TrailingPE', 'ForwardPE',
        'PriceToSalesRatioTTM', 'PriceToBookRatio', 'EVToRevenue', 'EVToEBITDA', 'Beta', '52WeekHigh', '52WeekLow',
        '50DayMovingAverage', '200DayMovingAverage', 'SharesOutstanding', 'DividendDate', 'ExDividendDate',
    )
    column_names = ['`%s`' % (k,) for k in keys]
    column_params = ['?' for _ in keys]
    x = 0
    with sql_cnxn() as cnxn:
        crsr = cnxn.cursor()
        crsr.execute(
            "select PK, ticker from Investments where ticker not in (select Symbol from Overview) "
            #"and market_sector = 'Transportation' "
            # "and market_cap between 2000000000 and 10000000000 "  # Mid-cap
            # "and market_cap between 250000000 and 2000000000 "  # Small-cap
            "%s"
            "order by market_cap desc limit %d" % (sql_parameters, row_limit, )
        )
        for row in crsr.fetchall():
            inv_pk, ticker = row[0], row[1]
            print(ticker, end=" ")
            investment_data = get_company_overview(ticker)
            row_template = [None for _ in keys]
            value_found = False
            for i, k in enumerate(keys):
                if k in investment_data:
                    value_found = True
                    row_template[i] = investment_data[k]
            if not value_found:
                # crsr.execute("delete from Investments where PK = ?", (inv_pk,))
                # cnxn.commit()
                print("Data not found, ignoring.")
                continue
            crsr.execute(
                "insert into Overview (`Investment PK`, %s) values (?, %s)" % (
                    ', '.join(column_names), ', '.join(column_params)
                ),
                [inv_pk] + row_template
            )
            print(len(row_template))
            cnxn.commit()
            x += 1
            if x >= row_limit:
                break


def get_investments_and_prices():
    with sql_cnxn() as cnxn:
        crsr = cnxn.cursor()
        crsr.execute("select * from `Market Capitalization Brackets`")
        res = crsr.fetchall()
    for row in res:
        bracket_size, overview_count, investments_count, lower_figure, upper_figure = row[1], row[2], row[3], row[4], row[5]
        row_limit = min(investments_count - overview_count, 350 - overview_count)
        if row_limit <= 0:
            continue
        print(row, row_limit, end=" ")
        sql_param = "and market_cap between %d and %d " % (lower_figure, upper_figure)
        print(sql_param)
        add_overviews(row_limit=row_limit, sql_parameters=sql_param)
        add_prices(row_limit=10000)


class Portfolio:
    def __init__(
            self, invested_amount=1_000_000, max_investments=10, sectors=None, industries=None,
            lower_market_cap=None, upper_market_cap=None, cap_size="", min_cash=100_000, start_date=datetime(2015, 1, 1),
            selection_method="random"
    ):
        if min_cash > invested_amount:
            raise Exception("Cannot hold more in cash than the invested amount")
        invested_amount *= 100
        min_cash *= 100
        self.total_cost = 0
        self.total_unrealised_gain = 0
        self.total_market_value = 0
        self.annualised_return = 0
        self.cash = invested_amount
        self.assets = []
        self.sectors = sectors
        self.industries = industries
        self.cap_size_str = cap_size
        if self.determine_cap_size(cap_size) is None:
            self.lower_market_cap = lower_market_cap
            self.upper_market_cap = upper_market_cap
        self.max_investments = max_investments
        self.date = start_date
        print("Building portfolio...")
        if selection_method == "random":
            for inv in self.get_random_investments(count=self.max_investments):
                self.assets.append(inv)
        amount_per_asset = round((invested_amount - min_cash) / len(self.assets))
        self.set_asset_prices(self.date)
        for asset in self.assets:
            self.purchase_asset(asset, amount_per_asset)

    def determine_cap_size(self, cap_size_str):
        with sql_cnxn() as cnxn:
            crsr = cnxn.cursor()
            crsr.execute("select `Lower Figure`, `Upper Figure` from `Market Capitalization Brackets` "
                         "where `Bracket Size` = ?", (cap_size_str,))
            res = crsr.fetchone()
            if res is not None:
                self.lower_market_cap = res[0]
                self.upper_market_cap = res[1]
                return True

    def purchase_asset(self, investment_object, max_purchase_amount):
        price = investment_object.price
        units = int(max_purchase_amount // price)
        cost = int(units * price)
        investment_object.amount_at_cost += cost
        investment_object.units += units
        self.cash -= cost
        self.total_cost += cost

    def get_investment(self, ticker, pk):
        with sql_cnxn() as cnxn:
            crsr = cnxn.cursor()
            crsr.execute(
                f"select {','.join(SQLiteInvestment.required_parameters)} from Overview "
                f"where `Investment PK` in (select distinct `Investment PK` from Prices "
                f"where `price date` between ? and ?) "
                f"and (Symbol = ? or `Investment PK` = ?) "
                f"and (select count)",
                (self.date - timedelta(days=5), self.date + timedelta(days=5), ticker, pk)
            )
            res = crsr.fetchone()
            if res is None:
                return
            return SQLiteInvestment(*res)

    def get_random_investments(self, count=10):
        with sql_cnxn() as cnxn:
            crsr = cnxn.cursor()
            selection_query = (
                f"select * from (select {','.join(SQLiteInvestment.required_parameters)} from `Investment Prices` "
                f"where `price date` between ? and ? "
            )
            query_param_values = [self.date, self.date + timedelta(days=7)]
            if self.lower_market_cap is not None:
                selection_query += "and MarketCapitalization >= ?"
                query_param_values += [self.lower_market_cap]
            if self.upper_market_cap is not None:
                selection_query += "and MarketCapitalization <= ?"
                query_param_values += [self.upper_market_cap]
            if self.sectors is not None:
                selection_query += "and Sector in (%s) " % (','.join(['?' for _ in self.sectors]), )
                query_param_values += self.sectors
            if self.industries is not None:
                selection_query += "and Industry in (%s) " % (','.join(['?' for _ in self.industries]), )
                query_param_values += self.industries
            selection_query += "order by `price date`, `Investment PK`) group by `Investment PK`"
            crsr.execute(selection_query, query_param_values)
            rows = crsr.fetchall()
            selected_rows = random.sample(rows, k=min(len(rows), count))
            return [SQLiteInvestment(*row) for row in selected_rows]

    def get_unrealised_gain(self, at_date):
        self.total_unrealised_gain = 0
        self.total_market_value = 0
        self.set_asset_prices(at_date=at_date)
        for asset in self.assets:
            asset.unrealised_gain = asset.market_value - asset.amount_at_cost
            self.total_unrealised_gain += asset.unrealised_gain
        return self.total_unrealised_gain / 100

    def make_assets_chart(self):
        asset_market_value = sum([asset.market_value for asset in self.assets])
        for asset in self.assets:
            asset.percentage_of_portfolio = asset.market_value / asset_market_value
        fig, ax = plt.subplots()
        market_values = []
        labels = []
        for inv in sorted(self.assets, key=lambda x: x.percentage_of_portfolio, reverse=True):
            market_values.append(inv.market_value)
            labels.append(f"{round(100 * inv.percentage_of_portfolio)}% {inv.name}")
        ax.pie(
            x=market_values,
            colors=self.get_chart_colors(),
            wedgeprops=dict(width=0.3),
            startangle=-40
        )
        plt.legend(
            labels=labels,
            loc="upper right",
            bbox_to_anchor=(2, 0.9)
        )
        plt.savefig("Report Resources/asset_values.png", bbox_inches='tight')

    def make_performance_chart(self, at_date):
        periods = []
        for yr in range(self.date.year, at_date.year + 1):
            periods.append(datetime(yr, at_date.month, at_date.day))
        x_axis = [x.strftime("%d/%m/%Y") for x in periods]
        y_axis = []
        largest_mval = 0
        for date_str, per in zip(x_axis, periods):
            self.set_asset_prices(per)
            if self.total_market_value >= largest_mval:
                largest_mval = self.total_market_value
            y_axis.append(self.total_market_value / 100)
        if largest_mval <= 1_000_000_00:
            divisor = 1
        elif largest_mval <= 1_000_000_000_00:
            divisor = 1_000
        else:
            divisor = 1_000_000
        plt.clf()
        plt.xticks(rotation=45)
        plt.plot(x_axis, [round(x / divisor) for x in y_axis])
        plt.grid(True)
        plt.savefig("Report Resources/performance_graph.png", bbox_inches='tight')

    def set_asset_prices(self, at_date):
        self.assets.sort(key=lambda x: x.pk)
        with sql_cnxn() as cnxn:
            crsr = cnxn.cursor()
            crsr.execute(
                "select * from (select `Investment PK`, `price date`, `open` from Prices "
                "where `Investment PK` in (%s) and `price date` between ? and ? "
                "order by `price date`,  `Investment PK`) group by `Investment PK`"
                % (','.join(['?' for _ in self.assets]),),
                [inv.pk for inv in self.assets] + [at_date, at_date + timedelta(days=7)]
            )
            self.total_market_value = 0
            for i, row in enumerate(crsr.fetchall()):
                if i >= len(self.assets):
                    break
                if self.assets[i].pk != row[0]:
                    self.assets[i].price = None
                    self.assets[i].price_date = None
                    self.assets[i].market_value = None
                    continue
                self.assets[i].price = round(row[2] * 100)
                self.assets[i].price_date = row[1]
                self.assets[i].market_value = self.assets[i].units * self.assets[i].price
                self.total_market_value += int(self.assets[i].market_value)

    def get_chart_colors(self):
        rgb_values = None
        if report_generator.short_params_len >= len(self.assets):
            rgb_values = []
            for rgb in report_generator.short_rgb_loop(stop=len(self.assets)):
                rgb_values.append(rgb)
        return rgb_values

    def build_html_report(self, at_date):
        with open("fund_report_template.html", 'r', encoding="utf-8") as rf:
            content = rf.read()
        report_title = "Fund Performance Report %s" % (at_date.strftime("%Y-%m-%d"),)
        report_date = at_date.strftime("%d/%m/%Y")
        start_date = self.date.strftime("%d/%m/%Y")
        with open("Report Resources/%s.html" % (report_title,), 'w', encoding="utf-8") as wf:
            sector_str = ' & '.join([x.strip().title() for x in self.sectors])
            #<tr><th>Name</th><th>Symbol</th><th>Units</th><th>Cost</th><th>Gross Value</th><th>Realised Gain / (Loss)</th></tr>
            investment_template = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            wf.write(
                content.replace(
                    "{{ base_dir }}", os.getcwd()
                ).replace(
                    "{{ report_title }}", report_title
                ).replace(
                    "{{ investment_rows }}", ''.join(
                        [investment_template % (x.name, x.symbol, f'{x.units:,}',  f'{round(x.amount_at_cost / 100):,}',
                         f'{round(x.market_value / 100):,}',
                         str(round((x.market_value / x.amount_at_cost - 1) * 100, 3)) + '%')
                         for x in self.assets]
                    )
                ).replace(
                    "{{ fund_name }}", "%s %s Fund" % (
                        sector_str,
                        self.cap_size_str.title()
                    )
                ).replace(
                    "{{ sector }}", sector_str
                ).replace(
                    "{{ investment_count }}", str(len(self.assets))
                ).replace(
                    "{{ report_date }}", report_date
                ).replace(
                    "{{ start_date }}", start_date
                ).replace(
                    "{{ total_cost }}", f'{round(self.total_cost / 100):,}'
                ).replace(
                    "{{ total_market_value }}", f'{round(self.total_market_value / 100):,}'
                ).replace(
                    "{{ total_return }}", f'{round(self.total_unrealised_gain / 100):,}'
                ).replace(
                    "{{ total_return_percentage }}", f'{round((self.total_market_value / self.total_cost - 1) * 100, 3):,}'
                ).replace(
                    "{{ annualised_return }}", f'{round(self.annualised_return, 3):,}'
                )
            )

    def calculate_results(self, at_date=datetime.today()):
        self.get_unrealised_gain(at_date)
        with open("portfolio_results.csv", 'w', encoding="utf-8", newline='') as wf:
            csv_writer = csv.writer(wf, delimiter="\t", quotechar='"')
            csv_writer.writerow(
                [
                    "PK", "Name", "Symbol", "Sector", "Cost Amount", "Market Value at 31/03/2023",
                    "Unreal Gains / Loss", "Unreal Gains / Loss (%)",
                ]
            )
            for inv in self.assets:
                csv_writer.writerow(
                    [
                        inv.pk, inv.name, inv.symbol, inv.sector, inv.amount_at_cost / 100, inv.market_value / 100,
                        inv.unrealised_gain / 100, (inv.market_value / inv.amount_at_cost - 1) * 100
                    ]
                )
            csv_writer.writerow([])
            csv_writer.writerow(["Portfolio Start Date", self.date])
            csv_writer.writerow(["Portfolio End Date", at_date])
            csv_writer.writerow(["Total Return", self.total_unrealised_gain / 100])
            total_return_factor = self.total_market_value / self.total_cost
            csv_writer.writerow(["Total Return (%)", (total_return_factor - 1) * 100])
            difference_in_years = (at_date.timestamp() - self.date.timestamp()) / (365 * 24 * 60 * 60)
            self.annualised_return = (total_return_factor ** (1 / difference_in_years) - 1) * 100
            csv_writer.writerow(["Annualised Return (%)", self.annualised_return])
            self.make_assets_chart()
            self.make_performance_chart(at_date)
            self.build_html_report(at_date)


class SQLiteInvestment:
    required_parameters = [
        "`Investment PK`", "`Symbol`", "`Name`", "`Description`", "`Currency`", "`Sector`", "`Industry`", "`open`",
        "`price date`"
    ]

    def __init__(self, investment_pk, symbol, name, description, currency, sector, industry, open_price, price_date):
        self.pk = investment_pk
        self.symbol = symbol
        self.name = name
        self.description = description
        self.currency = currency
        self.sector = sector
        self.industry = industry
        self.units = 0
        self.amount_at_cost = 0
        self.market_value = 0
        self.unrealised_gain = 0
        self.percentage_of_portfolio = 0
        self.price = round(open_price * 100)
        self.price_date = price_date

    def get_price(self, date):
        """
        Returns the closest price to the supplied date for the investment specified
        :param date: Datetime of the closest price to be selected from the database
        :return: Price as floating point number
        """
        if date == self.price_date:
            return self.price / 100
        with sql_cnxn() as cnxn:
            crsr = cnxn.cursor()
            crsr.execute(
                "select `price date`, open from Prices where `Investment PK` = ? and `price date` between ? and ? "
                "order by `price date` asc limit 1",
                (self.pk, date, date + timedelta(days=7))
            )
            res = crsr.fetchone()
            if res is None:
                new_price = None
                new_date = None
                return_price = None
            else:
                new_price = round(res[1] * 100)
                new_date = res[0]
                return_price = res[1]
            self.price = new_price
            self.price_date = new_date
            return return_price


if __name__ == "__main__":
    # Please populate with an API key from
    # https://www.alphavantage.co/support/#api-key
    API_KEY = "{{ YOUR API KEY }}"

    # Collects Investment Overview and Price from the alphavantage API and  stores it in the SQLite database
    # get_investments_and_prices()

    # Create a new portfolio. As an example, we'll look at a random selection of 15 Small Cap Finance stocks
    portf = Portfolio(sectors=["TECHNOLOGY"], cap_size="Small-cap", max_investments=15)

    # More examples of investment portfolios
    # portf = Portfolio(sectors=["LIFE SCIENCES"], cap_size="Micro-cap", max_investments=15)
    # portf = Portfolio(sectors=["TECHNOLOGY"], cap_size="Mid-cap", max_investments=25)

    # Prepares the report data to the supplied date. Will generate a csv file called "portfolio_results.csv" and complete
    # an HTML template for reporting the fund under "Report Resources"
    portf.calculate_results(at_date=datetime(2023, 3, 31))


