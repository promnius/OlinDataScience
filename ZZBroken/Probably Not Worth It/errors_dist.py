"""
Errors and distance traveled
"""

import cyb_records_2
import thinkstats2
import clean_events
import time, datetime

def CorrErrDist(records):

	ErrorDict = {}
	prev_sn = ""

	for record in records:

		if record.event_id in ErrorDict.keys():
			dist = ErrorDict.get(record.event_id)
			dist.append(record.dist)
			ErrorDict[record.event_id] = dist
		else:
			dist = []
			dist.append(record.dist)
			ErrorDict[record.event_id] = dist

	return ErrorDict

def main():
	all_recs = cyb_records_2.Errors()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	clean_recs = clean_events.CleanEvents(all_recs.records)
	print 'Number of clean events', len(clean_recs)

	errors = CorrErrDist(clean_recs)
	print 'Number of dict entries', len(errors)

	for key in errors.keys():
	 	print "Error id =", key, "Correlation =", thinkstats2.SerialCorr(errors.get(key)), "List length =", len(errors.get(key))

if __name__ == '__main__':
    main()