from django.db import models


class Checker(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    description = models.CharField(max_length=200)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    po = models.CharField(max_length=100)
    qtd_pallet = models.IntegerField()
    hall = models.CharField(max_length=100)
    tipped = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    # checker = models.CharField(max_length=100, blank=True)
    checker = models.ForeignKey(Checker, on_delete=models.SET_NULL, null=True, blank=True)
    arrival_time = models.TimeField(blank=True, null=True)
    check_out_time = models.TimeField(blank=True, null=True)
    bay1 = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.description} ({self.scheduled_date})"
    
    

# from django.db import models

# class Appointment(models.Model):
#     description = models.CharField(max_length=255)
#     scheduled_date = models.DateField()
#     scheduled_time = models.TimeField()
#     po = models.CharField(max_length=50)
#     pallet_qty = models.IntegerField()
#     hall = models.CharField(max_length=50)

#     tipped = models.BooleanField(default=False)
#     checked = models.BooleanField(default=False)
#     checker = models.CharField(max_length=100, blank=True, null=True)
#     feeder = models.CharField(max_length=100, blank=True, null=True)
#     putaway_driver = models.CharField(max_length=100, blank=True, null=True)

#     arrival_time = models.TimeField(blank=True, null=True)
#     check_out_time = models.TimeField(blank=True, null=True)

#     bay1 = models.CharField(max_length=10, blank=True, null=True)
#     bay2 = models.CharField(max_length=10, blank=True, null=True)
#     bay3 = models.CharField(max_length=10, blank=True, null=True)

#     def __str__(self):
#         return self.description
