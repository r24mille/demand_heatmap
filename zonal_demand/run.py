#!/usr/bin/env python
import os

import matplotlib
import numpy

import matplotlib.pyplot as plt
from zonal_demand.models import ZonalDemand


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ldc_analysis.settings")
    
    # Get timeseries of TransformerLoad associated with a Transformer
    demands = ZonalDemand.objects.using('zonal').all()

    # Find the length of the results to know first and last index, then get the number of days
    num_loads = len(demands)
    start_date = demands[0].demand_datetime_dst
    end_date = demands[num_loads - 1].demand_datetime_dst
    num_days = (end_date - start_date).days

    # Create an n x 24 matrix to hold each hour's values and zeros for hours without value
    load_heatmap = numpy.zeros(((num_days + 1), 24))
    
    # Loop over all TransformerLoad rows returned and populate them into the proper array slot
    for zonalDemand in demands:
        d = (zonalDemand.demand_datetime_dst - start_date).days
        load_heatmap[d][zonalDemand.hour - 1] = zonalDemand.total_ontario
    
    # Plot the timeseries matrix as a heatmap
    start_datenum = matplotlib.dates.date2num(start_date)
    end_datenum = matplotlib.dates.date2num(end_date)
    fig = plt.figure()
    ax = plt.subplot()
    # plt.subplots_adjust(left=0.2, bottom=None, right=1, top=None, wspace=None, hspace=None)
    im = ax.imshow(load_heatmap, interpolation='none', aspect='auto', extent=(0, 24, start_datenum, end_datenum), origin='lower', vmin=9000, vmax=27000)
    ax.yaxis_date()
    ax.set_title("Ontario Demand")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Year")
    ax.xaxis.set_ticks(range(0, 24, 2))
    cb = fig.colorbar(im)
    cb.set_label("Kilowatt-hours (kWh)")
    # plt.savefig("./figures/ontario.png", dpi=100)
    # plt.close()
    plt.show()
