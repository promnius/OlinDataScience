

import cyb_records
import time, datetime
import clean_events
import matplotlib.pyplot as plt
import checking_install_date_consistency as prep
import clean_events


"""pulls out the last chronological record, in the event that the records are NOT sorted by date."""
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
        
        
"""walks through the process of pulling out each variable that is desired from the respective table, and adding them
all to an intuitive list, then splitting the list up by desired factors (such as site code), and plotting the data.
this function is a little long, and maybe should be split up into smaller ones, but outlines one method of drawing data
from all the databases and combining them in a usable fashion. note that this function is VERY innefficient- it uses
linear searches for most of the lookups, and has a few loops that are O(N^2). These can be made more efficient if 
this code ends up being useful, but the order is still irrelevant for the small size of the data bases (Feb 24)"""
def main():
    
    # so that you don't have to type in passwords and usernames every time you connect- since you connect separately
    # for each table.
    myusername = raw_input("Please enter your username: ")
    mypassword = raw_input("Please enter your password: ")
    
    evs = cyb_records.Stats() #"Stat", or "Events", etc.
    evs.ReadRecords(username = myusername, password = mypassword)
    machines_events_list = prep.split_up_machine_events(evs.records)
    
    current_machines = [] # list of all the attributes we are interested in for each machine, for the most current entry.
    # format for a machine in current_machines:
    # [sn(str), up_time(int), site_code(int), number of errors]
    
    # grab sn, up time from the stats table, add them to the current_machines list
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

    #clean_records = clean_events.CleanEvents(evs.records)
    clean_records = evs.records
    print ("Total number of cleaned errors: " + str(len(clean_records)))
    
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
    
    # taking these numbers of errors and adding them to the current_machines list
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
    
    # extract the variables into separate vectors for plotting, based on what we want to plot them by.
    # mainly split up by site code- ignoring sites that don't exist.
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
    
    # preparing to print with color codes for site codes. splitting up main vector again.
    up_time9 = []
    up_time10 = []
    up_time11 = []
    up_time12 = []
    error_count9 = []
    error_count10 = []
    error_count11 = []
    error_count12 = []
    for machine in current_machines:
        site_code = machine[2]
        if site_code == 9:
            up_time9.append(machine[1])
            error_count9.append(machine[3])
        elif site_code == 10:
            up_time10.append(machine[1])
            error_count10.append(machine[3])
        elif site_code == 11:
            up_time11.append(machine[1])
            error_count11.append(machine[3])
        elif site_code == 12:
            up_time12.append(machine[1])
            error_count12.append(machine[3])
        else:
            pass # fake machine
    
    # plotting
    #plt.scatter(real_up_time, real_error_count, s = 100)
    #plt.scatter(fake_up_time, fake_error_count,  s = 20)
    
    
    # PUT THIS IN A FUNCTION!! NO NEED TO HAVE 10 copies!
    up_time9_kilos = []
    for time in up_time9:
        up_time9_kilos.append(time/1000.0)
    up_time10_kilos = []
    for time in up_time10:
        up_time10_kilos.append(time/1000.0)
    up_time11_kilos = []
    for time in up_time11:
        up_time11_kilos.append(time/1000.0)
    up_time12_kilos = []
    for time in up_time12:
        up_time12_kilos.append(time/1000.0)
        
    #plt.scatter(up_time9_kilos, error_count9, facecolor= 'r', s = 300, label= 'site code 9')
    #plt.scatter(up_time10_kilos, error_count10, facecolor= 'b', s = 300, label = 'site code 10')
    #plt.scatter(up_time11_kilos, error_count11, facecolor= 'g', s = 300, label = 'site code 11')
    #plt.scatter(up_time12_kilos, error_count12, facecolor= 'k', s = 300, label = 'site code 12')
 
    # unfiltered version
    plt.scatter(up_time9, error_count9, facecolor= 'r', s = 300, label= 'site code 9')
    plt.scatter(up_time10, error_count10, facecolor= 'b', s = 300, label = 'site code 10')
    plt.scatter(up_time11, error_count11, facecolor= 'g', s = 300, label = 'site code 11')
    plt.scatter(up_time12, error_count12, facecolor= 'k', s = 300, label = 'site code 12')
    
    plt.legend()
    plt.xlabel('Distance (kilometers)', fontsize = 24)
    plt.ylabel('Number of Errors', fontsize = 24)
    plt.title('Errors vs. Distance, by Machine and Site', fontsize = 30)
    plt.xlim([0, 100000000])
    plt.ylim([0,600])
    plt.show()
    
if __name__ == '__main__':
    main()