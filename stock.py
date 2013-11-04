import numpy as np
import pandas as pd
import requests
import StringIO
from pattern import web

def save_stock_data(symbol):
	try:
		url = "http://ichart.finance.yahoo.com/table.csv?s=" + symbol + "&ignore=.csv"
		data = requests.get(url).text
		pd.read_csv(StringIO.StringIO(data))
		f = open('data/' + symbol + '.csv', 'w')
		f.write(data)
		f.close()
	except Exception:
		print "Unable to download %s" % symbol
	

def load_symbols(exchange):
	return pd.read_csv('data/' + exchange + '.txt', sep='\t')

def save_all_stocks_data():
	for exchange in ['NASDAQ', 'NYSE']:
		for symbol in load_symbols(exchange)['Symbol']:
			save_stock_data(symbol)
			
def leaf_node(n):
	while n.children is not None and len(n.children) > 0 and n.children[0].type == 'element':
		n = n.children[0]
	return n
			
def save_analyst_opinion_data(symbol):
	try:
		url = "http://finance.yahoo.com/q/ud?s=" + symbol
		page = web.DOM(requests.get(url).text)
		data = page('table.yfnc_datamodoutline1 tr table tr')
		if len(data) > 1:
			columns = [leaf_node(n).content for n in data[0].children]
			entries = []
			for i in range(1, len(data)):
				entries.append([leaf_node(n).content for n in data[i].children])
			df = pd.DataFrame(entries, columns=columns)
			format = "%d-%b-%y"
			df['Date'] = pd.to_datetime(df['Date'], format=format)
			df = df.set_index('Date').sort_index(ascending=False)
			df.to_csv('data/analyst_opinion/' + symbol + '.txt')			
	except Exception:
		print "Unable to download analyst_opinion for %s" % symbol
		
def save_all_analyst_opinion_data():		
	for exchange in ['NASDAQ', 'NYSE']:
		for symbol in load_symbols(exchange)['Symbol']:
			save_analyst_opinion_data(symbol)
			
def save_all_stock_info():
	f = open('data/stock_info.csv', 'w')
	f.write("MarketCap,'PE','EPS','Dividend','DividentPct'\n")
	symbols, marketcaps, pes, epss, dividends, dividendpcts = [], [], [], [], [], []
	for exchange in ['NASDAQ', 'NYSE']:
		for symbol in load_symbols(exchange)['Symbol']:
			try:
				url = "http://finance.yahoo.com/q?s=" + symbol
				page = web.DOM(requests.get(url).text)
				data = page('table#table2 td.yfnc_tabledata1')
				market_cap = data[-4]('span')[0].content
				if market_cap[-1] == 'B':
					market_cap = float(market_cap[:-1]) * 10**9
				elif market_cap[-1] == 'M':
					market_cap = float(market_cap[:-1]) * 10**6
				else:
					market_cap = np.nan
				
				P_E = np.nan
				try:
					P_E = float(data[-3].content)
				except ValueError:
					P_E = np.nan
				
				EPS = np.nan
				try:
					EPS = float(data[-2].content)
				except ValueError:
					EPS = np.nan
				
				dividend_amount = np.nan
				dividend_pct = np.nan
				try:
					dividend_amount, dividend_pct = data[-1].content.strip().split(' ')
					dividend_amount = float(dividend_amount)
					dividend_pct = float(dividend_pct[1:-2])
				except ValueError:
					dividend_amount = np.nan
					dividend_pct = np.nan
				
				symbols.append(symbol)
				marketcaps.append(market_cap)
				pes.append(P_E)
				epss.append(EPS)
				dividends.append(dividend_amount)
				dividendpcts.append(dividend_pct)
			except Exception:
				print "Unable to get info for %s" % symbol
	df = pd.DataFrame({'Symbol': symbols, 'MarketCap': marketcaps, 'PE': pes, 'EPS': epss, 'Dividend': dividends, 'DividendPct': dividendpcts})
	df = df.set_index('Symbol').sort_index()
	df.to_csv('data/stock_info.txt')