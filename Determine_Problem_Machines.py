"""
Determine the cardio machines which are most likely in need of service
"""

# MORE TO DO: Make sure there is a try catch around the attempt to access the database!!
import cyb_records
import clean_events
import checking_install_date_consistency as prep    # NOTE: the function I want from prep should really end up in clean records!!
import datetime
import time
import timeseries_plots
import matplotlib.pyplot as plt

# Time in seconds
one_day = 86400
one_week = 604800
sixty_days = 5184000
todays_date = int((time.time()/one_day)+1)*one_day
sixty_days_ago = todays_date - sixty_days
print todays_date, time.strftime("%Y-%b-%d")

debugging_lev1 = True # basic code debugging and correcting coding errors. No need to use if code is working.
debugging_lev2 = True # useful and informative information, but not directly pertaining to the output of the script.
    
def assess_machine(machine):
    machine_sn = machine[0].sn # this function really only uses the sn for debugging purposes.
    debugging_print_timestamp = True
    events_week_1 = 0
    events_week_2 = 0
    events_week_3 = 0
    events_week_4 = 0
    
    for error in machine:
        current_timestamp_epoch = int(time.mktime(error.timestamp.timetuple()))

        if current_timestamp_epoch < sixty_days_ago or current_timestamp_epoch > todays_date:
            continue

        if debugging_lev1 and debugging_print_timestamp: 
            print("Event timestamp: " + str(error.timestamp))
            debugging_print_timestamp = False

        # Find events from most recent weeks
        error_latency =  todays_date - current_timestamp_epoch
        if error_latency < one_week:
            events_week_1 += 1
        elif error_latency < (2*one_week) and error_latency > (1*one_week):
            events_week_2 += 1
        elif error_latency < (3*one_week) and error_latency > (2*one_week):
            events_week_3 += 1
        elif error_latency < (4*one_week) and error_latency > (3*one_week):
            events_week_4 += 1

    # Compute cost
    cost = 4*events_week_1 + 3*events_week_2 + 2*events_week_3 + 1*events_week_4   
    if debugging_lev1: 
        print machine_sn[:-20], "# recent events: ", events_week_1, events_week_2, events_week_3, events_week_4
        print "Cost: ", cost
        print ""
        
    return cost

def main():
    # User input
    num_trouble_machines = raw_input("How many machines would you like to identify? ")
    num_trouble_machines = int(num_trouble_machines)
    username = raw_input("Please enter your username: ")
    password = raw_input("Please enter your password: ")
    
    # Clean events
    all_recs = cyb_records.Errors()
    all_recs.ReadRecords(username = username, password = password)
    clean_recs = clean_events.remove_watchdogs(list(all_recs.records))
    print('Number of total events in database (excluding watchdogs): ', (len(clean_recs)))

    machines = prep.split_up_machine_events(clean_recs)

    # Calculate risk level
    risk_levels = []
    for machine in machines:
        risk_levels.append(assess_machine(machine))
    risk_levels_sorted = sorted(risk_levels, reverse=True)
    print(risk_levels_sorted)
    
    # Identify machines in need of service
    trouble_machines = []
    for counter in range(num_trouble_machines):
        machine_index = risk_levels.index(risk_levels_sorted[counter])
        trouble_machines.append(machines[machine_index])
        
    timeseries_plots.plot_time_vs_errors_for_list_of_machines(trouble_machines)
    #time_vs_errors_for_one_site_code(clean_recs_all, 11, password = password, username = username)
    #time_vs_errors_for_one_site_code(clean_recs_no_watchdogs, 11, password = password, username = username)
    plt.show()
    
    
if __name__ == '__main__':
    main()