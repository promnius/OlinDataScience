"""
Detect specific error rates
"""

import thinkstats2
import time, datetime
import Cdf
import Pmf
import myplot

def GetErrorsPerWeek(records, machine_filter = []):
	"""
	Create a new dictionary. For each existing key, create a like key; run through the values
	and for each new week add them up. Append the length of the values in one week to the new
	key.
	"""

	MachineDict = {}
	one_day = 86400
	one_week = 604800
	eight_weeks = 4838400
	today = int((time.time()/one_day)+1)*one_day
	from_date = today - eight_weeks

	i = 0

	for record in records:
		if len(machine_filter) > 0 and record.sn not in machine_filter:
			continue

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

def PlotPMF(records, machine_filter = []):
	pmfs = []

	errors = GetErrorsPerWeek(records, machine_filter)
	for key in errors.keys():
		if SumErrors(errors.get(key)) > 10:
			pmf = Pmf.MakeHistFromDict(errors.get(key), key)
			pmfs.append(pmf)
	myplot.Pmfs(pmfs)
	myplot.Show(title="Histogram: Error Rate per Week", xlabel = 'Date', ylabel = 'Errors per week')