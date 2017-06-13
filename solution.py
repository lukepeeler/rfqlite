#!/usr/bin/env python

path = '/home/lpeeler/rfqlite/trade_input.txt'

limits = {} # sym -> side -> limit
trades = {} # sym -> side -> [price, qty]

def process_limit(lim_toks):
	# print "proc lim!"
	sym = lim_toks[1]
	limit = float(lim_toks[2])
	side = lim_toks[3]
	if sym in limits:
		limits[sym][side] = limit
	else:
		limits[sym] = {}
		limits[sym][side] = limit
	return
	
	
def process_quote(quote_toks):
	# print "proc quote!"
	sym = quote_toks[1]
	price = float(quote_toks[2])
	side = quote_toks[3]
	qty = int(quote_toks[4])
	my_side = 'B' if side == 'S' else 'S'
	trade_price = None
	if sym not in limits: # no limit for this symbol
		return
	if my_side not in limits[sym]: # opposite side not in limits for this symbol
		return
	limit = limits[sym][my_side]
	if my_side == 'B':
		if limit >= price:
			trade_price = price #### trade price always at quote if trade occurs
	elif my_side == 'S':
		if limit <= price:
			trade_price = price
	if trade_price is not None:
		del limits[sym][my_side] #### trade removes limit
		if sym not in trades:
			trades[sym] = {}
		if my_side not in trades[sym]:
			trades[sym][my_side] = []
		trades[sym][my_side].append([trade_price, qty])
		print_trade(sym, my_side, qty, trade_price)
	return 
	
def print_trade(symbol, side, qty, price):
	print ','.join(map(str, ['T', symbol, side, qty, price]))
	
def print_pnl(symbol, pnl):
	print ','.join(map(str, ['PnL', symbol, pnl]))

def process_close(close_toks):
	sym = close_toks[1]
	close_price = float(close_toks[2])
	# iterate through symbols
	for sym in trades:
		total_shares = 0
		gross_spent = 0.0
		gross_gained = 0.0
		if 'B' in trades[sym]:
			for buy in trades[sym]['B']:
				price = buy[0]
				qty = buy[1]
				total_shares += qty
				gross_spent += price * qty
		if 'S' in trades[sym]:
			for sell in trades[sym]['S']:
				price = sell[0]
				qty = sell[1]
				total_shares -= qty
				gross_gained += price * qty
		# print "gross gain: " + str(gross_gained)
		# print "gross spent: " + str(gross_spent)
		net = gross_gained - gross_spent
		pnl = net + close_price * total_shares
		print_pnl(sym, pnl)

with open(path) as f:
    for line in f:
		line = line.strip() ################ pain point
		toks = line.split(',')
		if toks[0] == 'L':
			process_limit(toks)
		elif toks[0] == 'Q':
			process_quote(toks)
		elif toks[0] == 'C':
			process_close(toks)
		else:
			print "ERROR: unhandled line: " + line
		
		
