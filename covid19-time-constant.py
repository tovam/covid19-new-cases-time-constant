import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from calendar import monthrange
import tempfile
import sys
try:
	# pip install backports-datetime-fromisoformat
	from backports.datetime_fromisoformat import MonkeyPatch
	MonkeyPatch.patch_fromisoformat()
except:pass

dataurl = 'https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv'
new_cases_avg = 7     # average window for new cases per day
time_constant_avg = 3 # average window for the time constant
# (_, output_filename) = tempfile.mkstemp('.png')
output_filename = '/tmp/covid19-frstats.png'

def plot_graph(get_formatted_data, filename, new_cases_avg=7, time_constant_avg=3):
	plt.figure(figsize=(12, 6))
	# get data
	total_cases = get_formatted_data()

	# reindexing
	date_str = total_cases.index[0]
	sdate = datetime.fromisoformat(total_cases.index[0]).date()
	edate = datetime.fromisoformat(total_cases.index[-1]).date()
	newindex = [str(sdate + timedelta(days=i)) for i in range((edate-sdate).days + 1)]
	total_cases = total_cases.reindex(newindex)

	# filling blanks
	total_cases = total_cases.fillna(method='ffill')

	# plotting total cases
	ax1 = total_cases.plot(label='Total cases')

	# plotting diff of total cases
	diff_total_cases = total_cases.diff()[1:].clip(lower=1) # set at least 1 new confirmed case per day to have a nice log
	diff_total_cases_avg = diff_total_cases.rolling(new_cases_avg, center=True).mean()
	(diff_total_cases_avg*10).plot(label='New cases (*10)')

	# plotting ln(diff of total cases)
	log_diff = np.log(diff_total_cases_avg)
	(log_diff*100000).plot(label='ln(New cases) (*1e5)')

	# calculating time constant
	diff_log_diff = log_diff.diff().rolling(time_constant_avg, center=True).mean()

	# drawing time constant plot
	ax2 = diff_log_diff.plot(secondary_y=True, color='#d62728', label='New cases time constant $(d^{-1})$')
	ax2.spines['right'].set_color('#d62728')
	ax2.tick_params(axis='y', colors='#d62728')
	ax2.set_ylim(-0.35, 0.35)
	ax2.set_xlim(left=-1)
	ax2.hlines(y=0, xmin=ax2.get_xlim()[0], xmax=ax2.get_xlim()[1], linewidth=1, color='#ffb0b0', linestyles='dashed')
	ax2.hlines(y=0.05, xmin=ax2.get_xlim()[0], xmax=ax2.get_xlim()[1], linewidth=1, color='#d62728', linestyles='dashed')
	bbox = dict(fc='#fbb', ec='none',  alpha=0.8)
	ax2.text(1.3, -0.008, 'New cases per day constant', fontsize=9, bbox=bbox)
	ax2.text(1.3, 0.063-0.018, 'New cases per day double every 14 days', fontsize=9, bbox=bbox)
	totdays = -int(date_str.split('-')[2])+0.5
	xticks = []
	for i,ym in enumerate(np.unique(np.array(list(map(lambda x:x[:7], newindex))))):
	    y,m = list(map(int,ym.split('-')))
	    monthlength = monthrange(y,m)[1]
	    if totdays>0:xticks.append((totdays+int(monthlength/2), '%d-%02d'%(y,m)))
	    ax1.axvspan(totdays, totdays+monthlength, facecolor=['white','lightgrey'][i%2], alpha=0.25)
	    totdays += monthlength
	plt.xticks(*zip(*xticks))

	legend_1 = ax1.legend(loc=2)
	legend_1.remove()
	ax2.legend(loc=4)
	ax2.add_artist(legend_1)

	plt.title('Covid-19 in France: new cases time constant from %s to %s\n'%(sdate, edate))
	ax1.set_xlabel('Date')
	ax1.annotate('Source: '+dataurl, xy=(2, 2), xycoords='figure pixels', annotation_clip=False)
	plt.savefig(filename)
	plt.clf()
	return filename

def get_formatted_data():
	"""
	Output format: one line per day, no hole
		date
		2020-01-24          3.0
		2020-01-25          3.0
		2020-01-26          3.0
		2020-01-27          3.0
		2020-01-28          4.0
	"""
	global dataurl
	data = pd.read_csv(dataurl)
	data = data[data.maille_code=='FRA']
	data = data[data.cas_confirmes.notnull()]
	data = data.groupby(['date'])['cas_confirmes'].max()
	return data

print(plot_graph(get_formatted_data, output_filename, new_cases_avg, time_constant_avg))
