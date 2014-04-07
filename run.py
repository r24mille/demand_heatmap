#!/usr/bin/env python
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demand_heatmap.settings")
    
    # Get timeseries of TransformerLoad associated with a Transformer
    from demand_heatmap.models import Meter, Transformer, TransformerLoad
    from django.db.models import Q
    transformers = Transformer.objects.filter(Phases='3', Enabled=True)[:5]
    
    fignum = 1
    print(len(transformers))
    for transformer in transformers:
        loads = transformer.transformerload_set.all()
        
        # Transformer must have TransformerLoad items
        if len(loads) > 0:
            # Find the length of the results to know first and last index, then get the number of days
            num_loads = len(loads)
            start_date = loads[0].ReadDate
            end_date = loads[num_loads - 1].ReadDate
            num_days = (end_date - start_date).days
        
            # Create an n x 24 matrix to hold each hour's values and zeros for hours without value
            load_heatmap = np.zeros(((num_days + 1), 24))
            
            # Loop over all TransformerLoad rows returned and populate them into the proper array slot
            for load in loads:
                d = (load.ReadDate - start_date).days
                load_heatmap[d][load.Interval] = load.LoadMW
            print(load_heatmap)
            
            # Plot the timeseries matrix as a heatmap
            start_datenum = matplotlib.dates.date2num(start_date)
            end_datenum = matplotlib.dates.date2num(end_date)
            fig = plt.figure(fignum)
            ax = plt.subplot()
            im = ax.imshow(load_heatmap, interpolation='none', aspect='auto', extent=(0, 24, start_datenum, end_datenum), origin='lower')
            ax.yaxis_date()
            ax.set_title("Transformer ID: " + load.Transformer.TransformerID)
            ax.xaxis.set_ticks(range(0, 24, 1))
            fig.colorbar(im)
            fignum = fignum + 1
    
    plt.show()
