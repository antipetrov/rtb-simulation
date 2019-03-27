from django.shortcuts import render
from django.http import HttpResponse
from . models import Ad, Category

def index(request):

    ads = Ad.objects.all()

    return render(request, 'index.html', {'ads': ads})