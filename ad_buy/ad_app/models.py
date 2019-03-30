from datetime import datetime, timedelta, date

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField

from . utils import timetable_to_dates


class Ad(models.Model):

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    content = models.TextField()
    categories = models.ManyToManyField("Category", related_name="ads", verbose_name="Категории", )

    def get_dates_by_ad(self) -> list:
        """
        Возвращает даты показа объявления
        :return:
        """

        dates_set = set()
        dates_qwr = AdCalendarDate.objects.filter(ad_id=self.pk).order_by('date').all()
        for date_rec in dates_qwr:
            dates_set.add(date_rec.date)

        return list(dates_set)

    def get_views_forecast(self, date_list) -> dict:
        """
        Выбирает из календаря дни показа объявления и за каждый день в каждой категории проводит торги
        Если Ообъявление за этот день - выиграло - прибавляем дневные прсмотры этой категории к общей сумме

        :param ad_object: Ad
        :return: dict
        """
        this_categories_qwr = self.categories.all()
        cats = [(cat.pk, cat.name) for cat in this_categories_qwr]
        cats_names = dict(cats)
        cat_views = {cat.pk: cat.stat_views_daily for cat in this_categories_qwr}

        calendar_dates_qwr = AdCalendarDate.objects.filter(date__in=date_list).all()

        # находим победителей торгов за каждый день показа в каждой категории
        best_ads = {}
        for item in calendar_dates_qwr:

            if item.date not in best_ads:
                best_ads[item.date] = {}

            if item.category_id not in best_ads[item.date]:
                best_ads[item.date][item.category_id] = {
                    'best_ad': {},
                }

            if best_ads[item.date][item.category_id]['best_ad'].get('cpm', 0) < item.cpm:
                best_ads[item.date][item.category_id]['best_ad'] = {'cpm': item.cpm, 'ad_id': item.ad_id}


        # находим просмотры за каждый день в каждой категории
        total_views = 0
        warnings = []
        for date, date_data in best_ads.items():
            for cat_id, ad_data in date_data.items():
                if ad_data['best_ad']['ad_id'] == self.pk:
                    total_views += cat_views[cat_id]
                else:
                    # победил не наш - рекомендация поднять цену

                    #todo: корректно учитывать вторую цену в случае наложения расписаний того же объявления
                    warnings.append({'date': date,
                                     'category': cats_names[cat_id],
                                     'recommended_cpm': ad_data['best_ad']['cpm']+1})

        return total_views, warnings


    def __str__(self):
        return "Объявление #{}: {}".format(self.pk, self.content[:32])


class Category(models.Model):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(verbose_name="Название", max_length=255)
    tag = models.CharField(verbose_name="Тег", max_length=255)
    stat_views_daily = models.IntegerField(verbose_name="Просимотров в день", default=0)

    def __str__(self):
        return "Категория #{}: {}".format(self.pk, self.name)


class AdTimetable(models.Model):

    class Meta:
        verbose_name = 'Расписание показов'
        verbose_name_plural = 'Расписания показов'

    ad = models.ForeignKey(Ad, verbose_name='Объявление',
                           related_name='timetables',  on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='Начало показа', null=False, db_index=True)
    categories = models.ManyToManyField("Category",
                                        related_name="ad_timetables", verbose_name="Категории", )
    weekdays = ArrayField(
        models.CharField(verbose_name="Дни недели", max_length=3,
                         choices=settings.WEEKDAYS, blank=True, default=settings.WEEKDAYS)
    )
    day_count = models.IntegerField(verbose_name="Дней показа")
    cpm = models.IntegerField(verbose_name="CPM (руб. за 1000 показов)")
    time_create = models.DateTimeField(verbose_name="Время создания", default=datetime.now())
    time_update = models.DateTimeField(verbose_name="Время изменения", default=datetime.now())

    @property
    def weekdays_str(self) -> list:
        return [settings.WEEKDAYS_DICT[w] for w in self.weekdays]

    def generate_calendar(self, dry_run=False) -> list:
        """
        Создаем записи AdCalendarDate для этого расписания - по одной записи для каждой даты и категории
        :param dry_run:
        :return:
        """

        calendar_entries = []

        # what categories affected
        target_categories = self.categories.all()
        if not target_categories:
            target_categories = self.ad.categories.all()

        actual_dates = timetable_to_dates(self.start_date, self.day_count, self.weekdays)

        for new_date in actual_dates:
            for current_category in target_categories:
                new_calendar_entry = AdCalendarDate(
                    date=new_date,
                    ad=self.ad,
                    timetable=self,
                    category=current_category,
                    cpm=self.cpm
                )
                if not dry_run:
                    new_calendar_entry.save()
                calendar_entries.append(new_calendar_entry)


        return calendar_entries

    def save(self, *args, **kwargs):
        super(AdTimetable, self).save(*args, **kwargs)

        # delete old calendar
        AdCalendarDate.objects.filter(ad_id=self.pk)

        self.generate_calendar()

    def __str__(self):
        return "Расписание #{}: Объявление #{} с {}".format(self.pk, self.ad.pk, self.start_date)


class AdCalendarDate(models.Model):

    class Meta:
        verbose_name = 'День показа'
        verbose_name_plural = 'Дни показа'

    date = models.DateField(verbose_name='Дата', null=False, db_index=True)

    ad = models.ForeignKey(Ad, verbose_name='Объявление',
                           related_name='calendar_dates',  on_delete=models.CASCADE)

    timetable = models.ForeignKey(AdTimetable, verbose_name='Расписание',
                                  related_name='timetables',  on_delete=models.CASCADE)

    category = models.ForeignKey(Category, verbose_name='Категория',
                                 related_name='calendar_dates', on_delete=models.CASCADE)

    cpm = models.IntegerField(verbose_name="CPM (руб. за 1000 показов)", db_index=True)



    @classmethod
    def get_daily_wins(cls, date_list: list) -> dict:
        """
        Выбирает из календаря дни по указанному списку и показывает самое дорогое объявление в каждой категории

        :param date_list:
        :return: dict
        """
        items = cls.objects.filter(date__in=date_list).all()

        result = {}
        for item in items:

            if item.date not in result:
                result[item.date] = {}

            if item.category_id not in result[item.date]:
                result[item.date][item.category_id] = {
                    'ads': [],
                    'best_ad': {},
                }

            result[item.date][item.category_id]['ads'].append(item)
            if result[item.date][item.category_id]['best_ad'].get('cpm', 0) < item.cpm:
                result[item.date][item.category_id]['best_ad'] = {'cpm': item.cpm, 'ad_id': item.id}

        return result



def get_views_by_ad(ad: Ad) -> dict:
    """
    Выбирает из календаря дни показа объявления ad и за каждый день в каждой категории проводит торги
    Если Ообъявление за этот день - выиграло - прибавляем дневные прсмотры этой категории к общей сумме

    :param ad_object: Ad
    :return: dict
    """

    cat_qwr = ad.categories.all()

    items = cls.objects.filter(date__in=date_list).all()

    result = {}
    for item in items:

        if item.date not in result:
            result[item.date] = {}

        if item.category_id not in result[item.date]:
            result[item.date][item.category_id] = {
                'ads': [],
                'best_ad': {},
            }

        if result[item.date][item.category_id]['best_ad'].get('cpm', 0) < item.cpm:
            result[item.date][item.category_id]['best_ad'] = {'cpm': item.cpm, 'ad_id': item.id}

    return result
