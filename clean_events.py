"""
Cleaning up the event data
"""

import cyb_records
import time, datetime
TIME_RANGE = 3600

def CleanEvents(records):
	"""
	Change yyyy-mm-dd hh:mm:ss to seconds since epoch 2008 Jan 01.
	Check if events with same serial number are within the range (i.e. duplicates), and add all unique events to new list.
	"""

	clean_events_list = []
	prev_sn = ""
	prev_timestamp = 0
	unique_event = True

	for record in records:
		sn = record.sn
		timestamp = int(time.mktime(record.timestamp.timetuple()))

		if sn == prev_sn:
			if (timestamp - prev_timestamp) >= TIME_RANGE:
				unique_event = True
			else:
				unique_event = False

		if unique_event:
			clean_events_list.append(record)

		prev_sn = sn
		prev_timestamp = timestamp

	return clean_events_list


def PrintRecords(records):
	#for field in records[0].__dict__.keys():
		#print field + " | ",

	print "sn | error | timestamp"
	print "----"

	record_number = 0

	for record in records:
		print str(record.sn) + " " + str(record.description) + "           " + str(record.timestamp)
		record_number = record_number + 1
		#for key in record.__dict__.keys():
			#print str(getattr(record, key)) + " | ",
		#print "~~~~"
		if record_number >= 15:
			break


def main():
    evs = cyb_records.Events()
    evs.ReadRecords()
    print 'Number of total events', len(evs.records)

    clean_records = CleanEvents(evs.records)
    print "Number of clean events", len(clean_records)
    PrintRecords(clean_records)


if __name__ == '__main__':
    main()