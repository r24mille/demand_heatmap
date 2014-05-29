""""
Created on May 28, 2014

@author: r24mille
"""
from django.db import connections
from matplotlib import pyplot
import numpy


def partition_by_temperature(location_id, start_datetime, end_datetime):
    """
    First analysis method partitions demand measurements into 2D arrays by 
    temperature x hour, values are average aggregate demand. Returns a 
    dictionary using temperature as a key. The value is a 2D list hour x 
    rounded temperature.
    
    Arguments:
    location_id -- The weathertables.location to use for hourly temperature 
                   measurements.
    start_datetime -- A string in MySQL DATETIME format indicating the 
                      timeseries starting point (inclusive) of aggregate 
                      readings.
    end_datetime -- A string in MySQL DATETIME format indicating the timeseries
                    ending point (inclusive) of aggregate readings.
    """
    cursor = connections["ldc"].cursor()
    cursor.execute("select hour(arr.aggregate_reading_datetime_standard) as hour_of_day, " + 
                    "(arr.aggregate_reading / arr.number_of_meters) as avg_reading, " + 
                    "round(wu.temp_metric) as rounded_temp " + 
                    "from r24mille_aggregate_res_readings arr " + 
                    "left join weathertables.wunderground_observation wu " + 
                    "    on wu.observation_datetime_standard = arr.aggregate_reading_datetime_standard " + 
                    "    and wu.location_id = " + str(location_id) + " " + 
                    "where arr.aggregate_reading_datetime_standard >= '" + str(start_datetime) + "' " + 
                    "and arr.aggregate_reading_datetime_standard <= '" + str(end_datetime) + "' " + 
                    "and dayofweek(arr.aggregate_reading_datetime_standard) > 1 " + 
                    "and dayofweek(arr.aggregate_reading_datetime_standard) < 7 " + 
                    "order by arr.aggregate_reading_datetime_standard asc")
    
    # Create a 2D array of aggregate readings partitioned by temperature and 
    # hour-of-day.
    temperature_dict = {}
    for row in cursor.fetchall():
        hour_of_day = int(row[0])
        avg_reading = row[1]
        rounded_temp = int(row[2])
        
        if rounded_temp not in temperature_dict:
            temperature_dict[rounded_temp] = [0] * 24
            
        if temperature_dict[rounded_temp][hour_of_day]: 
            temperature_dict[rounded_temp][hour_of_day].append(avg_reading)
        else:
            temperature_dict[rounded_temp][hour_of_day] = [avg_reading]
    return temperature_dict

def plot_tou_dict_comparison(pre_tou_dict, post_tou_dict):
    """
    Creates summary comparison plots of a pre-TOU dictionary and a post-TOU 
    dictionary. The y-axis value is the mean reading for a given 
    (temperature, hour-of-day) tuple.
    
    Arguments:
    pre_tou_dict -- A dictionary of pre-TOU average aggregate demand for a 
                    region using temperature as key. The value is a 2D list 
                    of hours x demand.
    post_tou_dict -- A dictionary of post-TOU average aggregate demand for a 
                     region using temperature as key. The value is a 2D list 
                     of hours x demand.
    """
    hours = 24
    temps = list(pre_tou_dict.keys()) + list(post_tou_dict.keys())
    days = list(pre_tou_dict.values()) + list(post_tou_dict.values())
    readings = []
    # Iterate through all readings to find the max over all 
    for d in days:
        for h in range(hours):
            if isinstance(d[h], list):
                for i in d[h]:
                    readings.append(i)
            else:
                readings.append(d[h])
    max_reading = max(readings)
    
    for t in range(min(temps), max(temps)):
        
        pre_means = [0] * (hours)
        pre_stderrs = [0] * (hours)
        post_means = [0] * (hours)
        post_stderrs = [0] * (hours)
        for h in range(hours):
            if t in pre_tou_dict:
                pre_means[h] = numpy.mean(pre_tou_dict[t][h])
                pre_stderrs[h] = numpy.std(pre_tou_dict[t][h])
            if t in post_tou_dict:
                post_means[h] = numpy.mean(post_tou_dict[t][h])
                post_stderrs[h] = numpy.std(post_tou_dict[t][h])
        
        ind = numpy.arange(hours)  # the x locations for the groups
        width = 0.3  # the width of the bars
        
        fig = pyplot.figure(t)
        ax = pyplot.subplot()
        rects1 = ax.bar(ind, pre_means, width, yerr=pre_stderrs,
                        ecolor="black", color='#3C3CFF', edgecolor='#3C3CFF')  # blue
        rects2 = ax.bar(ind + width, post_means, width, yerr=post_stderrs,
                        ecolor="black", color='#580A58', edgecolor='#580A58')  # purple
        
        # Time-of-Use priods
        ax.fill_between(x=[0, (7 + width)], y1=max_reading,
                        facecolor='#98C13D', edgecolor='#98C13D',
                        alpha=0.5)  # off-peak
        ax.fill_between(x=[(7 + width), (11 + width)], y1=max_reading,
                        facecolor='#FAC80F', edgecolor='#FAC80F',
                        alpha=0.5)  # mid-peak
        ax.fill_between(x=[(11 + width), (17 + width)], y1=max_reading,
                        facecolor='#C95927', edgecolor='#C95927',
                        alpha=0.5)  # on-peak
        ax.fill_between(x=[(17 + width), (19 + width)], y1=max_reading,
                        facecolor='#FAC80F', edgecolor='#FAC80F',
                        alpha=0.5)  # mid-peak
        ax.fill_between(x=[(19 + width), (24)], y1=max_reading,
                        facecolor='#98C13D', edgecolor='#98C13D',
                        alpha=0.5)  # off-peak
        
        
        # add some
        ax.set_ylabel("Mean Household Reading (kWh)")
        ax.set_ylim(0, max_reading)
        ax.set_title("Mean Household Reading by Hour for Outdoor " + 
                     "Temperature " + str(t) + " Celsius \nBefore/After " + 
                     "Time-of-Use Billing (May - Oct)")
        ax.set_xticks(ind + width)
        ax.set_xticklabels(list(range(hours)))
        ax.set_xlabel("Hour of Day")
        ax.set_xlim(0, hours)
        
        ax.legend((rects1[0], rects2[0]),
                   ('Pre-TOU', 'Post-TOU'),
                   loc='upper right')
        
        def autolabel(rects):
            # attach some text labels
            for rect in rects:
                height = rect.get_height()
                if height > 0:
                    ax.text(rect.get_x() + rect.get_width() / 2.,
                            1.05 * height,
                            round(rect.get_height(), 2),
                            ha='center',
                            va='bottom')
        
        # autolabel(rects1)
        # autolabel(rects2)
        pyplot.savefig("./figures/summer_" + str(t).zfill(2) + ".png")
        pyplot.close(t)
            

if __name__ == '__main__':
    windsor_location_id = 13
    pre_tou_summer_start = '2011-05-01 00:00:00'
    pre_tou_summer_end = '2011-10-31 23:59:59'
    pre_tou_summer_dict = partition_by_temperature(windsor_location_id,
                                                   pre_tou_summer_start,
                                                   pre_tou_summer_end)
    # print("pre_tou", pre_tou_summer_dict)
    
    post_tou_summer_start = '2012-05-01 00:00:00'
    post_tou_summer_end = '2012-10-31 23:59:59'
    post_tou_summer_dict = partition_by_temperature(windsor_location_id,
                                                   post_tou_summer_start,
                                                   post_tou_summer_end)
    
    # print("post_tou", post_tou_summer_dict)
    
    plot_tou_dict_comparison(pre_tou_summer_dict, post_tou_summer_dict)
