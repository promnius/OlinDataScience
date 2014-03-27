"""
Time series analysis with stats and errors
"""

import cyb_records
import clean_events
import thinkstats2

def AutoCorr(xs, lag):
    return Corr(xs[:-lag], xs[lag:])

def main():

if __name__ == '__main__':
    main()