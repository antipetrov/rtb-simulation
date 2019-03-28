from datetime import date

from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.conf import settings

from . models import Ad, Category
from . forms import AdTimetableForm


def index(request):

    cat = request.GET.get('cat')
    search = request.GET.get('search')
    page = request.GET.get('page', 1)

    ads = Ad.objects

    category_selected = None
    if cat:
        category_selected = Category.objects.filter(tag=cat).first()
        if category_selected:
            ads = ads.filter(categories__pk=category_selected.pk)

    if search:
        ads = ads.filter(content__icontains=search)

    ads = ads.all()

    paginator = Paginator(ads, settings.ADS_LIST_ON_PAGE)

    return render(request, 'index.html',
                  {
                      'ads': paginator.get_page(page),
                      'paginator': paginator,
                      'current_page': page,
                      'current_category': category_selected,
                      'search': search
                  })


def ad_view(request, id):
    try:
        current_ad = Ad.objects.get(pk=id)
    except Ad.DoesNotExist:
        return HttpResponse(status=404)

    cats = [(cat.pk, cat.name) for cat in current_ad.categories.all()]
    selected_cat_ids = [c[0] for c in cats]

    initial_data = {
        'category_ids': selected_cat_ids,
        'start_date': date.today().strftime(settings.DATE_FORMAT)
    }

    form = AdTimetableForm(initial=initial_data)
    form.fields['category_ids'].choices = cats

    return render(request, 'ad_single.html', {'current_ad': current_ad, 'form': form})


