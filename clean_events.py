"""
Cleaning up the event data
"""

import cyb_records
import time, datetime
TIME_RANGE = 3600

def remove_watchdogs(records):
	watchdog_event = '0x80100009'

	clean_records = []

	for record in records:
		if str(record.event_id) != watchdog_event:
			clean_records.append(record)

	return clean_records

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

def main():
	evs = cyb_records.Events()
	evs.ReadRecords()
	all_records = evs.records
	
	unit_test_removing_watchdogs(list(all_records))
	unit_test_clean_records(list(all_records))
	
if __name__ == '__main__':
	main()