#!/usr/bin/env python
import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demand_heatmap.settings")
    from demand_heatmap.models import Meter, Transformer
    met = Meter.objects.get(MeterID=38838)
    print(met.Transformer.TransformerID)