import csv

from django.shortcuts import render
from django.views import generic
from bot import models
from django.http import HttpResponse


class PhotoListView(generic.ListView):
    model = models.Photo


def PhotoRawView(request, pk):
    photo = models.Photo.objects.get(pk=pk)
    return HttpResponse(photo.content, content_type="application/octet-stream")


def csv_download(request):
    data = models.Photo.objects.select_related('user').select_related('location').all()
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="leafy.csv"'},
    )
    writer = csv.writer(response)
    writer.writerow(['user id', 'username', 'first name', 'last name', 'phone', 'location- longtitude',
                     'location- latitude', 'accuracy', 'picture url'])
    for line in data:
        writer.writerow(line.user.id, line.user.username, line.user.first_anme, line.user.last_name,
                        line.user.phone, line.location.longitude, line.location.latitude,
                        line.location.accuracy_meters, f'https://leafy.hasadna.org.il/photos/raw/{line.id}/')
