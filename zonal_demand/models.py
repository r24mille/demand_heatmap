from django.db import models

class ZonalDemand(models.Model):
    """
    A timeseries measurement of electricity demand for each transmission zone in Ontario. 
    This model class suffers from a poorly-formatted table structure.
    """
    zonal_demand_id = models.IntegerField(primary_key=True)
    demand_datetime_dst = models.TimeField(auto_now=False, auto_now_add=False)
    demand_datetime_standard = models.TimeField(auto_now=False, auto_now_add=False)
    demand_timezone = models.CharField(max_length=3)
    hour = models.IntegerField()
    total_ontario = models.DecimalField()
    total_zones = models.DecimalField()
    difference = models.DecimalField()
    northwest = models.DecimalField()
    northeast = models.DecimalField()
    ottawa = models.DecimalField()
    east = models.DecimalField()
    toronto = models.DecimalField()
    essa = models.DecimalField()
    bruce = models.DecimalField()
    southwest = models.DecimalField()
    niagara = models.DecimalField()
    west = models.DecimalField()
    
    class Meta:
        db_table = "zonal_demand"
        managed = False