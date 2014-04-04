"""
Detect increasing errors
"""

import cyb_records
import clean_events
import thinkstats2
import time, datetime
import Cdf
import Pmf
import myplot

def GetErrorTimestamps(records):
	ErrorDict = {}
	prev_sn = ""
	from_date = 1377993600		# Sept 01, 2013
	today = 1396569600			# April 04, 2014

	for record in records:
		seconds = int(time.mktime(record.timestamp.timetuple()))
		if seconds > from_date and seconds < today:
			if record.event_id in ErrorDict.keys():
				timestamp_list = ErrorDict.get(record.event_id)
				timestamp_list.append(record.timestamp)
				ErrorDict[record.event_id] = timestamp_list
			else:
				timestamp_list = []
				timestamp_list.append(record.timestamp)
				ErrorDict[record.event_id] = timestamp_list

	return ErrorDict

def Buckets(records):
	ErrorDict = {}
	prev_sn = ""
	from_date = 1377993600		# Sept 01, 2013
	interval = 604800			# One week in seconds

	for record in records:
		x = 1

	return ErrorDict

def GetErrorsPerWeek(record, from_date, to_date):
	seconds = int(time.mktime(record.timestamp.timetuple()))
	if seconds > from_date:
		if record.event_id in ErrorDict.keys():
			timestamp_list = ErrorDict.get(record.event_id)
			timestamp_list.append(record.timestamp)
			ErrorDict[record.event_id] = timestamp_list
		else:
			timestamp_list = []
			timestamp_list.append(record.timestamp)
			ErrorDict[record.event_id] = timestamp_list

def ErrorsPerTime(records):
	all_cdfs = []

	for key in records.keys():
		value = records.get(key)
		
		if len(value) > 15:
			cdf = Cdf.MakeCdfFromList(value, key)
			all_cdfs.append(cdf)

	return all_cdfs

def main():
	all_recs = cyb_records.Events()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	# clean_recs = clean_events.CleanEvents(all_recs.records)
	# print 'Number of clean events', len(clean_recs)

	event_timestamps = GetErrorTimestamps(all_recs.records)
	print 'Number of event codes', len(event_timestamps)
	for key in event_timestamps.keys():
		print key, len(event_timestamps[key])

	cdf = ErrorsPerTime(event_timestamps)
	myplot.Cdfs(cdf)
	myplot.Show(title="CDF: errors over time | 2014-04-04", xlabel = 'Date', ylabel = 'CDF')

	# cdf = ErrorsPerTime(event_timestamps)
	# myplot.Pmfs(pmf)
	# myplot.Show(title="PMF: errors over time | 2014-04-04", xlabel = 'Date', ylabel = 'PMF')

if __name__ == '__main__':
	main()