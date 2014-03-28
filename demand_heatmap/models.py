from django.db import models
'''
Created on Mar 28, 2014

@author: Reid Miller
'''

class Meter(models.Model):
    '''
    Meter represents a customer meter record
    '''

        
    MeterID = models.IntegerField(primary_key=True)
    MeterNumber = models.CharField(max_length=30)
    CustomerPremiseNumber = models.IntegerField()
    ConnectDate = models.TimeField(auto_now=False, auto_now_add=False)

    class Meta:
        db_table = "Meters"
        unique_together = ("MeterNumber", "CustomerPremiseNumber", "ConnectDate")