from django.shortcuts import render
from django.http import HttpResponse
from . models import Ad, Category

def index(request):

    ads = Ad.objects.all()

    return render(request, 'index.html', {'ads': ads})


def ad_view(request, id):

    current_ad = Ad.objects.get(pk=id)

    return render(request, 'ad_single.html', {'current_ad': current_ad})