# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# MIT License
#
# Copyright (c) 2020 Maharishi Bhatia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# %% [markdown]
# **Import Reference**

# %%
# import chart_studio.plotly as py
import requests
import numpy as np
import pandas as pd
import json
import plotly as py
import plotly.graph_objects as go
from plotly.offline import plot as pyo
import plotly.figure_factory as ff
from lxml import html

# %% [markdown]
# **Json Processing**

# %%
portfolio = json.load(open("./portfolio.json", "r"))
portfolioset = set(portfolio)

# %% [markdown]
# **Call FinWiz site**

# %%
tickers = ','.join(str(s) for s in portfolioset)
URL = 'https://www.finviz.com/screener.ashx?v=110&t='+tickers
page = requests.get(URL)
tree = html.fromstring(page.content)


# %%
screener = tree.xpath('//table[@bgcolor="#d3d3d3"]/tr')

# %% [markdown]
# **Post process HTML scrapping**

# %%
# screener
header = True
stocks = []
for stock in screener:
    if header:
        headerarr = []
        headerarr.append("Group")
        headerarr.append(stock.xpath('./td[2]/text()')[0])
        headerarr.append(stock.xpath('./td[3]/text()')[0])
        headerarr.append(stock.xpath('./td[4]/text()')[0])
        headerarr.append(stock.xpath('./td[9]/text()')[0])
        headerarr.append(stock.xpath('./td[10]/text()')[0])
        headerarr.append("Unit Cost")
        headerarr.append("Qty")
        headerarr.append("Total Cost")
        headerarr.append("UnRealized Gain/Loss")
        headerarr.append("UnRealized Gain/Loss %")
        stocks.append(headerarr)
        header = False
    else:
        uc = "0"
        qty = "0"
        unrgl = 0
        unrglpct = 0
        price = stock.xpath('./td[9]/a/span/text()')[0]  # Price

        if stock.xpath('./td[2]/a/text()')[0] in portfolioset:
            uc = portfolio[stock.xpath('./td[2]/a/text()')[0]]["unitcost"]
            qty = portfolio[stock.xpath('./td[2]/a/text()')[0]]["qty"]
            unrgl = (float(price) - float(uc)) * float(qty)
            unrglpct = ((float(price) - float(uc)) / float(uc))

        arr = []  # stock.xpath('./td/a/text()')
        arr.append(portfolio[stock.xpath(
            './td[2]/a/text()')[0]]["group"])  # Group
        arr.append(stock.xpath('./td[2]/a/text()')[0])  # Ticker
        arr.append(stock.xpath('./td[3]/a/text()')[0])  # Company
        arr.append(stock.xpath('./td[4]/a/text()')[0])  # Sector
        arr.append("${0}".format(price))
        arr.append(stock.xpath('./td[10]/a/span/text()')[0])  # Change
        arr.append("${0}".format(uc))
        arr.append(qty)
        arr.append("${:.2f}".format(float(uc) * float(qty)))
        arr.append("${:.2f}".format(unrgl))
        arr.append("{:.2%}".format(unrglpct))
        stocks.append(arr)
# print(stocks)

# %% [markdown]
# **Attach it to DataFrame**

# %%
dataset = pd.DataFrame(stocks)
headers = dataset.iloc[0]
dataset = dataset[1:]
dataset.rename(columns=headers)


# %%
table = ff.create_table(stocks, height_constant=10, index_title="Portfolio")
table.show()
# pyo(table)


# %%
