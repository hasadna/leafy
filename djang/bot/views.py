from django.shortcuts import render
from django.views import generic
from bot import models
from django.http import HttpResponse


class PhotoListView(generic.ListView):
    model = models.Photo


def PhotoRawView(request, pk):
    photo = models.Photo.objects.get(pk=pk)
    return HttpResponse(photo.content, content_type="application/octet-stream")
