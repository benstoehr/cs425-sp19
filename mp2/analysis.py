import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
import re
import json

benslog = "log.txt"

filename20 = "log20.txt"
filename100 = "log100.txt"
filenameBlockTx20 = "blockTx20.txt"
filenameBlockTx100 = "blockTx100.txt"
filenameBlockLog20 = "block20.txt"
filenameBlockLog100 = "block100.txt"

# Log File
# bloxk-tx: [blockHash tx1 tx2 tx3 tx4] (log when node terminates?)
# block level: [timestamp level hash1 hash2 hash3 hash4] (log the current chain when new block created?-	)

# TODO:
# 1. How long does each transaction take to appear in a block? Are there congestion delays?
#    -> block - tx data, t(tx first appeared) - t(block is mined) is the delay -> [blockHash tx1 tx2 tx3 tx4]
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
	ttype_list = ['TRANSACTION', 'BLOCK', 'SOLVED']
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

def read_blockTx(filename):
	raw = []
	with open(filename, 'r') as f:
		for line in f:
			record = line.split(' ') # separating sign to be checked
			if len(record) >= 2:
				raw.append(record)
			
	labels = ['blockHash', 'txID']
	df = pd.DataFrame.from_records(raw, columns=labels)
	return df

def read_blockLog(filename):
	raw = []
	with open(filename, 'r') as f:
		for line in f:
			record = line.split(' ') # separating sign to be checked
			if len(record) >= 2:
				hash_list = []
				record_list = []
				for blockhash in len(record)-2
					i = blockhash + 2
					hash_list.append(reocrd[i]) # hash
				record_list.append(record[0]) # timestamp
				record_list.append(record[1]) # level
				record_list.append(hash_list)
				raw.append(record_list)

	# labels = ['timestamp', 'level', 'blockHashList']
	# df = pd.DataFrame.from_records(raw, columns=labels)
	return raw

def check_split(recordList):
	"""
	recordList: [ts, level, hashList]
	"""

def draw_hist(d, output_filename):
	"""
	d: array
	output_filename: filename without path
	"""
	output_path = "img/"
	output = output_path + output_filename

	sns.set(style="whitegrid")
	sns_plot = sns.distplot(d, kde=False, color="b")
	fig = sns_plot.get_figure()
	fig.savefig(output)
	plt.clf()

def draw_line(df, x, y, color, output_filename):
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
	# sns.set_palette(sns.color_palette("Blues"))
	if color != None:
		sns_plot = sns.lineplot(x=x, y=y, hue=color, data=df, legend=False)
	else:
		sns_plot = sns.lineplot(x=x, y=y, data=df, legend=False)
	fig = sns_plot.get_figure()
	fig.savefig(output)
	plt.clf()

# Start to work
raw_df20 = read_data(filename20)
raw_df20['nodeNum'] = 20
raw_df20['bytes'] = raw_df20['bytes'].astype(int)
raw_df20['timestamp'] = pd.to_datetime(raw_df20['timestamp'], unit='s')
raw_df20['sentTime'] = pd.to_datetime(raw_df20['sentTime'], unit='s')
raw_df100 = read_data(filename100)
raw_df100['nodeNum'] = 100
raw_df100['bytes'] = raw_df100['bytes'].astype(int)
raw_df100['timestamp'] = pd.to_datetime(raw_df100['timestamp'], unit='s')
raw_df100['sentTime'] = pd.to_datetime(raw_df100['sentTime'], unit='s')
print(raw_df20.shape, raw_df100.shape)

raw_df = pd.concat([raw_df20, raw_df100]).reset_index()

# transactions for plots in CP1
tx_df = raw_df[raw_df.status == 'IncomingNodeTransaction'].sort_values(by=['timestamp']).drop_duplicates(subset=['tID', 'toNode'], keep="first")

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

# Plot 3 & 4
# node# receiving a specific message -> x = timestamp, y = rownumByMsg, color = messageID
# adjust time as 0-end
tx20_df = tx_df[tx_df.nodeNum == 20].reset_index()
tx100_df = tx_df[tx_df.nodeNum == 100].reset_index()
print(tx20_df.shape, tx100_df.shape)
tx20_firstSent_df = tx20_df.groupby(['tID'])['sentTime'].min().reset_index()
tx100_firstSent_df = tx100_df.groupby(['tID'])['sentTime'].min().reset_index()
tx20_firstSent = pd.Series(tx20_firstSent_df.sentTime.values,index=tx20_firstSent_df.tID).to_dict()
tx100_firstSent = pd.Series(tx100_firstSent_df.sentTime.values,index=tx100_firstSent_df.tID).to_dict()

def tx20_FS(x):
	return tx20_firstSent[x]

def tx100_FS(x):
	return tx100_firstSent[x]

tx20_df['firstSent'] = tx20_df.tID.apply(tx20_FS)
tx100_df['firstSent'] = tx100_df.tID.apply(tx100_FS)
tx20_df['adjustTime'] = (tx20_df.timestamp - tx20_df.firstSent)
tx100_df['adjustTime'] = (tx100_df.timestamp - tx100_df.firstSent)
tx20_df['adjustTime'] = tx20_df['adjustTime'].dt.microseconds.abs()
tx100_df['adjustTime'] = tx100_df['adjustTime'].dt.microseconds.abs()
tx20_df_rownum = tx20_df.groupby(['rownumByMsg'])['adjustTime'].mean().reset_index()
tx100_df_rownum = tx100_df.groupby(['rownumByMsg'])['adjustTime'].mean().reset_index()
# print(tx20_df_rownum.head(5))
# print(tx100_df_rownum.head(5))

draw_line(tx20_df_rownum, 'rownumByMsg', 'adjustTime', None, 'plot03_line_tx_reached_20.png')
draw_line(tx100_df_rownum, 'rownumByMsg', 'adjustTime', None, 'plot04_line_tx_reached_100.png')
print("done 3 & 4")

# Plot 5 & 6
# total bandwidth (all messages includes tx, block, solve, verify)
# sent: Outgoing*, received: Incoming*
raw_df20['flow'] = raw_df20.status.apply(lambda x: x[:8])
raw_df100['flow'] = raw_df100.status.apply(lambda x: x[:8])

bw20_df = raw_df20[raw_df20.flow == "Incoming"]
bw100_df = raw_df100[raw_df100.flow == "Incoming"]
bw20_df['cumBandwidth'] = bw20_df['bytes'].cumsum()
bw100_df['cumBandwidth'] = bw100_df['bytes'].cumsum()
print(raw_df20.head(5))
draw_line(bw20_df.sort_values(['timestamp'], ascending=True), 'timestamp', 'cumBandwidth', None, 'plot05_line_bandwidth_20.png')
draw_line(bw100_df.sort_values(['timestamp'], ascending=True), 'timestamp', 'cumBandwidth', None, 'plot06_line_bandwidth_100.png')

# Plot 7 & 8
# the congestion delays (tx in block)
# histogram (delay)

blockTx20_df = read_blockTx(filenameBlockTx20)
blockTx100_df = read_blockTx(filenameBlockTx100)

txts_df = tx_df.groupby(['tID'])['timestamp'].min().reset_index()
blockts_df = raw_df[raw_df.status == 'IncomingBlock']groupby(['tID'])['timestamp'].min().reset_index()
blockTx20_df.merge(txts_df, how='left', left_on='txID', right_on='tID', suffixes : ('', '_tx'))
blockTx20_df.merge(blockts_df, how='left', left_on='blockHash', right_on='tID', suffixes : ('', '_block'))
blockTx100_df.merge(txts_df, how='left', left_on='txID', right_on='tID', suffixes : ('', '_tx'))
blockTx100_df.merge(blockts_df, how='left', left_on='blockHash', right_on='tID', suffixes : ('', '_block'))
blockTx20_df['timeElapsed'] = (blockTx20_df.timestamp_block - blockTx20_df.timestamp_tx)
blockTx100_df['timeElapsed'] = (blockTx20_df.timestamp_block - blockTx100_df.timestamp_tx)
blockTx20_df['timeElapsed'] = blockTx20_df['timeElapsed'].dt.microseconds.abs()
blockTx100_df['timeElapsed'] = blockTx100_df['timeElapsed'].dt.microseconds.abs()

draw_hist(blockTx20_df['timeElapsed'].values, 'plot07_hist_propagation_delay_tx_block_20.png')
draw_hist(blockTx100_df['timeElapsed'].values, 'plot08_hist_propagation_delay_tx_block_100.png')

# Plot 9 & 10
# block propagation
# histogram (propagation time)

# blocks take how long to propagate to all nodes
block20_df = raw_df[raw_df.status == 'IncomingBlock' & raw_df.nodeNum == 20].sort_values(by=['timestamp']).drop_duplicates(subset=['tID', 'toNode'], keep="first")
block100_df = raw_df[raw_df.status == 'IncomingBlock' & raw_df.nodeNum == 100].sort_values(by=['timestamp']).drop_duplicates(subset=['tID', 'toNode'], keep="first")

# calculate the time elaspsed from solved to all nodes
block20_solved_df = raw_df[raw_df.ttype == 'SOLVED' & raw_df.nodeNum == 20].groupby(['tID'])['timestamp'].min().reset_index()
block100_solved_df = raw_df[raw_df.ttype == 'SOLVED' & raw_df.nodeNum == 100].groupby(['tID'])['timestamp'].min().reset_index()
block20_solved = pd.Series(block20_solved_df.sentTime.values,index=block20_solved_df.tID).to_dict()
block100_solved = pd.Series(block20_solved_df.sentTime.values,index=block20_solved_df.tID).to_dict()
block20_df['sentTime'] = tx20_df.tID.apply(lambda x: block20_solved[x])
block100_df['sentTime'] = tx100_df.tID.apply(lambda x: block100_solved[x])
##### record the solved time
block20_df['timeElapsed'] = (block20_df.timestamp - block20_df.sentTime)
block100_df['timeElapsed'] = (block100_df.timestamp - block100_df.sentTime)
block20_df['timeElapsed'] = block20_df['timeElapsed'].dt.microseconds.abs()
block100_df['timeElapsed'] = block100_df['timeElapsed'].dt.microseconds.abs()

# total elapsed time for each transaction forwarding
# histogram: x = timeElapsed
ttlTimeBlock20 = block20_df.groupby(['tID'])['timeElapsed'].max().reset_index()
ttlTimeBlock100 = block100_df.groupby(['tID'])['timeElapsed'].max().reset_index()
draw_hist(ttlTimeBlock20['timeElapsed'].values, 'plot09_hist_block_propagation_delay_all_20.png')
draw_hist(ttlTimeBlock100['timeElapsed'].values, 'plot10_hist_block_propagation_delay_all_100.png')

# Plot 11 & 12
# Splits, how often, the longest split (height)
# scatter: x=time, y=split height

# recordList: [ts, level, hashList]
blockLog20 = read_blockLog(filenameBlockLog20)
blockLog100 = read_blockLog(filenameBlockLog100)

for i in len(blockLog20)-1:
	curTimestamp = blockLog20[i][0]
	curLevel = blockLog20[i][1]
	nextTimestamp = blockLog20[i+1][0]
	nextLevel = blockLog20[i+1][1]
