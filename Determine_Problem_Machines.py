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
from collections import OrderedDict
import cyb_graphs

# Time in seconds
one_day = 86400
one_week = 604800
sixty_days = 5184000
todays_date = int((time.time()/one_day)+1)*one_day
sixty_days_ago = todays_date - sixty_days
print time.strftime("%Y-%b-%d")

debugging_lev1 = False # basic code debugging and correcting coding errors. No need to use if code is working.
debugging_lev2 = True # useful and informative information, but not directly pertaining to the output of the script.
    
def AssessRisk(machine):
    machine_sn = machine[0].sn
    debugging_print_timestamp = True
    events_week_1 = 0
    events_week_2 = 0
    events_week_3 = 0
    events_week_4 = 0
    
    for error in machine:
        current_timestamp_epoch = int(time.mktime(error.timestamp.timetuple()))

        if current_timestamp_epoch < sixty_days_ago or current_timestamp_epoch > todays_date:
            continue

        # if debugging_lev1 and debugging_print_timestamp: 
        #     print("Event timestamp: " + str(error.timestamp))
        #     debugging_print_timestamp = False

        # Find events from most recent weeks
        error_latency =  todays_date - current_timestamp_epoch
        if error_latency < one_week:
            events_week_1 += 1
        elif error_latency < (2*one_week) and error_latency > (1*one_week):
            events_week_2 += 1
        elif error_latency < (3*one_week) and error_latency > (2*one_week):
            events_week_3 += 1
        elif error_latency > (3*one_week):
            events_week_4 += 1

    # Compute cost
    cost = 4*events_week_1 + 3*events_week_2 + 2*events_week_3 + 1*events_week_4   
    if debugging_lev1: 
        print machine_sn[:-25], "# recent events: ", events_week_1, events_week_2, events_week_3, events_week_4
        print "Cost: ", cost
        print ""
        
    return cost

def main():
    # Clean events
    all_recs = cyb_records.Errors()
    all_recs.ReadRecords(username = "kbrookshier", password = "Cybex321")
    clean_recs = clean_events.remove_watchdogs(all_recs.records)
    print('Number of total events in database (excluding watchdogs): ', (len(clean_recs)))

    # Get machine list
    machines = prep.split_up_machine_events(clean_recs)

    # Risk levels
    risk_levels = {}
    for machine in machines:
        risk = AssessRisk(machine)
        risk_levels[machine[0]] = risk

    risk_levels_sorted = OrderedDict(sorted(risk_levels.items(), key=lambda t: t[1], reverse = True))
    
    print '{:25}  {:10}  {:>5}  {:30}'.format('Machine id', 'Product #', 'Risk', 'Facility')
    print "------------------------------------------------------"
    for key in risk_levels_sorted.keys():
        val = risk_levels_sorted.get(key)
        if val > 10:
            output = '{:25}  {:10}  {:>5}  {:30}'.format(key.sn.strip(), key.product_number, val, key.name)
            print output

    # Graphs
    top_risk_machines = []
    keys = risk_levels_sorted.keys()
    for i in range(3):
        top_risk_machines.append(keys[i].sn)

    cyb_graphs.PlotPMF(clean_recs, top_risk_machines)

    
if __name__ == '__main__':
    main()