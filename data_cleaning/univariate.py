#!/usr/bin/env python
import decimal
import math
import os
from scipy import stats

from django.db import connections, transaction
from numpy import arange
import numpy
import pylab


def hourly_sm_reading_histogram():
    """Creates a histogram of smart meter readings to identify their 
    distribution and find outliers.
    """
    cursor = connections["ldc"].cursor()
    cursor.execute("select smr.Reading " 
                   "from essex_annotated.SmartMeterReadings smr " 
                   "inner join Meters m on m.MeterID = smr.MeterID " 
                   "  and m.`Phase` = 1 " 
                   "left join meter_data_quality_flag mdqf " 
                   "  on smr.MeterID = mdqf.MeterID " 
                   "  and mdqf.applicability_start_date <= '2011-05-01' " 
                   "  and mdqf.applicability_end_date >= '2012-10-31' " 
                   "where smr.MeterID >= 20000 and smr.MeterID < 21000 " 
                   "and mdqf.MeterID is null " 
                   "and smr.ReadDate >= '2011-05-01' " 
                   "and smr.ReadDate <= '2011-10-31'")
    # Create a list of hourly reading values
    readings = [row[0] for row in cursor.fetchall()]
    readings.sort()
    trim = 0.0005
    sample_size = len(readings)
    print("readings length pre-trim", len(readings))
    readings = stats.trimboth(readings, proportiontocut=trim)
    print("readings length post-trim", len(readings))
    bin_sz = 0.1
    bin_min = 0.0
    bin_max = round(max(readings), 1)
    print("bin size=" + str(bin_sz) + 
          ", bin min=" + str(bin_min) + 
          ", bin max=" + str(bin_max))
    # Create histogram of values
    n, bins, patches = pylab.hist(readings, 
                                  bins=pylab.frange(bin_min, bin_max, bin_sz), 
                                  normed=False, 
                                  histtype="stepfilled")
    pylab.setp(patches, "facecolor", "g", "alpha", 0.75)
    pylab.title("Histogram of Hourly Readings \n" 
                "(Summer 2011, sample: " + str(sample_size) + " readings, "
                "trim:" + str(trim * 100.0) + "%)")
    pylab.xlabel("Hourly Reading (kW)")
    pylab.ylabel("Occurrences")
    
    if trim > 0:
        pylab.savefig("hourly_sm_reading_histogram_summer2011_trimmed.png")
    else:
        pylab.savefig("hourly_sm_reading_histogram_summer2011.png")
    #pylab.show()
    

def reading_count_histogram():
    """Gets the number of readings in a time range grouped by MeterID"""
    cursor = connections["ldc"].cursor()
    cursor.execute("select count(smr.read_datetime) "
                   "from essex_annotated.SmartMeterReadings smr " 
                   "inner join Meters m "
                   "  on m.MeterID = smr.MeterID and m.`Phase` = 1 "
                   "left join meter_data_quality_flag mdqf "
                   "  on smr.MeterID = mdqf.MeterID " 
                   "  and mdqf.applicability_start_date <= '2011-05-01' "
                   "  and mdqf.applicability_end_date >= '2012-10-31' "
                   "where smr.MeterID >= 20000 and smr.MeterID < 30000 "
                   "and mdqf.MeterID is null " 
                   "and smr.ReadDate >= '2011-05-01' " 
                   "and smr.ReadDate <= '2011-10-31' "
                   "group by smr.MeterID")
    # Create a list of observation counts
    reading_counts = [row[0] for row in cursor.fetchall()]
    reading_counts.sort()
    trim = 0
    sample_size = len(reading_counts)
    print("readings length pre-trim", len(reading_counts))
    readings = stats.trimboth(reading_counts, proportiontocut=trim)
    print("readings length post-trim", len(readings))
    bin_sz = 1
    bin_min = min(readings)
    bin_max = max(readings)
    print("bin size=" + str(bin_sz) + 
          ", bin min=" + str(bin_min) + 
          ", bin max=" + str(bin_max))
    # Create histogram of values
    n, bins, patches = pylab.hist(readings, 
                                  bins=range(bin_min, bin_max, bin_sz), 
                                  normed=False, 
                                  histtype="stepfilled")
    pylab.setp(patches, "facecolor", "g", "alpha", 0.75)
    pylab.title("Number of Readings Histogram \n" 
                "(Summer 2011, sample: " + str(sample_size) + " meters, "
                "trim:" + str(trim * 100.0) + "%)")
    pylab.xlabel("Number of Readings During Timeframe")
    pylab.ylabel("Number of Meters")
    pylab.savefig("sm_reading_count_histogram_summer2011.png")
    pylab.tick_params(axis='both', )
    pylab.show()

def main():
    """Main method for running univariate outlier analysis functions."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ldc_analysis.settings")
    # hourly_sm_reading_histogram()
    reading_count_histogram()

if __name__ == '__main__':
    main()