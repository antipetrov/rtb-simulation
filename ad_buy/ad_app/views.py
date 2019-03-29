from datetime import date

from django.shortcuts import render, resolve_url
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.conf import settings

from . models import Ad, Category, AdTimetable, WEEKDAYS
from . forms import AdTimetableForm


def index(request):

    cat = request.GET.get('cat')
    search = request.GET.get('search')
    page = request.GET.get('page', 1)

    ads = Ad.objects.prefetch_related('categories')

    category_selected = None
    if cat:
        category_selected = Category.objects.filter(tag=cat).first()
        if category_selected:
            ads = ads.filter(categories__pk=category_selected.pk)

    if search:
        ads = ads.filter(content__icontains=search)

    ads = ads.order_by('-id').all()

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

    # check if ad exists
    try:
        current_ad = Ad.objects.prefetch_related('categories').get(pk=id)
    except Ad.DoesNotExist:
        return HttpResponse(status=404)

    current_timetables = current_ad.timetables.prefetch_related('categories').all()
    cats = [(cat.pk, cat.name) for cat in current_ad.categories.all()]

    if request.POST:
        form = AdTimetableForm(data=request.POST)
        form.fields['category_ids'].choices = cats

        if not form.is_valid():

            form.fields['category_ids'].choices = cats
            return render(request, 'ad_single.html', {'current_ad': current_ad,
                                                      'form': form,
                                                      'errors': form.errors})
        else:
            new_timetable = AdTimetable(
                ad=current_ad,
                start_date=form.cleaned_data['start_date'],
                weekdays=form.cleaned_data['weekdays'],
                day_count=form.cleaned_data['day_count'],
                cpm=form.cleaned_data['cpm'],

            )

            new_timetable.save()

            new_timetable.categories.set(form.cleaned_data['category_ids'])

            return render(request, 'ad_single.html', {'current_ad': current_ad,
                                                      'form': form,
                                                      'errors': form.errors,
                                                      'message': 'Расписание сохранено!'})


    else:
        selected_cat_ids = [c[0] for c in cats]

        initial_data = {
            'category_ids': selected_cat_ids,
            'start_date': date.today().strftime(settings.DATE_FORMAT),
            'day_count':1,
            'cpm': 10,
            'weekdays': [w[0] for w in WEEKDAYS]
        }

        form = AdTimetableForm(initial=initial_data)
        form.fields['category_ids'].choices = cats

    return render(request, 'ad_single.html', {
        'current_ad': current_ad,
        'timetables': current_timetables,
        'form': form,
        'errors': []
    })
