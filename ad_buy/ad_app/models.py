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

    def get_dates(self) -> list:
        """
        Возвращает даты показа объявления
        :return:
        """

        from django.db.models import Max

        dates = []
        calendar_dates = list(AdCalendarDate.objects.values('date').filter(ad_id=self.pk).annotate(cpm_max=Max('cpm')))
        for date_rec in calendar_dates:
            dates.append(date_rec['date'])

        return dates

    def get_views_forecast(self, date_list) -> dict:
        """
        Выбирает из календаря дни показа объявления и за каждый день в каждой категории проводит торги
        Если Ообъявление за этот день - выиграло - прибавляем дневные прсмотры этой категории к общей сумме
        Дневные просмотры берутся из статистики (Category.stat_views_daily)

        :param date_list: list
        :return: dict
        """
        this_categories_qwr = self.categories.all()
        cats = [(cat.pk, cat.name) for cat in this_categories_qwr]
        cats_names = dict(cats)
        cat_views = {cat.pk: cat.stat_views_daily for cat in this_categories_qwr}

        # находим победителей торгов за каждый день показа категориях этого объявления
        best_ads = AdCalendarDate.get_daily_wins(date_list, [cat.pk for cat in this_categories_qwr])

        # считаем просмотры за каждый день в каждой категории
        total_views = 0
        warnings = []
        for date, categories in best_ads.items():
            for cat_id, best_ad_data in categories.items():
                if best_ad_data['ad_id'] == self.pk:
                    total_views += cat_views[cat_id]
                else:
                    # победил не наш - рекомендация поднять цену
                    warnings.append({'date': date,
                                     'category': cats_names[cat_id],
                                     'recommended_cpm': best_ad_data['cpm']+1})

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
    def get_daily_wins(cls, date_list: list, cat_id_list: list = None) -> dict:
        """
        Выбирает из календаря дни по списку date_list и показывает самое дорогое объявление в каждой категории

        Возвращает словарь вида
        result[date][category_id] <- {'cpm':<int>, 'ad_id':<int>}

        :param date_list:
        :return: dict
        """
        items = cls.objects.filter(date__in=date_list)

        if cat_id_list:
            items = items.filter(category__in=cat_id_list)

        result = {}
        for item in items.all():

            if item.date not in result:
                result[item.date] = {}

            if item.category_id not in result[item.date]:
                result[item.date][item.category_id] = {}

            if result[item.date][item.category_id].get('cpm', 0) < item.cpm:
                result[item.date][item.category_id] = {'cpm': item.cpm, 'ad_id': item.ad.id}

        return result

