import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import re

filename20 = "log20.txt"
filename100 = "log100.txt"

# TODO:
# 1. How long does each transaction take to appear in a block? Are there congestion delays?
#    -> block - tx data, t(tx first appeared) - t(block is mined) is the delay -> {block: [tx1, tx2, ..]}
# 2. How long does a block propagate throughout the entire network?
#    -> can be achieved by current log
# 3. How often do chain splits (i.e., two blocks mined at the same height) occur? 
#    -> need to log the height of blocks & their id
# How long is the longest split you observed? 
# (i.e., smallest distance to least common ancestor of two nodes)
######## -> log timestamp and current chain when new block created? [timestamp level hash1 hash2 hash3 ...]

# Plan:
# [the propagation delay]
# 1. minimum, maximum, and median propagation delay
# (histogram of time elapsed) 
# Plot 1-1, 1-2: x = time elapsed for half of nodes receiving the transaction, y = count/freq
# Plot 2-1, 2-2: x = time elapsed for all nodes receiving the transaction, y = count/freq 
# 2. number of nodes the transaction reached
# Plot 3: x = time, y = node # has received the transaction, color = transaction, nodes = 20
# Plot 4: x = time, y = node # has received the transaction, color = transaction, nodes = 100
# Heighlight the median propagation on the plots above
# [bandwidth used by your system]
# both the sent and received # Plot the aggregate data for all nodes
# Plot 5: x = time, y = total bandwidth used, color = sent/received, nodes = 20
# Plot 6: x = time, y = total bandwidth used, color = sent/received, nodes = 100
# []

def read_data(filename):
	raw = []
	ttype_list = ['TRANSACTION', 'BLOCK']
	with open(filename, 'r') as f:
		for line in f:
			record = line.split(' ') # separating sign to be checked
			if len(record) > 2:
				if record[4] in ttype_list:
					raw.append(record)

    # fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + 
    # " " + str(bytes) + " " + str(ttype) + " " + str(tID) + " " + str(fromNode) + " " + 
    # str(toNode) + " " + str(sentTime) + "\n"
	# name: vm[#]node[i]
	# ttype: TRANSACTION/BLOCK/...etc
	# tID: Tx: txID/Block: selfHash/Puzzle: hash/Verify: hash_solution
	labels = ['timestamp', 'name', 'status', 'bytes', 'ttype', 'tID', 'fromNode', 'toNode', 'sentTime']
	df = pd.DataFrame.from_records(raw, columns=labels)
	return df

def draw_hist(d, output_filename):
	"""
	d: array
	output_filename: filename without path
	"""
	output_path = "img/"
	output = output_path + output_filename

	sns.set(style="whitegrid")
	sns.distplot(d, kde=False, color="b")
	fig = sns_plot.get_figure()
	fig.savefig(output)
	plt.clf()

def draw_line(df, y, color, output_filename):
	"""
	df: dataframe
	y: the column for y axis
	color: the grouping column
	output_filename: filename without path
	"""
	output_path = "img/"
	output = output_path + output_filename

	sns_plot = ""
	sns.set(style="whitegrid")
	sns.despine(left=True)
	sns.palplot(sns.color_palette("Blues"))
	if color != None:
		sns_plot = sns.lineplot(x="timestamp", y=y, hue=color, data=df, legend=False)
	else:
		sns_plot = sns.lineplot(x="timestamp", y=y, data=df, legend=False)
	fig = sns_plot.get_figure()
	fig.savefig(output)
	plt.clf()

# Start to work
raw_df20 = read_data(filename20)
raw_df20['nodeNum'] = 20
raw_df100 = read_data(filename100)
raw_df100['nodeNum'] = 100

# deal with timestamp
raw_df = pd.concat([raw_df20, raw_df100]).reset_index()
raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'], unit='s')
raw_df['sentTime'] = pd.to_datetime(raw_df['sentTime'], unit='s')
raw_df['bytes'] = raw_df['bytes'].astype(int)

# transactions for plots in CP1
tx_df = raw_df[raw_df.status == 'IncomingNodeTransaction'].sort_values(by=['timestamp']).drop_duplicates(subset=['txID', 'toNode'], keep="first")

# calculate the time elaspsed from every pair of nodes
tx_df['timeElapsed'] = (tx_df.timestamp - tx_df.sentTime)
tx_df['timeElapsed'] = tx_df['timeElapsed'].dt.microseconds.abs()

# Plot 1
# total elapsed time for each transaction forwarding to exact half of nodes
# histogram: x = timeElapsed
tx_df['rownumByMsg'] = tx_df.sort_values(['timestamp'], ascending=True) \
             .groupby(['tID','nodeNum']) \
             .cumcount() + 1
halfTime = tx_df[tx_df.rownumByMsg > (tx_df.nodeNum/2)].groupby(['tID','nodeNum'])['timeElapsed'].sum().reset_index()
# print(halfTime['timeElapsed'].values)
draw_hist(halfTime[halfTime.nodeNum == 20]['timeElapsed'].values, 'plot01-1_hist_propagation_delay_half_20.png')
draw_hist(halfTime[halfTime.nodeNum == 100]['timeElapsed'].values, 'plot01-2_hist_propagation_delay_half_100.png')

# Plot 2
# total elapsed time for each transaction forwarding
# histogram: x = timeElapsed
ttlTime = tx_df.groupby(['tID','nodeNum'])['timeElapsed'].sum().reset_index()
draw_hist(ttlTime[ttlTime.nodeNum == 20]['timeElapsed'].values, 'plot02-1_hist_propagation_delay_all_20.png')
draw_hist(ttlTime[ttlTime.nodeNum == 100]['timeElapsed'].values, 'plot02-2_hist_propagation_delay_all_100.png')

# node# receiving a specific message -> x = timestamp, y = rownumByMsg, color = messageID
# adjust time as 0-end
tx20_df = tx_df[tx_df.nodeNum == 20]
tx100_df = tx_df[tx_df.nodeNum == 100]
tx20_firstSent = tx20_df.groupby(['tID'])['sentTime'].min().to_dict()
tx100_firstSent = tx100_df.groupby(['tID'])['sentTime'].min().to_dict()

tx20_df['firstSent'] = tx20_df.tID.map(tx20_firstSent)
tx100_df['firstSent'] = tx100_df.tID.map(tx100_firstSent)
tx20_df['timestamp'] = tx20_df.timestamp - tx20_df.firstSent
tx100_df['timestamp'] = tx100_df.timestamp - tx100_df.firstSent
tx20_df['timestamp'] = tx20_df['timestamp'].dt.microseconds.abs()
tx100_df['timestamp'] = tx100_df['timestamp'].dt.microseconds.abs()

draw_line(tx20_df, 'rownumByMsg', 'tID', 'plot03_line_tx_reached_20.png')
draw_line(tx100_df, 'rownumByMsg', 'tID', 'plot04_line_tx_reached_100.png')

# total bandwidth (all messages includes tx, block, solve, verify)
# sent: Outgoing*, received: Incoming*
raw_df20['flow'] = raw_df20.status.apply(lambda x: x[:8])
raw_df100['flow'] = raw_df100.status.apply(lambda x: x[:8])
raw_df20['cumBandwidth'] = raw_df20['bytes'].cumsum()
raw_df100['cumBandwidth'] = raw_df100['bytes'].cumsum()
# print(df20)
draw_line(raw_df20, 'cumBandwidth', 'flow', 'plot05_line_bandwidth_20.png')
draw_line(raw_df100, 'cumBandwidth', 'flow', 'plot06_line_bandwidth_100.png')
