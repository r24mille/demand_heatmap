""""
Created on May 28, 2014

@author: r24mille
"""
from django.db import connections

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

if __name__ == '__main__':
    windsor_location_id = 13
    pre_tou_summer_start = '2011-05-01 00:00:00'
    pre_tou_summer_end = '2011-10-31 23:59:59'
    pre_tou_summer_dict = partition_by_temperature(windsor_location_id, 
                                                   pre_tou_summer_start, 
                                                   pre_tou_summer_end)
    print(pre_tou_summer_dict)
    
    post_tou_summer_start = '2012-05-01 00:00:00'
    post_tou_summer_end = '2012-10-31 23:59:59'
    post_tou_summer_dict = partition_by_temperature(windsor_location_id, 
                                                   post_tou_summer_start, 
                                                   post_tou_summer_end)