from datetime import date, timedelta
from django.conf import settings




def timetable_to_dates(start_date: date, day_count: int, weekdays_allowed: list) -> list:
    """
    Конвертируем параметры расписания в список дат
    :param start_date: начало показа
    :param day_count: дней показа
    :param weekdays_allowed: в какие дни недели разрешено
    :return: list список дат
    """
    result = []

    day_count = day_count
    new_date = start_date

    while day_count > 0:

        # if weekday allowed
        current_weekday_code = settings.WEEKDAYS[new_date.weekday()][0]
        if weekdays_allowed and current_weekday_code in weekdays_allowed:

            result.append(new_date)

            day_count -= 1
            new_date += timedelta(days=1)

    return result


def calculate_daily_views(current_ad, date_list, category_ids, cpm):

    from .models import AdCalendarDate

    daily_bids_data = AdCalendarDate.daily_winners(date_list)

    categories_all = current_ad.categories.all()
    cat_views = {cat.pk:cat.stat_views_daily for cat in categories_all}
    cats_dict = {cat.pk:cat.name for cat in categories_all}

    # проходим по выбранным датам и считаем посещения
    # если другое объявление выигрывает - посещений нет
    warnings = []
    views_dict = {}
    views_total = 0
    for new_date in date_list:
        daily_data = daily_bids_data.get(new_date, {})
        date_key = new_date.isoformat()

        views_dict[date_key] = 0

        for new_cat_id in category_ids:
            new_cat_idx = int(new_cat_id)
            best_ad = daily_data.get(new_cat_idx, {}).get('best_ad')

            if best_ad:
                if best_ad['cpm'] > cpm:
                    warnings.append({
                        'date': new_date,
                        'category': cats_dict[new_cat_idx],
                        'recommended_cpm': best_ad['cpm'] + 1,
                        'new_cpm': cpm
                    })
                else:
                    views_dict[date_key] += cat_views[new_cat_idx]
                    views_total += cat_views[new_cat_idx]
            else:
                views_dict[date_key] += cat_views[new_cat_idx]
                views_total += cat_views[new_cat_idx]

    return {
        'warnings': warnings,
        'dates': date_list,
        'views_total': views_total,
        'views': views_dict,
    }