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
import matplotlib.pyplot as plt
import checking_install_date_consistency as prep
import clean_events

def latest_record(machine):
    #print(str(machine[0].sn) + str(len(machine)) + "entries.")
    latest_timestamp = int(time.mktime(machine[0].received_at.timetuple()))
    latest_record = machine[0]
    #print("latest timestamp:" + str(latest_timestamp))
    for record in machine:
        new_timestamp = int(time.mktime(record.received_at.timetuple()))
        #print ("current timestamp" + str(new_timestamp))
        if new_timestamp > latest_timestamp:
            latest_timestamp = int(time.mktime(record.received_at.timetuple()))
            latest_record = record
            #print "New timestamp is latest."
    return latest_record
        
def main():
    myusername = raw_input("Please enter your username: ")
    mypassword = raw_input("Please enter your password: ")
    
    evs = cyb_records.Stats() #"Stat", or "Events", etc.
    evs.ReadRecords(username = myusername, password = mypassword)
    machines_events_list = prep.split_up_machine_events(evs.records)
    
    current_machines = []
    # format for a machine in current machines:
    # [sn(str), up_time(int), site_code(int), ]
    
    # grab sn, up time from the stats table
    for machine in machines_events_list:
        new_list = []
        if "" in str(machine[0].sn): # optional filtering of which records are collected.
            record = latest_record(machine)
            #print (str(record.sn) + str(record.up_time))#str(int((record.up_time/1000000.0))))
            new_list.append(str(record.sn))
            new_list.append(int(record.up_time))
        current_machines.append(new_list)
    
    
    # add in the facility id from the machines table.
    evs = cyb_records.Machines()
    evs.ReadRecords(username = myusername, password = mypassword)
    for record in evs.records:
        current_sn = str(record.sn)
        for machine in current_machines:
            machine_sn = machine[0]
            if machine_sn == current_sn:
                machine.append(int(record.facility_id))
    #print("First Machine in list: " + str(current_machines[0]))
    
    
    evs = cyb_records.Events()
    evs.ReadRecords(username = myusername, password = mypassword)

    clean_records = clean_events.CleanEvents(evs.records)
    
    errors = []
    
    # add in the number of errors by summing errors for each sn in the error table.
    for record in clean_records:
        machine_found = False
        for machine in errors:
            if machine[0] == str(record.sn):
                machine[1] += 1
                machine_found = True
        if machine_found == False:
            errors.append([str(record.sn), 1])
    #print errors
    
    for error in errors:
        for machine in current_machines:
            if machine[0] == error[0]:
                machine.append(error[1])
    # in case any machines have never thrown an error, make sure they still get an entry
    for machine in current_machines:
        if len(machine) < 4:
            # machine has no prior errors
            machine.append(0)
            
    #print current_machines
    
    # extract the variables
    real_up_time = []
    real_error_count = []
    fake_up_time = []
    fake_error_count = []
    for machine in current_machines:
        site_code = machine[2]
        if site_code >= 9 and site_code <= 12:
            # site is a real one
            real_up_time.append(machine[1])
            real_error_count.append(machine[3])
        else:
            # site code is a fake. still worth trying?
            fake_up_time.append(machine[1])
            fake_error_count.append(machine[3])
    print("Up times: " + str(real_up_time))
    print("Error Counts: " + str(real_error_count))
    
    plt.scatter(real_up_time, real_error_count, s = 100)
    #plt.scatter(fake_up_time, fake_error_count,  s = 20)
    plt.show()
    
if __name__ == '__main__':
    main()