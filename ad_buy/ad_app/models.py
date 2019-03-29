from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import ArrayField

W_MONDAY = ('mon', 'Понедельник')
W_TUESDAY = ('tue', 'Вторник')
W_WEDNESDAY = ('wed', 'Среда')
W_THURSDAY = ('thr', 'Четверг')
W_FRIDAY = ('fri', 'Пятница')
W_SATURDAY = ('sat', 'Суббота')
W_SUNDAY = ('sun', 'Воскресенье')

WEEKDAYS = (W_MONDAY, W_TUESDAY, W_WEDNESDAY, W_THURSDAY, W_FRIDAY, W_SATURDAY, W_SUNDAY)
WEEKDAYS_DICT = dict(WEEKDAYS)

class Ad(models.Model):

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    content = models.TextField()
    categories = models.ManyToManyField("Category", related_name="ads", verbose_name="Категории", )

    def __str__(self):
        return "Объявление #{}: {}".format(self.pk, self.content[:32])


class Category(models.Model):

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(verbose_name="Название", max_length=255)
    tag = models.CharField(verbose_name="Тег", max_length=255)

    def __str__(self):
        return "Категория #{}: {}".format(self.pk, self.name)

class AdTimetable(models.Model):

    class Meta:
        verbose_name = 'Расписание показов'
        verbose_name_plural = 'Расписания показов'

    ad = models.ForeignKey(Ad, verbose_name='Объявление', related_name='timetables',  on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name='Начало показа', null=False, db_index=True)
    categories = models.ManyToManyField("Category", related_name="ad_timetables", verbose_name="Категории", )
    weekdays = ArrayField(models.CharField(verbose_name="Дни недели", max_length=3, choices=WEEKDAYS, blank=True, default=WEEKDAYS))
    day_count = models.IntegerField(verbose_name="Дней показа")
    cpm = models.IntegerField(verbose_name="CPM (руб. за 1000 показов)")
    time_create = models.DateTimeField(verbose_name="Время создания", default=datetime.now())
    time_update = models.DateTimeField(verbose_name="Время изменения", default=datetime.now())

    @property
    def weekdays_str(self):
        return [WEEKDAYS_DICT[w] for w in self.weekdays]

    def __str__(self):
        return "Расписание #{}: Объявление #{} с {}".format(self.pk, self.ad.pk, self.start_date )
