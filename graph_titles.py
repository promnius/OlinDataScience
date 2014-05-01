"""
Graph titles
"""

import time, datetime
from time import gmtime, strftime
import cyb_records

def GetDate():
	date = (time.strftime("%Y-%b-%d"))
	return date

def GetSiteName(site_number):
	site_name = ''

	site_codes = {"9": "Office Test Units", \
		"10": "Cybex Medway Showroom", \
		"11": "Planet Fitness Webster Square", \
		"12": "MacColl YMCA", \
		"13": "Holiday Inn Taunton", \
		"14": "Planet Fitness Franklin, MA", \
		"15": "Gold's Gym Natick", \
		"16": "Planet Fitness Shrewsbury", \
		"17": "Cybex Customer Service", \
		"18": "Southbridge YMCA"}

	if site_number in site_codes.keys():
		site_name = site_codes.get(site_number)

	return site_name

def main():
	today = GetDate()
	site_title = GetSiteName('11')

	graph_title = "[" + today + "] " + site_title + " cardio equipment histogram of machine events"

	print graph_title

if __name__ == '__main__':
	main()