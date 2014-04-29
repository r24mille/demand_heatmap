from django.db import models


class Feeder(models.Model):
    """Represents shared electricity feeder lines."""
    FeederID = models.CharField(max_length=20, 
                                primary_key=True, 
                                db_column="Feeder")
    ParentFeeder = models.ForeignKey("self")
    MeterType = models.CharField(max_length=2)
    
    class Meta:
        db_table = "FeederMapping"
        managed = False


class PropertyType(models.Model):
    """Classifies properties (eg. residential, commercial, industrial)"""
    PropertyTypeID = models.IntegerField(primary_key=True, 
                                         db_column="property_type_id")
    property_type_desc = models.CharField(max_length=45)
    
    class Meta:
        db_table = "property_type"
        managed = False


class Transformer(models.Model):
    """Represents a distribution transformer."""
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
    Enabled = models.BooleanField()
    Quantity = models.SmallIntegerField()
    Angle = models.DecimalField()
    AreaTown = models.CharField(max_length=40)
    Status = models.CharField(max_length=100)
    Owner = models.CharField(max_length=100)
    Connect_Date = models.TimeField(auto_now=False, auto_now_add=False)
    Disconnect_Date = models.TimeField(auto_now=False, auto_now_add=False)
    
    class Meta:
        db_table = "Transformers"
        managed = False


class UnitOfMeasure(models.Model):
    """Represents a unit of measure to provide context for readings and loads
    (eg. kW, kWh, kvar).
    """
    UnitOfMeasureID = models.IntegerField(primary_key=True, db_column="UOMID")
    PrimaryDescription = models.CharField(max_length=50)
    SecondaryDescription = models.CharField(max_length=50)
    
    class Meta:
        db_table = "UnitsOfMeasure"
        managed = False


class DataQualityFlag(models.Model):
    """Describes several data quality issues that can be joined to Meter or 
    Transformer objects.
    """
    data_quality_flag_id = models.IntegerField(primary_key=True)
    flag_description = models.CharField(max_length=48)
    
    class Meta:
        db_table = "data_quality_flag"
        managed = False


class TransformerLoad(models.Model):
    """A timeseries measurement of demand for each 
        :model:`transformer_demand.Transformer`.
    """
    TransformerLoadID = models.IntegerField(primary_key=True, 
                                            db_column="TransformerLoads_id")
    Transformer = models.ForeignKey(Transformer, db_column="TransformerID")
    ReadDate = models.DateField()
    reading_datetime_standard = models.DateTimeField()
    Interval = models.IntegerField()
    LoadMW = models.FloatField(db_column="TransformerLoad")
    
    class Meta:
        db_table = "TransformerLoads"
        managed = False
        ordering = ["reading_datetime_standard"]
    

class Meter(models.Model):
    """Represents a customer meter record."""
    # Although MySQL contains composite PK, MeterID is unique for Django
    MeterID = models.IntegerField(primary_key=True)  
    MeterNumber = models.CharField(max_length=30)
    CustomerPremiseNumber = models.IntegerField()
    ConnectDate = models.TimeField(auto_now=False, auto_now_add=False)
    DisconnectDate = models.TimeField(auto_now=False, auto_now_add=False)
    PeakKW = models.FloatField()
    Volts = models.IntegerField()
    Phase = models.IntegerField()
    Enabled = models.BooleanField()
    Feeder = models.ForeignKey(Feeder, db_column="Feeder")
    Transformer = models.ForeignKey(Transformer, db_column="TransformerID")
    PropertyType = models.ForeignKey(PropertyType, 
                                     db_column="property_type_id")
    fsa_code = models.CharField(max_length=3)
    da_id_2006 = models.IntegerField()
    da_id_2011 = models.IntegerField()

    class Meta:
        db_table = "Meters"
        unique_together = ("MeterNumber", 
                           "CustomerPremiseNumber", 
                           "ConnectDate")
        managed = False


class MeterDataQualityFlag(models.Model):
    """Joins a Meter and a DataQualityFlag to mark an issue with a given
    Meter, described with the DataQualityFlag
    """
    meter_data_quality_flag_id = models.IntegerField(primary_key=True)
    Meter = models.ForeignKey(Meter, db_column="MeterID")
    DataQualityFlag = models.ForeignKey(DataQualityFlag, 
                                        db_column="data_quality_flag_id")
    applicability_start_date = models.DateField()
    applicability_end_date = models.DateField()
    
    class Meta:
        db_table = "meter_data_quality_flag"
        managed = False


class SmartMeterReading(models.Model):
    """Hourly electricity demand measurements for households."""
    # Althought MySQL contains composite PK, SmartMeterReadings_id has been 
    # added with a unique index for the purposes of ORM in Django
    SmartMeterReadingsID = models.IntegerField(primary_key=True, 
                                               db_column="SmartMeterReadings_id")
    Meter = models.ForeignKey(Transformer, db_column="MeterID")
    ReadDate = models.DateField()
    ReadTime = models.IntegerField()
    read_datetime = models.DateTimeField()
    UnitOfMeasure = models.ForeignKey(UnitOfMeasure, db_column="UOMID")
    Reading = models.FloatField()
    
    class Meta:
        db_table = "SmartMeterReadings"
        unique_together = ("MeterNumber",
                           "ReadDate",
                           "ReadTime",
                           "UnitOfMeasure")
        managed = False
        
        
