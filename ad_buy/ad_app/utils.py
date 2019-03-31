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

