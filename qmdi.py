"""
Detect specific error rates
"""

import cyb_records
import clean_events
import thinkstats2
import time, datetime
import Cdf
import Pmf
import myplot

def GetErrorsPerWeek(records):
	"""
	Create a new dictionary. For each existing key, create a like key; run through the values
	and for each new week add them up. Append the length of the values in one week to the new
	key.
	"""

	MachineDict = {}
	#from_date = 1385856000		# Dec 01, 2013
	from_date = 1383264000 		# Nov 01, 2013
	today = 1397692800			# Apr 17, 2014
	one_week = 604800
	one_day = 86400
	i = 0

	for record in records:
		if record.event_id == "0x80100008":
			seconds = int(time.mktime(record.timestamp.timetuple()))
			if seconds < from_date or seconds > today:
				continue

			if record.sn in MachineDict.keys():
				CurrentError = MachineDict.get(record.sn)
			else:
				CurrentError = {}
			
			if seconds > (from_date + one_week):
				from_date = seconds - 1
				i = 0
			
			if i == 0:
				current_week = record.timestamp
				CurrentError[current_week] = 1
				i += 1
			elif current_week not in CurrentError.keys():
				CurrentError[current_week] = 1
			else:
				CurrentError[current_week] += 1
			
			MachineDict[record.sn] = CurrentError
	
 	return MachineDict

def SumErrors(MachineDict):
	total = 0
	for key in MachineDict.keys():
		total += MachineDict.get(key)

	return total

def main():
	all_recs = cyb_records.Events()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	pmfs = []

	errors = GetErrorsPerWeek(all_recs.records)
	for key in errors.keys():
		if SumErrors(errors.get(key)) > 10:
			pmf = Pmf.MakeHistFromDict(errors.get(key), key)
			pmfs.append(pmf)
	myplot.Pmfs(pmfs)
	myplot.Show(title="Histogram: Error Rate per Week for All Treadmills | 2014-04-17", xlabel = 'Date', ylabel = 'Errors per week')

if __name__ == '__main__':
	main()