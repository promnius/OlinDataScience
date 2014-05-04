"""
Cleaning up the event data
"""

import cyb_records
import time, datetime
TIME_RANGE = 3600

'''This function tries to remove all the errors that aren't actually errors because they are, in fact, only watchdogs
that are thrown on machine startup regardless of condition. Note that because the error codes are so cryptic, we are
only removing the most common of the watchdogs. There may be more similar errors.'''
def remove_watchdogs(records):
	# 9, 12, 13, 29 are the different things turning on- aka, not errors
	# quick defining the error strings as constants
	err9 = '0x80100009'
	#err12 = '0x8000000C'
	#err13 = '0x8000000D'
	#errtest = '0x80000016'

	indexes_to_remove = [err9]
	
	records = remove_specific_errors(records, indexes_to_remove)

	return records

'''This function cleans a dataset of errors by removing errors of specific error code, where error_codes
is a list of strings representing the hexidecimal error codes to be removed.'''
def remove_specific_errors(records, error_codes):
	local_debugging = False
	first_time_through_loop = True
	indexes_to_remove = []
	index = 0
	for record in records:
		if first_time_through_loop and local_debugging: # print one record so I can know what form it comes in
			print("event id of the first record (for formatting purposes): " + str(record.event_id))
			quick_test = False
		ev_id = str(record.event_id) # event id
		if ev_id in error_codes: # then the record is a watchdog. not included in final records.
			indexes_to_remove.append(index)
		index += 1
	if local_debugging:
		print('list of indexes, original order: ' + str(indexes_to_remove))
	indexes_to_remove.sort(reverse=True)
	if local_debugging:
		print('list of indexes, reverse sorted: ' + str(indexes_to_remove))
	# making sure we remove the last index first, because removing the first index would shift the location of the rest of them.
	for index in indexes_to_remove:
		records.pop(index)
	return records

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

def unit_test_removing_watchdogs(records):
	num_records = len(records)
	print ('Number of total events' + str(num_records))
	
	no_watchdog_records = remove_watchdogs(records)
	num_no_watchdog_records = len(no_watchdog_records)
	print ("Number of events that are NOT watchdogs: " + str(num_no_watchdog_records))
	num_watchdog_errors = num_records - num_no_watchdog_records
	print ("Number of watchdog errors removed: " + str(num_watchdog_errors))
	print ("Percent of records that are watchdog errors: " + str("%.2f" % ((num_watchdog_errors * 100.0)/ num_records)) + "%")

def unit_test_clean_records(records):
	num_records = len(records)
	print ('Number of total events: ' + str(num_records))

	clean_records = CleanEvents(records)
	num_clean_records = len(clean_records)
	print ("Number of clean events: " + str(num_clean_records))
	print ("Example of the clean records: ")
	PrintRecords(clean_records)

def main():
	evs = cyb_records.Events()
	evs.ReadRecords()
	all_records = evs.records
	
	# select one of these if you want to run a test.
	unit_test_removing_watchdogs(list(all_records)) # pass a copy of all_records
	unit_test_clean_records(list(all_records))
	
if __name__ == '__main__':
	main()