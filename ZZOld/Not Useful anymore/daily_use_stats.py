"""
Daily use statistics
"""

import cyb_records
import Pmf
import Cdf
import thinkplot
import time, datetime
import myplot

def CdfPerDay(records):
	all_cdfs = []
	DayDict = {'Sunday': [], 'Monday': [], 'Tuesday':[], 'Wednesday':[], 'Thursday':[], 'Friday':[], 'Saturday':[]}

	# Make dictionary with dates
	for record in records:
		if record.facility_id == 12:
		#if record.product_configuration == "8114NZJ":
			day = time.strftime("%A", record.in_service.timetuple())
			day_list = DayDict.get(day)
			#if record.avg_dist < 50000:
			day_list.append(float(record.avg_dist))
			DayDict[day] = day_list

	# Browse dictionary and make CDF
	for key in DayDict.keys():
		value = DayDict.get(key)

		if len(value) > 0:
			cdf = Cdf.MakeCdfFromList(value, key)
			all_cdfs.append(cdf)

	return all_cdfs

def main():
	all_recs = cyb_records.Stats()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	cdf = CdfPerDay(all_recs.records)
	myplot.Cdfs(cdf)
	myplot.Show(title="CDF: daily usage of machines at the YMCA", xlabel = 'Distance (in m / day)', ylabel = 'Percentile')

if __name__ == '__main__':
    main()