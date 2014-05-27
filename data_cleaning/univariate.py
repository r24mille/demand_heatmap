#!/usr/bin/env python
import decimal
import math
import os
from scipy import stats

from django.db import connections, transaction
from numpy import arange
import numpy
import pylab


def create_histogram(a, trim_p, bin_size, p_title, p_ylabel, p_xlabel, 
                     file_prefix, dec_prec=0, trim_type="both"):
    """Interacts with pylab to draw and save histogram plot.
    
    Arguments:
    a -- array_like list of values to plot
    trim_p -- Percentile (range 0 to 1) of values to trim (float)
    bin_size -- Size of histogram's value bins (float)
    p_title -- Title of plot
    p_ylabel -- ylabel of plot
    p_xlabel -- xlabel of plot
    file_prefix -- Filename prefix
    dec_prec -- (Optional) Decimal precision of bins. Defaults to 0. (int)
    trim_type -- (Optional) Controls the tail of distribution that percentile 
                 trim_p is applied. Values include "both", "left", and "right".
                 Defaults to "both".
    """
    a.sort()
    sample_size = len(a)
    print("a length pre-trim_p", len(a))
    if trim_type == "left" or trim_type == "right":
        a = stats.trim1(a, trim_p, trim_type)
    else:
        a = stats.trimboth(a, trim_p)
    print("a length post-trim_p", len(a))
    bin_min = math.floor(min(a)) # TODO Round down to dec_prec instead
    bin_max = round(max(a), dec_prec)
    print("bin size=" + str(bin_size) + 
          ", bin min=" + str(bin_min) + 
          ", bin max=" + str(bin_max))
    # Create histogram of values
    n, bins, patches = pylab.hist(a, 
                                  bins=pylab.frange(bin_min, 
                                                    bin_max, 
                                                    bin_size), 
                                  normed=False, 
                                  histtype="stepfilled")
    pylab.setp(patches, "facecolor", "g", "alpha", 0.75)
    pylab.title(p_title)
    pylab.xlabel(p_xlabel)
    pylab.ylabel(p_ylabel)
    
    if trim_p > 0:
        pylab.savefig(file_prefix + "_trimmed.png")
    else:
        pylab.savefig(file_prefix + ".png")
    pylab.show()


def hourly_sm_reading_histogram():
    """Creates a histogram of smart meter readings to identify their 
    distribution and find outliers.
    """
    cursor = connections["ldc"].cursor()
    cursor.execute("select smr.Reading " 
                   "from essex_annotated.SmartMeterReadings smr " 
                   "inner join Meters m on m.MeterID = smr.MeterID " 
                   "   and m.`Phase` = 1 " 
                   "left join meter_data_quality_flag mdqf " 
                   "   on smr.MeterID = mdqf.MeterID " 
                   "   and mdqf.applicability_start_date <= '2011-05-01' " 
                   "   and mdqf.applicability_end_date >= '2012-10-31' " 
                   "where smr.MeterID >= 20000 and smr.MeterID < 20100 " 
                   "and mdqf.MeterID is null " 
                   "and smr.ReadDate >= '2011-05-01' " 
                   "and smr.ReadDate <= '2011-10-31'")
    # Create a list of hourly reading values
    readings = [row[0] for row in cursor.fetchall()]
    
    # Create histogram
    sample_size = len(readings)
    trim_p = 0.0005
    p_title = "Histogram of Hourly Readings \n" \
                "(Summer 2011, sample: " + str(sample_size) + " readings, " \
                "right trim:" + str(trim_p * 100.0) + "%)"
    p_xlabel = "Hourly Reading (kW)"
    p_ylabel = "Occurrences"
    create_histogram(readings, trim_p, 0.1, p_title, p_ylabel, p_xlabel, 
                     "hourly_sm_reading_histogram_summer2011", 1, "right")
    

def reading_count_histogram():
    """Gets the number of readings in a time range grouped by MeterID"""
    cursor = connections["ldc"].cursor()
    cursor.execute("select count(smr.read_datetime) "
                   "from essex_annotated.SmartMeterReadings smr " 
                   "inner join Meters m "
                   "  on m.MeterID = smr.MeterID and m.`Phase` = 1 "
                   "left join meter_data_quality_flag mdqf "
                   "   on smr.MeterID = mdqf.MeterID " 
                   "   and mdqf.applicability_start_date <= '2011-05-01' "
                   "   and mdqf.applicability_end_date >= '2012-10-31' "
                   "where smr.MeterID >= 20000 and smr.MeterID < 30000 "
                   "and mdqf.MeterID is null " 
                   "and smr.ReadDate >= '2011-05-01' " 
                   "and smr.ReadDate <= '2011-10-31' "
                   "group by smr.MeterID")
    # Create a list of observation counts
    reading_counts = [row[0] for row in cursor.fetchall()]
    
    # Create histogram
    sample_size = len(reading_counts)
    trim_p = 0.001
    p_title = "Number of Readings Histogram \n" \
                "(Summer 2011, sample: " + str(sample_size) + " meters, " \
                "left trim:" + str(trim_p * 100.0) + "%)"
    p_xlabel = "Number of Readings During Timeframe"
    p_ylabel = "Number of Meters"
    create_histogram(reading_counts, trim_p, 1, p_title, p_ylabel, p_xlabel, 
                     "sm_reading_count_histogram_summer2011", 0, "left")
    
    
def sm_reading_exception_count_histogram():
    """Counts the number of exceptions per MeterNumber and plots a 
    histogram.
    """
    cursor = connections["ldc"].cursor()
    cursor.execute("select count(smre.reading_datetime_standard) "
                   "from Meters m "
                   "left join SmartMeterReadingsExceptions smre "
                   "   on smre.MeterNumber = m.MeterNumber "
                   "group by m.MeterNumber")
    # Create a list of observation counts
    exception_counts = [row[0] for row in cursor.fetchall()]
    
    # Create histogram
    sample_size = len(exception_counts)
    bin_size = 10.0
    trim_p = 0
    p_title = "Number of Exceptions Histogram \n" \
                "(sample: " + str(sample_size) + " meters, " \
                "bin size:" + str(bin_size) + ", " \
                "trim: " + str(trim_p * 100.0) + "%)"
    p_xlabel = "Number of Exception per Meter"
    p_ylabel = "Occurrences"
    create_histogram(exception_counts, trim_p, bin_size, p_title, p_ylabel, p_xlabel, 
                     "sm_exception_count_histogram", 0, "right")


def main():
    """Main method for running univariate outlier analysis functions."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ldc_analysis.settings")
    # hourly_sm_reading_histogram()
    # reading_count_histogram()
    sm_reading_exception_count_histogram()


if __name__ == '__main__':
    main()