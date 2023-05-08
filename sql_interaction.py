import sqlite3
from contextlib import contextmanager
import os


@contextmanager
def sql_cnxn():
    if not os.path.exists("investment_data"):
        os.mkdir("investment_data")
    if not os.path.exists("investment_data/PortfolioAnalysis.db"):
        open("investment_data/PortfolioAnalysis.db", 'wb').close()
    cnxn = sqlite3.connect("investment_data/PortfolioAnalysis.db")
    yield cnxn
    cnxn.close()
