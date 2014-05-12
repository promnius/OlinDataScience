"""
Determine the cardio machines which are most likely in need of service
"""
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
eight_weeks = 4838400
todays_date = int((time.time()/one_day)+1)*one_day
eight_weeks_ago = todays_date - eight_weeks
print time.strftime("%Y-%b-%d")
    
def AssessRisk(machine):
    machine_sn = machine[0].sn
    events_week_1 = 0
    events_week_2 = 0
    events_week_3 = 0
    events_week_4 = 0
    
    for error in machine:
        current_timestamp_epoch = int(time.mktime(error.timestamp.timetuple()))

        if current_timestamp_epoch < eight_weeks_ago or current_timestamp_epoch > todays_date:
            continue

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
        
    return cost

def main():
    # Clean events
    all_recs = cyb_records.Errors()
    num_trouble_machines = raw_input("How many top risk machines would you like to plot? ")
    username = raw_input("Please enter your username: ")
    password = raw_input("Please enter your password: ")
    all_recs.ReadRecords(username = username, password = password)
    clean_recs = clean_events.remove_watchdogs(all_recs.records)

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
    for i in range(int(num_trouble_machines)):
        top_risk_machines.append(keys[i].sn)

    cyb_graphs.PlotPMF(clean_recs, top_risk_machines)

if __name__ == '__main__':
    main()