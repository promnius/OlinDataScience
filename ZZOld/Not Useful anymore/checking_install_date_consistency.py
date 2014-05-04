"""
CURRENT KNOWN ISSUES
code for testing record recieved latency has a bug.

We noticed that many of the machines seem to have discrepencies with data that should be constant but isn't. one 
commonly noticed thing was the install date changes. this script identifies which machines have a constant install
date.

It checks all sorts of discrepencies, including:
install dates not consistent
created at not close to equal recieved at (latency)

Planned Updates:
the function split_up_machine_events should return a list of machines where the machines are sorted alphabeticlly by sn. or at least somehow sorted.
"""

import cyb_records
import time, datetime
import clean_events
TIME_RANGE = 3600

"""Returns true if all install dates are within the acceptable variation of the mean for the given machine. input is a list of records for
ONE machine (use 0 for acceptable_variation to check if they are all identical). acceptable_variation measured in seconds?"""
def install_dates_consistent_or_not(records, acceptable_variation):

    total_time = 0
    excluded = 0 # for dealing with machines that don't have an install date.
    for record in records:
        total_time += int(time.mktime(record.install_date.timetuple())) # turns the install_date entry into a time in seconds??
    ave_install_date = total_time/ (len(records)-excluded)
    
    install_dates_consistent = True
    #print("Install Dates: ")
    for record in records:
        install_date =  int(time.mktime(record.install_date.timetuple()))
        #print install_date
        if (install_date < (ave_install_date - acceptable_variation)) or (install_date > (ave_install_date + acceptable_variation)):
            # install date is not consistent . . . thats not good!
            install_dates_consistent = False
    return install_dates_consistent

"""takes a list of records and splits it up into a bunch of smaller list with homogenous machine serial numbers. it then returns
these lists as one large list. Then you can preform operations on a list of records pertaining to only one machine. Note that these lists
are not sorted by this program (they may come sorted from the database.)"""
def split_up_machine_events(records):
    machines_list = []
    for record in records:
        machine_name = record.sn
        #print machine_name
        event_placed = False
        for machine in machines_list:
            if machine[0].sn == machine_name: # the machine already exists
                machine.append(record)
                event_placed = True
        if event_placed == False: # new machine encountered, add another list to machines_list
            new_list = []
            new_list.append(record)
            machines_list.append(new_list)
    return machines_list

"""Takes a list of machines, where each machine is a list of records for that machine, and determines if any of the machines have inconsistencies
in their install dates. It then prints some stats about the list."""
def check_install_date_consistency(machine_records_list):
    # simple starter test- code depreciated now.    
    #test = install_dates_consistent_or_not(machines_events_list[8], 0)
    #print ("Number of entries in this machine's events: "+str(len(machines_events_list[8])))
    #print ("Do all of these events have a consistent install date? ")
    #print ("Answer: " + str(test))

    install_dates_consistent = []
    for machine in machine_records_list:
        install_date_consistent = install_dates_consistent_or_not(machine, 0)
        install_dates_consistent.append(install_date_consistent)
    num_machines_consistent = 0
    index_counter = 0
    inconsistent_machines = [] # list of strings representing machine serial numbers
    for boolean_value in install_dates_consistent:
        if boolean_value:
            num_machines_consistent += 1
        else: # machine has errors in install date
            inconsistent_machines.append(str(machine_records_list[index_counter][0].sn))
        index_counter +=1
    inconsistent_machines = sorted(inconsistent_machines) # this is why I chose to save the serial numbers as strings
    print(str(num_machines_consistent) + " out of " + str(len(machine_records_list)) + " machines have consistent install dates.")
    print("Machines with inconsistent install dates:")
    for machine in inconsistent_machines:
        print(machine)
    
"""This takes all the records for one machine and determines the number of these records that have unusually high latency. returned as a percentage.
max difference in seconds?
returns: percentage of machines above max_latency, average latency in seconds?"""
def check_created_recieved_discrepancies(records, max_latency):
    latent_records = [] # Note that this isn't returned, but could be. it might contain some useful information.
    total_latency = 0
    for record in records:
        created_time = int(time.mktime(record.created_at.timetuple()))
        recieved_time = int(time.mktime(record.received_at.timetuple()))
        latency = recieved_time - created_time
        if latency < 0:
            # shouldn't be possible
            print("ERROR!! There was a record entry for " + str(record.sn) + " that was recieved before it was created.")
        elif latency > max_latency:
            # machine is highly latent
            latent_records.append(record)
        total_latency += latency
    ave_latency = total_latency/ len(records)
    percent_highly_latent = float((len(latent_records))/ len(records))*100.0
    return percent_highly_latent, ave_latency
        
def main():
    evs = cyb_records.Stats() #"Stat", or "Events", etc.
    evs.ReadRecords()
    machines_events_list = split_up_machine_events(evs.records)
    check_install_date_consistency(machines_events_list)
    max_latency = 60 # seconds?
    
    # testing code- will end up in another function
    #percent, ave_latent = check_created_recieved_discrepancies(machines_events_list[0], max_latency)
    #print ("Machine " + str(machines_events_list[0][0].sn) + " was " + str(percent) +" percent latent (cuttoff at " 
    #       + str(max_latency) + " seconds latent) and had an average latency of " + str(ave_latent) + " seconds")
    
    machine_entries_length = []
    for machine in machines_events_list:
        machine_entries_length.append((len(machine),machine))
    machine_entries_length = sorted(machine_entries_length)
    
    for machine in machine_entries_length:
        print (str(machine[1][0].sn)+ " is in the stats database " + str(machine[0]) + " times.")


    
if __name__ == '__main__':
    main()