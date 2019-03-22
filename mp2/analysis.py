import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt

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
	    	raw.append(record)

	# columns TBD
	labels = ['timestamp', 'type', 'txID', 'message', 'fromNode', 'toNode', 'timestampFromNode', 'status', 'nodeNum', 'bytes']
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
	sns.despine(left=True)
	sns.distplot(d20, kde=False, color="b", ax=axes[0, 0])
	sns.distplot(d100, kde=False, color="r", ax=axes[0, 0])
	plt.setp(axes, yticks=[])
	fig = plt.get_figure()
	fig.savefig(output)

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
		sns_plot = sns.lineplot(x="timestamp", y=y, hue=color, data=df)
	else:
		sns_plot = sns.lineplot(x="timestamp", y=y, data=df)
	fig = sns_plot.get_figure()
	fig.savefig(output)

# TODO: total bandwidth
# have to record how many bytes used in logging

df = raw_df[draw_dff.status == 'first-time' & draw_dff.type == 'TRANSACTION']

# calculate the time elaspsed from every pair of nodes
df['timeElapsed'] = (df.timestamp - df.timestampFromNode).microseconds

# Plot 1
# total elapsed time for each transaction forwarding to exact half of nodes
# histogram: x = timeElapsed
df['rownumByMsg'] = df.sort_values(['timestamp'], ascending=True) \
             .groupby(['txID']) \
             .cumcount() + 1
halfTime = df['rownumByMsg' > HalfNodeNum].group_by(['messageID']).sum(['timeElapsed'])
draw_hist(halfTime[halfTime.nodeNum == 20], halfTime[halfTime.nodeNum == 100], 'plot01_hist_propagation_delay_half.png')

# Plot 2
# total elapsed time for each transaction forwarding
# histogram: x = timeElapsed
ttlTime = df.group_by(['txID']).sum(['timeElapsed']) 
draw_hist(ttlTime[ttlTime.nodeNum == 20], ttlTime[ttlTime.nodeNum == 100], 'plot02_hist_propagation_delay_all.png')

# node# receiving a specific message -> x = timestamp, y = rownumByMsg, color = messageID
draw_line(df[df.nodeNum == 20], 'rownumByMsg', 'txID', 'plot03_line_tx_reached_20.png')
draw_line(df[df.nodeNum == 100], 'rownumByMsg', 'txID', 'plot04_line_tx_reached_100.png')

# total bandwidth ??? time? bandwidth?
df20 = df[df.nodeNum == 20]
df100 = df[df.nodeNum == 100]
df20['cumBandwidth'] = df20['bytes'].cumsum()
df100['cumBandwidth'] = df100['bytes'].cumsum()
draw_line(df20, 'cumBandwidth', 'direction', 'plot05_line_bandwidth_20.png')
draw_line(df100, 'cumBandwidth', 'direction', 'plot06_line_bandwidth_100.png')