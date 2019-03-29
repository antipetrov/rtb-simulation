from datetime import date
import json

from django.shortcuts import render, resolve_url
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.conf import settings

from . models import Ad, Category, AdTimetable, AdCalendarDate
from . forms import AdTimetableForm
from . utils import timetable_to_dates, calculate_daily_views


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
            'weekdays': [w[0] for w in settings.WEEKDAYS]
        }

        form = AdTimetableForm(initial=initial_data)
        form.fields['category_ids'].choices = cats

    return render(request, 'ad_single.html', {
        'current_ad': current_ad,
        'timetables': current_timetables,
        'form': form,
        'errors': []
    })


def ad_timetable_preview_json(request, id):

    try:
        current_ad = Ad.objects.prefetch_related('categories').get(pk=id)
    except Ad.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'ad {} not found'.format(id)}, status=400)

    try:
        timetable_data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'error': 'json decode error'}, status=400)

    # load cats (to validate form)
    categories_all = current_ad.categories.all()
    cats = [(cat.pk, cat.name) for cat in categories_all]

    form = AdTimetableForm(data=timetable_data)
    form.fields['category_ids'].choices = cats

    if not form.is_valid():
        return JsonResponse({'status': 'error', 'error': 'data invalid'}, status=400)

    # from here timetable_data considered valid

    cat_views = {cat.pk:cat.stat_views_daily for cat in categories_all}
    cats_dict = dict(cats)

    date_list = timetable_to_dates(
        form.cleaned_data['start_date'],
        form.cleaned_data['day_count'],
        form.cleaned_data['weekdays']
    )

    daily_bids_data = AdCalendarDate.daily_winners(date_list)

    view_stat = calculate_daily_views(current_ad, )

    # проходим по выбранным датам и считаем посещения
    # если другое объявление выигрывает - посещений нет
    warnings = []
    views_dict = {}
    views_total = 0
    for new_date in date_list:
        daily_data = daily_data.get(new_date, {})
        date_key = new_date.isoformat()

        views_dict[date_key] = 0

        for new_cat_id in form.cleaned_data['category_ids']:
            new_cat_idx = int(new_cat_id)
            best_ad = daily_data.get(new_cat_idx, {}).get('best_ad')

            if best_ad:
                if best_ad['cpm'] > form.cleaned_data['cpm']:
                    warnings.append({
                        'date': new_date,
                        'category': cats_dict[new_cat_idx],
                        'recommended_cpm': best_ad['cpm'] + 1,
                        'new_cpm': form.cleaned_data['cpm']
                    })
                else:
                    views_dict[date_key] += cat_views[new_cat_idx]
                    views_total += cat_views[new_cat_idx]
            else:
                views_dict[date_key] += cat_views[new_cat_idx]
                views_total += cat_views[new_cat_idx]

    return JsonResponse({
        'status': 'ok',
        'warnings': warnings,
        'dates': date_list,
        'views_total': views_total,
        'views': views_dict,
    })
