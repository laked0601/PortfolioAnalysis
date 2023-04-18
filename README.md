# PortfolioAnalysis
An Investment Fund reporting tool and generator built from scratch using SQLite and Python. Collects data using the stock market API at https://www.alphavantage.co/ and can model how a diverse selection of investment strategies have historically performed.
<h2>📌 Context</h2>
<ul>
  <li>An Investment Fund is a financial instrument that holds ownership in a diverse selection of assets intended to meet the desired investment strategy of it's investors. Investment funds play a critical role in diversifying investment portfolios to achieve desired financial outcomes. </li>
  <li>This research project aims to explore how investment portfolios can be effectively constructed, and their historic performance can be measured and reported to investors.</li>
  <li>It includes an SQLite based built around a Python Application, which is specifically designed to collect historic performance data for approximately 1400 stocks of varying size, market sector and industry in the United States. This data is then analysed, according to a desired investment strategy, to calculate fund returns to investors over time.</li>
</ul>
<h2>⚙️ How it Works</h2>
<ul>
  <li>The code is designed to store market data from the web API at alphavantage.co and can generate the actual returns of a theoretical, historic investment strategy, as well as a detailed report showing the fund's asset weighting, performance each year, and the unrealized gain on each asset since inception.</li>
  <li>For example, here is the generated report for an investment portfolio consisting of 15 Finance stocks with Small Market Capitalization established in January 2015:</li>
</ul>
<img src='https://user-images.githubusercontent.com/90655952/232638297-f1c056f6-62e2-4d14-8886-9cf6f1d495b5.png'>
<ul><li>For the above report, the following code was used:</li></ul>

```python
# Create a new portfolio. As an example, we'll look at a random selection of 15 Small Cap Finance stocks
portf = Portfolio(sectors=["FINANCE"], cap_size="Small-cap", max_investments=15)

# Prepares the report data to the supplied date. Will generate a csv file called "portfolio_results.csv" and complete
# an HTML template for reporting the fund under "Report Resources"
portf.calculate_results(at_date=datetime(2023, 3, 31))
```

<h2>📁 Installation</h2>
<h3>Prerequisites</h3>
<ul>
  <li>Install Python and add it to your system path<br><a href='https://www.python.org/downloads/'>https://www.python.org/downloads/</a></li>
  <li>Run 'setup.bat' or 'setup.sh'. This will create the required SQLite Database and populate the tables and views needed to store the data.</li>
  <li>Register for a new API key alphavantage.co and add your API key to 'main.py':<br><a href='https://www.alphavantage.co/support/#api-key'>https://www.alphavantage.co/support/#api-key</a></li>
  <li>*Optional* Install SQLite studio at <a href='https://sqlitestudio.pl/'>https://sqlitestudio.pl/</a>. This is a graphical interface for SQLite will make reading and understanding the data in the SQLite database much easier.</li>
</ul>
<p>Once complete, 'main.py' should look like this</p>

```python
if __name__ == "__main__":
 # Please populate with an API key from
 # https://www.alphavantage.co/support/#api-key
 API_KEY = "{{ YOUR API KEY }}"

 # Collects Investment Overview and Price from the alphavantage API and  stores it in the SQLite database
 # get_investments_and_prices()

 # Create a new portfolio. As an example, we'll look at a random selection of 15 Small Cap Finance stocks
 portf = Portfolio(sectors=["FINANCE"], cap_size="Small-cap", max_investments=15)

 # More examples of investment portfolios
 # portf = Portfolio(sectors=["LIFE SCIENCES"], cap_size="Micro-cap", max_investments=15)
 # portf = Portfolio(sectors=["TECHNOLOGY"], cap_size="Mid-cap", max_investments=25)

 # Prepares the report data to the supplied date. Will generate a csv file called "portfolio_results.csv" and complete
 # an HTML template for reporting the fund under "Report Resources"
 portf.calculate_results(at_date=datetime(2023, 3, 31))
```

<p>This is now ready to run and can produce an example report for the performance of a Fund of your desired strategy under "/Report Resources/". For spreadsheet analysis, a file called "portfolio_results.csv" will be created which can be modified as needed.</p>
