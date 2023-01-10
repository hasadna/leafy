from django.contrib.gis.db import models

class Canopy(models.Model):
    name = models.CharField(max_length=254)
    geom = models.MultiPolygonField(srid=4326)

class User(models.Model):
    pass

class UserLocation(models.Model):
    pass

class Photo(models.Model):
    pass
