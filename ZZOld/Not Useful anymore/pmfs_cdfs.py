"""
PDFs and CMFs
"""

import cyb_records
import myplot
import Pmf
import Cdf
import urllib
import clean_events
import checking_install_date_consistency as prep

def SnPn(records):
	treadmills_list = []
	recumbent_bikes_list = []
	upright_bikes_list = []
	arc_trainer_list = []

	for record in records:
		pn = record.product_number

		if pn in ["770TX", "625TX", "525TX"]:
			treadmills_list.append(record)
		elif pn == "770R":
			recumbent_bikes_list.append(record)
		elif pn == "770C":
			upright_bikes_list.append(record)
		elif pn in ["625A", "525AT"]:
			arc_trainer_list.append(record)			

	return treadmills_list, recumbent_bikes_list, upright_bikes_list, arc_trainer_list

"""takes a list of records and returns a list of records that only contains machines that have a product number."""
#def real_machines():

def CalcDist(records):
    dist_list = []
    prev_dist = 0

    i = 0

    for record in records:
    	dist = record.avg_dist

    	if i > 0:
    		dist_list.append(dist)
        
        prev_dist = dist
        i = 1

    return dist_list

def CalcTime(records):
    """Extract the pace column and return a list of speeds in m/s."""
    time_list = []
    prev_time = 0

    i = 0

    for record in records:
    	time = record.motor_time
    	delta_time = time - prev_time
    	#print record.sn, time, delta_time

    	if delta_time >= 300 and delta_time <= 7200 and i > 0:
    		time_list.append(delta_time)

    	#if i > 0:
    	#	time_list.append(time)
        
        prev_time = time
        i = 1

    return time_list

def PmfPerMachine(records):
	i = 0
	prev_sn = ''
	current_machine_data = []
	all_pmfs = []

	for record in records:
		if record.sn != prev_sn and i>0:	
			times = CalcTime(current_machine_data)

			if len(times) > 0:
				pmf = Pmf.MakePmfFromList(times, prev_sn)
				all_pmfs.append(pmf)

			current_machine_data = []

		current_machine_data.append(record)
		prev_sn = record.sn

		i += 1

	return all_pmfs

def CdfPerMachine(records):
	i = 0
	prev_sn = ''
	current_machine_data = []
	all_cdfs = []

	for record in records:
		if record.sn != prev_sn and i>0:
			# avg dist
			dist = CalcDist(current_machine_data)

			if len(dist) > 0:
				cdf = Cdf.MakeCdfFromList(dist, prev_sn)
				all_cdfs.append(cdf)

			# time
			# times = CalcTime(current_machine_data)

			# if len(times) > 0:
			# 	cdf = Cdf.MakeCdfFromList(times, prev_sn)
			# 	all_cdfs.append(cdf)

			current_machine_data = []

		current_machine_data.append(record)
		prev_sn = record.sn

		i += 1

	return all_cdfs

def PrintRecords(records):
	print "Product # | Time | Distance"
	record_number = 0

	for record in records:
		print str(record.product_number) + " " + str(record.up_time) + " " + str(record.dist)
		record_number = record_number + 1

		if record_number >= 30:
			break

"""Creates a PDF of error probability sorted by machine, and also prints some basic stats about the errors- such
as the most common error for each machine, and the number of times that error was thrown."""
def Pmf_errors(all_records):
	all_pmfs = []
	clean_records = clean_events.CleanEvents(all_records)
	machines = prep.split_up_machine_events(clean_records)
	# develope a mapping of all possible errors to ingeters
	all_errors = {}
	counter = 1
	for machine in machines:
		for record in machine:
			if record.description in all_errors.keys():
				pass # do nothing, error already recorded
			else:
				all_errors[record.description] = counter
				counter += 1
	print("A dictionary of All the errors: " + str(all_errors))
	print("Number of unique errors in the database: " + str(len(all_errors.keys())))
	
	for machine in machines: # handle each machine separately
		error_frequency = {}
		current_sn = machine[0].sn
		for record in machine: # for every error that this machine has thrown, sort it into the errors dictionary
			if record.description in error_frequency.keys(): # error has occured at least once before, just increment errors
				error_frequency[record.description] = error_frequency[record.description] + 1
			else: # error is a new one
				error_frequency[record.description] = 1
		# calculate the number of unique errors per machine, and the largest number of any one error.
		max_unique_error_occurance = max(error_frequency.values())
		most_occured_error = []
		for code in error_frequency.keys():
			if error_frequency[code] == max_unique_error_occurance:
				most_occured_error.append(code)
		print("Machine: " + str(current_sn) + "Site code: " + str(record.facility_id) + "threw error: " + str(most_occured_error) + " " + str(max_unique_error_occurance) + " times. This was the most of one type of error.")
		max_unique_errors = len(error_frequency.keys())
		print("and this machine had " + str(max_unique_errors) + " unique types of errors.")
		
	# now, convert the error codes to numbers (something that is easily sortable/indexable)
		numerical_error_frequency = {}
		for code in error_frequency.keys():
			error_number = all_errors[code]
			numerical_error_frequency[error_number] = error_frequency[code]
		pmf = Pmf.MakePmfFromDict(numerical_error_frequency, current_sn)
		all_pmfs.append(pmf)
	return all_pmfs
def create_error_pmf():
	all_events = cyb_records.Events()
	all_events.ReadRecords()
	all_records = all_events.records
	my_pmfs = Pmf_errors(all_records)
	myplot.Pmfs(my_pmfs)
	myplot.Show(title="PDF of different types of errors Per Machine", xlabel = 'Error Codes', ylabel = 'Probability')
	

def main():
	all_recs = cyb_records.Stats()
	all_recs.ReadRecords()
	print 'Number of total stats', len(all_recs.records)

	cdf = CdfPerMachine(all_recs.records)
	myplot.Cdfs(cdf)
	myplot.Show(title="CDF of cardio machine average distances", xlabel = 'Average Distances', ylabel = 'Probability')
	# pmfs = PmfPerMachine(all_recs.records)
	# myplot.Pmfs(pmfs)
	# myplot.Show(title='PMF cardio speeds',
	# 	       xlabel='duration (sec)',
 #               ylabel='probability')

if __name__ == '__main__':
    #main()
    create_error_pmf()