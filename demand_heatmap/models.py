from django.db import models
'''
Created on Mar 28, 2014

@author: Reid Miller
'''


class Transformer(models.Model):
    '''
    Transformer represents a distribution transformer
    '''
    
    
    TransformerID = models.CharField(max_length=20, primary_key=True)
    Type = models.CharField(max_length=100)
    KVA = models.IntegerField()
    Phasing = models.CharField(max_length=6)
    CircuitNumber = models.CharField(max_length=16)
    PrimaryVoltage = models.CharField(max_length=16)
    SecondaryVoltage = models.CharField(max_length=20)
    InstallationYear = models.IntegerField()
    DWGNumber = models.CharField(max_length=30)
    Phases = models.CharField(max_length=24)
    Serial1 = models.CharField(max_length=100)
    Serial2 = models.CharField(max_length=100)
    Serial3 = models.CharField(max_length=100)
    Enabled = models.SmallIntegerField()
    Quantity = models.SmallIntegerField()
    Angle = models.DecimalField()
    Status = models.CharField(max_length=100)
    Owner = models.CharField(max_length=100)
    Connect_Date = models.TimeField(auto_now=False, auto_now_add=False)
    Disconnect_Date = models.TimeField(auto_now=False, auto_now_add=False)
    
    class Meta:
        db_table = "Transformers"
        

class Meter(models.Model):
    '''
    Meter represents a customer meter record
    '''

        
    MeterID = models.IntegerField(primary_key=True)
    MeterNumber = models.CharField(max_length=30)
    CustomerPremiseNumber = models.IntegerField()
    ConnectDate = models.TimeField(auto_now=False, auto_now_add=False)
    Transformer = models.ForeignKey(Transformer, db_column="TransformerID")

    class Meta:
        db_table = "Meters"
        unique_together = ("MeterNumber", "CustomerPremiseNumber", "ConnectDate")
        