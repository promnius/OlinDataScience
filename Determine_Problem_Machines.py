
# MORE TO DO: Make sure there is a try catch around the attempt to access the database!!

import cyb_records
import clean_events
# NOTE: the function I want from prep should really end up in clean records!!
import checking_install_date_consistency as prep
import datetime
import time
import timeseries_plots
import matplotlib.pyplot as plt

# NEED WAY OF AUTOGRABBING THIS!!
todays_date = 1399235139 
one_week = 604800 # seconds

debugging_lev1 = True # basic code debugging and correcting coding errors. No need to use if code is working.
debugging_lev2 = True # useful and informative information, but not directly pertaining to the output of the script.


"""This program will read in the entire database of errors, sift through them using an elementary cost function,
and determine the machines that it thinks are the most likely to be nearing damage."""
def main():
    print("Program will now attempt to determine the machines with the highest level of risk"
          + " by looking for machines with the largest number of errors in recent history, weighting them based on date.")
    # NEED ERROR CHECKING to see if input is an int.
    num_trouble_machines = raw_input("How many machines would you like to identify?")
    num_trouble_machines = int(num_trouble_machines)
    username = raw_input("Please enter your username: ")
    password = raw_input("Please enter your password: ")

    
    all_recs = cyb_records.Errors()
    all_recs.ReadRecords(username = username, password = password)
    
    # watchdogs are ignored for this analysis because they are deemed unlikely to be the source
    # of a damaged machine. Hopefully, as a greater understanding of the machines and their error
    # codes is accumulated, a more accurate cost function could be implemented that weights each
    # error based on its likelyhood of being dangerous to the health of the machine, or even better
    # yet, a script that allows the user to enter parameters for analyzing 'top risk' machines.
    clean_recs = clean_events.remove_watchdogs(list(all_recs.records))
    if debugging_lev2: print('Number of total Errors in database (excluding watchdogs): ' + str(len(clean_recs)))

    machines = prep.split_up_machine_events(clean_recs)

    risk_levels = []
    for machine in machines:
        risk_levels.append(assess_machine(machine))
    #print(str(risk_levels))
    #print(len(risk_levels))
    risk_levels_sorted = sorted(risk_levels, reverse=True)
    print(risk_levels_sorted)
    print(risk_levels)
    
    # extracting the top problem machines from their error cost functions.
    # NOTE: ERRORS WILL occur if two machines have identical cost functions. maybe solve this by also checking that the machine hasn't already been added?
    trouble_machines = []
    for counter in range(num_trouble_machines):
        machine_index = risk_levels.index(risk_levels_sorted[counter])
        trouble_machines.append(machines[machine_index])
        
        
    timeseries_plots.plot_time_vs_errors_for_list_of_machines(trouble_machines)
    #time_vs_errors_for_one_site_code(clean_recs_all, 11, password = password, username = username)
    #time_vs_errors_for_one_site_code(clean_recs_no_watchdogs, 11, password = password, username = username)
    plt.show()
    
"""This function is the cost analysis function that takes a list of errors all belonging to one machine,
and based on a simple weighting function, returns a numeric assessment of the machine's risk level. the 
current weighting function only considers date- the more recent the error the heavier it counts against the machine."""
def assess_machine(machine):
    machine_sn = machine[0].sn # this function really only uses the sn for debugging purposes.
    debugging_print_timestamp = True # leave as true. Turn of this debugging option with debugging_lev1. This variable
    # just limits the number of print statements.
    num_errors_one_week = 0
    num_errors_two_week = 0
    num_errors_three_week = 0
    num_errors_four_week = 0
    
    for error in machine:
        # convert timestamp into seconds since 1970 epoch, to make it more easily sorted and compared.
        current_timestamp_epoch = int(time.mktime(error.timestamp.timetuple()))
        if debugging_lev1 and debugging_print_timestamp: 
            print("DEBUGGING LEV 1: current timestamp is: " + str(error.timestamp) + '. In seconds since the Epoch, this is: ' + str(current_timestamp_epoch))
            debugging_print_timestamp = False
        error_latency =  todays_date - current_timestamp_epoch
        # finding which errors (if any) have occured in the last four weeks, and sorting them accordingly
        if error_latency < one_week:
            num_errors_one_week += 1
        elif error_latency < 2* one_week:
            num_errors_two_week += 1
        elif error_latency < 3* one_week:
            num_errors_three_week += 1
        elif error_latency < 4* one_week:
            num_errors_four_week += 1
    if debugging_lev1: print("DEBUGGING LEV 1: number of recent errors (one week) for machine " + str(machine_sn) + " is: " + str(num_errors_one_week))
        
    # computing the cost function
    cost = 4*num_errors_one_week + 3*num_errors_two_week + 2*num_errors_three_week + 1*num_errors_four_week   
    if debugging_lev1: 
        print("DEBUGGING LEV 1: Total cost for this machine (arbitrary units): " + str(cost)) 
        print("")
        
    return cost
    
    
if __name__ == '__main__':
    main()
    