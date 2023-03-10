# from django.contrib.gis.db import models
from django.db import models
from django.utils import timezone


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=30, default='guest')
    first_anme = models.CharField(max_length=30, default='guest')
    last_name = models.CharField(max_length=30, default='guest')
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)

    def __str__(self):
        return f'{self.username}: {self.first_anme} {self.last_name}'


class UserLocation(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=8, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    created_at = models.DateTimeField(db_index=True, default=timezone.now)


class Photo(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    content = models.BinaryField()
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    location = models.ForeignKey("UserLocation", on_delete=models.RESTRICT)
