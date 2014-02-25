"""
PDFs and CMFs
"""

import cyb_records
import myplot
import Pmf
import Cdf
import urllib
import clean_events

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
    main()