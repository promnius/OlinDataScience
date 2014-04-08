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
	"""
	Create a dictionary. Go through records, and for each type of events create a key; append
	the timestamp value for each key. Return the dictionary.
	"""
	ErrorDict = {}
	prev_sn = ""
	from_date = 1385856000		# Dec 01, 2013
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

def GetErrorsPerWeek(records):
	"""
	Create a new dictionary. For each existing key, create a like key; run through the values
	and for each new week add them up. Append the length of the values in one week to the new
	key.
	"""

	ErrorDict = {}
	from_date = 1385856000		# Dec 01, 2013
	today = 1396828800		# Apr 07, 2014
	one_week = 604800
	i = 0

	for record in records:
		seconds = int(time.mktime(record.timestamp.timetuple()))
		# Skip iteration if it's before the start date of the studied time period
		if seconds < from_date or seconds > today:
			continue
		
		# Get existing data for this error ID if it exists, otherwise create an empty dict
		if record.event_id in ErrorDict.keys():
			CurrentError = ErrorDict.get(record.event_id)
		else:
			CurrentError = {}
		
		# If the error timestamp is after the current week, reset the current week to this one
		if seconds > (from_date + one_week):
			from_date = seconds - 1
			i = 0
		
		# If it's the first error of the week, create the entry in the current dictionary, and count 1 error
		if i == 0:
			current_week = record.timestamp
			CurrentError[current_week] = 1
			i += 1
		# Otherwise, just increment the number of errors for that week
		elif current_week not in CurrentError.keys():
			CurrentError[current_week] = 1
		else:
			CurrentError[current_week] += 1
		
		# Save the data to the errors dictionary
		ErrorDict[record.event_id] = CurrentError
	
 	return ErrorDict

def SumErrors(ErrorDict):
	total = 0
	for key in ErrorDict.keys():
		total += ErrorDict.get(key)

	return total

def ErrorsPerTime(records):
	"""
	For each key, create a list. Make a CDF from that list.
	"""
	all_cdfs = []

	for key in records.keys():
		value = records.get(key)
		
		if len(value) > 30:
			cdf = Cdf.MakeCdfFromList(value, key)
			all_cdfs.append(cdf)

	return all_cdfs

def main():
	all_recs = cyb_records.Events()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	ErrorNames = {"0x80100009": "Watchdog", \
		"0x80100008": "Approaching over-temp", \
		"0x80100005": "Communication issue", \
		"0x80100007": "Controller foldback", \
		"0x80200062": "Unknown"}

	pmfs = []

	errors = GetErrorsPerWeek(all_recs.records)
	for key in errors.keys():
		if SumErrors(errors.get(key)) > 30:
			pmf = Pmf.MakeHistFromDict(errors.get(key), ErrorNames.get(key))
			pmfs.append(pmf)
	myplot.Pmfs(pmfs)
	myplot.Show(title="Histogram: errors rate | 2014-04-08", xlabel = 'Date', ylabel = 'Errors per week')

	#event_timestamps = GetErrorTimestamps(all_recs.records)
	#print 'Number of event codes', len(event_timestamps)
	# for key in event_timestamps.keys():
	# 	print key, len(event_timestamps[key])

	#error_rates = GetErrorsPerWeek(event_timestamps)

	# cdf = ErrorsPerTime(error_rates)
	# myplot.Cdfs(cdf)
	# myplot.Show(title="CDF: errors over time | 2014-04-04", xlabel = 'Date', ylabel = 'CDF')

if __name__ == '__main__':
	main()