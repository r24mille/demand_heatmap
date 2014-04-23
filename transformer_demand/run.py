#!/usr/bin/env python
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ldc_analysis.settings")
    
    # Get timeseries of TransformerLoad associated with a Transformer
    from transformer_demand.models import Transformer
    phaseStr = "1"
    areaStr = "A1-TEC"
    transformers = Transformer.objects.using('ldc').filter(Phases=phaseStr, Enabled=True, AreaTown=areaStr)
    
    fignum = 1
    for transformer in transformers:
        demands = transformer.transformerload_set.all()
        
        # Transformer must have TransformerLoad items
        if len(demands) > 0:
            # Find the length of the results to know first and last index, then get the number of days
            num_loads = len(demands)
            start_date = demands[0].ReadDate
            end_date = demands[num_loads - 1].ReadDate
            num_days = (end_date - start_date).days
        
            # Create an n x 24 matrix to hold each hour's values and zeros for hours without value
            load_heatmap = np.zeros(((num_days + 1), 24))
            
            # Loop over all TransformerLoad rows returned and populate them into the proper array slot
            for zonalDemand in demands:
                d = (zonalDemand.ReadDate - start_date).days
                load_heatmap[d][zonalDemand.Interval] = zonalDemand.LoadMW
            
            # Plot the timeseries matrix as a heatmap
            start_datenum = matplotlib.dates.date2num(start_date)
            end_datenum = matplotlib.dates.date2num(end_date)
            fig = plt.figure(fignum)
            ax = plt.subplot()
            plt.subplots_adjust(left=0.2, bottom=None, right=1, top=None,
                wspace=None, hspace=None)
            im = ax.imshow(load_heatmap, interpolation='none', aspect='auto', extent=(0, 24, start_datenum, end_datenum), origin='lower')
            ax.yaxis_date()
            ax.set_title("Transformer ID: " + transformer.TransformerID)
            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Day of Year")
            ax.xaxis.set_ticks(range(0, 24, 2))
            cb = fig.colorbar(im)
            cb.set_label("Kilowatt-hours (kWh)")
            plt.savefig("./figures/" + phaseStr + "-phase/" + areaStr + "/" + transformer.TransformerID + ".png", dpi=100)
            plt.close(fignum)
            
            # Increase fignum
            fignum = fignum + 1
    
    plt.show()
