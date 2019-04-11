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
#    -> block - tx data, t(tx first appeared) - t(block is mined) is the delay
# 2. How long does a block propagate throughout the entire network?
#    -> can be achieved by current log
# 3. How often do chain splits (i.e., two blocks mined at the same height) occur? 
#    -> need to log the height of blocks & their id
# How long is the longest split you observed? 
# (i.e., smallest distance to least common ancestor of two nodes)

# Plan:
# [the propagation delay]
# 1. minimum, maximum, and median propagation delay
# (histogram of time elapsed) 
# Plot 1: x = time elapsed for half of nodes receiving the transaction, y = count/freq, color = node #
# Plot 2: x = time elapsed for all nodes receiving the transaction, y = count/freq, color = node # 
# 2. number of nodes the transaction reached
# Plot 3: x = time, y = node # has received the transaction, color = transaction, nodes = 20
# Plot 4: x = time, y = node # has received the transaction, color = transaction, nodes = 100
# Heighlight the median propagation on the plots above
# [bandwidth used by your system]
# both the sent and received # Plot the aggregate data for all nodes
# Plot 5: x = time, y = total bandwidth used, color = sent/received, nodes = 20
# Plot 6: x = time, y = total bandwidth used, color = sent/received, nodes = 100

def read_data(filename):
	raw = []
	with open(filename, 'r') as f:
		for line in f:
			record = line.split(' ') # separating sign to be checked
			del record[0]
			if len(record) > 2:
				if record[1] == "TRANSACTION":
					raw.append(record)

	# columns TBD
	# fileString = '{0:.6f}'.format(timestamp_a) + " " + str(self.name) + " " + str(status) + " " 
	# + str(bytes) + " " + str(ttype) + " " + str(txID) + " " + str(fromNode) + " " + str(toNode) 
	# + " " + str(sentTime)  + "\n"
	# name: vm[#]node[i]
	# ttype: TRANSACTION/BLOCK/...etc
	labels = ['timestamp', 'name', 'status', 'bytes', 'ttype', 'txID', 'fromNode', 'toNode', 'sentTime']
	df = pd.DataFrame.from_records(raw, columns=labels)
	return df

def draw_hist(d20, d100, output_filename):
	"""
	d: array
	output_filename: filename without path
	"""
	output_path = "img/"
	output = output_path + output_filename

	sns.set(style="whitegrid")
	f, axes = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
	sns.distplot(d20, kde=False, color="b", ax=axes[0])
	sns.distplot(d100, kde=False, color="r", ax=axes[1])
	plt.setp(axes)
	#fig = plt.get_figure()
	plt.savefig(output)
	plt.close()

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
	if color != None:
		sns_plot = sns.lineplot(x="timestamp", y=y, hue=color, data=df, legend=False)
	else:
		sns_plot = sns.lineplot(x="timestamp", y=y, data=df, legend=False)
	fig = sns_plot.get_figure()
	fig.savefig(output)

# Start to work
raw_df20 = read_data(filename20)
raw_df20['nodeNum'] = 20
raw_df100 = read_data(filename100)
raw_df100['nodeNum'] = 100
raw_df = pd.concat([raw_df20, raw_df100]).reset_index()

df = raw_df[raw_df.ttype == 'TRANSACTION'].sort_values(by=['timestamp']).drop_duplicates(subset=['txID', 'toNode'], keep="first")
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
df['timestampFromNode'] = pd.to_datetime(df['timestampFromNode'], unit='s')
df['bytes'] = df['bytes'].astype(int)

# calculate the time elaspsed from every pair of nodes
df['timeElapsed'] = (df.timestamp - df.timestampFromNode)
df['timeElapsed'] = df['timeElapsed'].dt.microseconds.abs()

# Plot 1
# total elapsed time for each transaction forwarding to exact half of nodes
# histogram: x = timeElapsed
df['rownumByMsg'] = df.sort_values(['timestamp'], ascending=True) \
             .groupby(['txID']) \
             .cumcount() + 1
halfTime = df[df.rownumByMsg > (df.nodeNum/2)].groupby(['txID','nodeNum'])['timeElapsed'].sum().reset_index()
# print(halfTime['timeElapsed'].values)
draw_hist(halfTime[halfTime.nodeNum == 20]['timeElapsed'].values, halfTime[halfTime.nodeNum == 100]['timeElapsed'].values, 'plot01_hist_propagation_delay_half.png')

# Plot 2
# total elapsed time for each transaction forwarding
# histogram: x = timeElapsed
ttlTime = df.groupby(['txID','nodeNum'])['timeElapsed'].sum().reset_index()
draw_hist(ttlTime[ttlTime.nodeNum == 20]['timeElapsed'].values, ttlTime[ttlTime.nodeNum == 100]['timeElapsed'].values, 'plot02_hist_propagation_delay_all.png')

# node# receiving a specific message -> x = timestamp, y = rownumByMsg, color = messageID
draw_line(df[df.nodeNum == 20], 'rownumByMsg', 'txID', 'plot03_line_tx_reached_20.png')
draw_line(df[df.nodeNum == 100], 'rownumByMsg', 'txID', 'plot04_line_tx_reached_100.png')

# total bandwidth ??? time? bandwidth?
df20 = df[df.nodeNum == 20]
df100 = df[df.nodeNum == 100]
df20['cumBandwidth'] = df20['bytes'].cumsum()
df100['cumBandwidth'] = df100['bytes'].cumsum()
# print(df20)
draw_line(df20, 'cumBandwidth', None, 'plot05_line_bandwidth_20.png')
draw_line(df100, 'cumBandwidth', None, 'plot06_line_bandwidth_100.png')
