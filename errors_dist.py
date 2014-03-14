"""
Errors and distance traveled
"""

import cyb_records
import thinkstats2

def CorrErrDist(records):

	ErrorDict = {}

	for record in records:
		if record.description in ErrorDict.keys():
			dist = ErrorDict.get(record.description)
			dist.append(record.dist)
			ErrorDict[record.description] = dist
		else:
			dist = []
			dist.append(record.dist)
			ErrorDict[record.description] = dist

	return ErrorDict

def main():
	all_recs = cyb_records.Errors()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	errors = CorrErrDist(all_recs.records)

	for key in errors.keys:
		print key, SerialCorr(errors.get(key))

if __name__ == '__main__':
    main()