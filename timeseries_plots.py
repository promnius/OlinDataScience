"""
Errors and distance traveled
"""

import cyb_records_3
import thinkstats2
import clean_events
import time, datetime
import checking_install_date_consistency as prep
import matplotlib.pyplot as plt


def main():
    colors = ['b', 'g', 'r', 'k', 'm']
    
    all_recs = cyb_records_3.Errors()
    all_recs.ReadRecords()
    print 'Number of total Events', len(all_recs.records)

    #clean_recs = clean_events.CleanEvents(all_recs.records)
    clean_recs = all_recs.records
    print 'Number of clean events', len(clean_recs)
    
    collecting_site_codes = cyb_records_3.Machines()
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

    machines = prep.split_up_machine_events(clean_recs)
    #real_machines = ['G0608625TX022N-8114NZJ                            ', 'G0724770AT052N                                    ']
    sitecode = 11 # options are 10-14. 11 is the only one with good data. see database for more details
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
    plt.show()
    
    
    #errors = CorrErrDist(clean_recs)
    #print 'Number of dict entries', len(errors)

    #for key in errors.keys():
    #     print "Error id =", key, "Correlation =", thinkstats2.SerialCorr(errors.get(key)), "List length =", len(errors.get(key))

if __name__ == '__main__':
    main()