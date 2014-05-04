"""
Daily use statistics
"""

import cyb_records
import Cdf
import thinkplot
import time, datetime
import myplot

from scipy import stats
import numpy as np
from scipy.stats import kstest, ks_2samp

def CdfPerDay_ScipyStyle(records):
	all_cdfs = []
	DayDict = {'Sunday': [], 'Monday': [], 'Tuesday':[], 'Wednesday':[], 'Thursday':[], 'Friday':[], 'Saturday':[]}

	# Make dictionary with dates
	for record in records:
		if record.product_configuration == "8114NZJ":
			day = time.strftime("%A", record.in_service.timetuple())
			day_list = DayDict.get(day)
				
			if record.avg_dist < 50000:
				day_list.append(float(record.avg_dist))
				DayDict[day] = day_list

	# Browse dictionary and make CDF
	for key in DayDict.keys():
		value = DayDict.get(key)

		if len(value) > 0:
			cdf = Cdf.MakeCdfFromList(value, key)

			all_cdfs.append(cdf.ps)

	return all_cdfs

def main():
	all_recs = cyb_records.Stats()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	cdf = CdfPerDay_ScipyStyle(all_recs.records)

	print "Fri-norm  ", str(kstest(cdf[5], 'norm'))
	print "Fri-Mon  ", str(ks_2samp(cdf[5], cdf[1]))
	print "Fri-Tue  ", str(ks_2samp(cdf[5], cdf[2]))
	print "Fri-Wed  ", str(ks_2samp(cdf[5], cdf[3]))
	print "Fri-Thu  ", str(ks_2samp(cdf[5], cdf[4]))
	print "Fri-Sat  ", str(ks_2samp(cdf[5], cdf[6]))
	print "Fri-Sun  ", str(ks_2samp(cdf[5], cdf[0]))

if __name__ == '__main__':
    main()