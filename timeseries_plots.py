"""
Errors and distance traveled
"""

import cyb_records
import thinkstats2
import clean_events
import time, datetime
import checking_install_date_consistency as prep
import matplotlib.pyplot as plt

'''This function is in the wrong file- should maybe be in clean records, or some kind of sort records.
maybe the same file as the 'sort by machines' is in.'''
'''This function takes the machines database, and returns a dictionary containing all of the machine serial
numbers in the database, sorted by site code. Note that the 'sort by site code' part is currently not adaptive-
it uses a list of known site codes rather than reading them from the database. This can be improved in the future.
Efficiency is also low- by using the right SQL query, the complexity of this algorithem could drop significantly.'''
'''Also, could make this a class that stores the sns, rather than re-running it every time. it would be less server 
load that way.'''
def all_sns_by_site(username = None, password = None):
    collecting_site_codes = cyb_records.Machines()
    if password != None and username != None:
        collecting_site_codes.ReadRecords(username = username, password = password)
    else:
        collecting_site_codes.ReadRecords()

    all_serial_numbers = []
    cybex_showroom_sns = []
    planet_fitness_1_sns = []
    YMCA_sns = []
    holiday_inn_sns = []
    planet_fitness_2_sns = []
    for record in collecting_site_codes.records:
        if record.sn not in all_serial_numbers: # we haven't added this one yet.
            all_serial_numbers.append(record.sn)
            if record.facility_id == 10: # cybex showroom
                cybex_showroom_sns.append(record.sn)
            elif record.facility_id == 11: # planet fitness
                planet_fitness_1_sns.append(record.sn)
            elif record.facility_id == 12: # YMCA
                YMCA_sns.append(record.sn)
            elif record.facility_id == 13: # holiday inn
                holiday_inn_sns.append(record.sn)
            elif record.facility_id == 14: # planet fitness #2
                planet_fitness_2_sns.append(record.sn)
    sns_by_site = {}
    sns_by_site[10] = cybex_showroom_sns
    sns_by_site[11] = planet_fitness_1_sns
    sns_by_site[12] = YMCA_sns
    sns_by_site[13] = holiday_inn_sns
    sns_by_site[14] = planet_fitness_2_sns
    return sns_by_site
    
    
def time_vs_errors_for_one_site_code(clean_recs, sitecode, username=None, password=None):
    colors = ['b', 'g', 'r', 'k', 'm']
    plt.figure()
    
    # getting site codes so we can plot by site.
    sns_by_site = all_sns_by_site(username = username, password = password)

    machines = prep.split_up_machine_events(clean_recs)
    real_machines = sns_by_site[sitecode]
    
    num_machines_plotted = 0
    for machine in machines:
        if machine[0].sn in real_machines: # this machine is worth plotting
            times = []
            num_errors = []
            error_counter = 1
            for record in machine:
                times.append(record.timestamp) # altered from created_at. other option: received_at, timestamp
            times.sort()
            for time in times:
                num_errors.append(error_counter)
                error_counter += 1
            
            print('Number of events for this machine: ' + str(len(times)))
            print('Machine being shown: ' + str(machine[0].sn))
            #plt.scatter(times, num_errors, facecolor= 'b', s = 300) #, label = 'site code 10')
            serial_number = str(machine[0].sn)
            serial_number.strip()
            plt.plot(times,num_errors, colors[num_machines_plotted%len(colors)], linewidth=2.0, label = serial_number)
            num_machines_plotted += 1
        
    
    
    plt.legend(loc = 2)
    plt.xlabel('Date', fontsize = 24)
    plt.ylabel('Number of Errors', fontsize = 24)
    plt.title('Errors throughout Time, per machine at Site Code ' + str(sitecode), fontsize = 30)
    #plt.xlim([0, 100000000])
    #plt.ylim([0,600])
    #plt.show()
    
def main():
    username = raw_input("Please enter your username: ")
    password = raw_input("Please enter your password: ")
    
    all_recs = cyb_records.Errors()
    all_recs.ReadRecords(username = username, password = password)
    print 'Number of total Events', len(all_recs.records)

    #clean_recs = clean_events.CleanEvents(all_recs.records)
    clean_recs_all = list(all_recs.records)
    clean_recs_no_watchdogs = clean_events.remove_watchdogs(list(all_recs.records))
    print 'Number of clean events (without watchdogs): ', len(clean_recs_no_watchdogs)
    
    time_vs_errors_for_one_site_code(clean_recs_all, 11, password = password, username = username)
    time_vs_errors_for_one_site_code(clean_recs_no_watchdogs, 11, password = password, username = username)
    plt.show()
    
if __name__ == '__main__':
    main()
    
