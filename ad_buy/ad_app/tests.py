from datetime import date
from django.test import TestCase

from django.conf import settings
from django.test import TestCase
from . models import Ad, Category, AdTimetable, AdCalendarDate
from . utils import timetable_to_dates


class UtilsTestCase(TestCase):
    def test_timetable_to_dates(self):
        dates = timetable_to_dates(date(2019,3,30), 2, [settings.W_FRIDAY[0]])

        self.assertEqual(dates[0], date(2019,4,5))
        self.assertEqual(dates[1], date(2019,4,12))


class AdTestCase(TestCase):

    def setUp(self):
        self.cat1 = Category.objects.create(name='testcat1', tag='testcat1', stat_views_daily=300)
        self.cat2 = Category.objects.create(name='testcat2', tag='testcat2', stat_views_daily=400)

        self.ad1 = Ad.objects.create(content='test1')
        self.ad1.categories.add(self.cat1)
        self.ad1.categories.add(self.cat2)

        self.ad2 = Ad.objects.create(content='test2')
        self.ad2.categories.add(self.cat1)

        self.ad3 = Ad.objects.create(content='test3')
        self.ad3.categories.add(self.cat2)

    def TearDown(self):
        self.ad1.delete()
        self.ad2.delete()
        self.ad3.delete()

    def test_calendar_creation(self):
        # create new timetable
        AdTimetable.objects.create(
            ad=self.ad1,
            start_date=date(2019, 3, 30),
            day_count=10,
            weekdays=list(settings.WEEKDAYS_DICT.keys()),
            cpm=10,
        )

        dates = self.ad1.get_dates()

        self.assertEqual(len(dates), 10)

    def test_calendar_weekdays(self):

        # check correct weekdays parsing
        AdTimetable.objects.create(
            ad=self.ad1,
            start_date=date(2019, 3, 30),
            day_count=2,
            weekdays=[settings.W_FRIDAY[0]],
            cpm=10,
        )

        dates = self.ad1.get_dates()

        self.assertEqual(dates[0], date(2019, 4, 5))
        self.assertEqual(dates[1], date(2019, 4, 12))


    def test_ad_wins(self):

        AdTimetable.objects.create(
            ad=self.ad1,
            start_date=date(2019, 3, 30),
            day_count=5,
            weekdays=list(settings.WEEKDAYS_DICT.keys()),
            cpm=10,
        )

        AdTimetable.objects.create(
            ad=self.ad2,
            start_date=date(2019, 3, 30),
            day_count=2,
            weekdays=list(settings.WEEKDAYS_DICT.keys()),
            cpm=20,
        )

        dates = self.ad1.get_dates()
        wins = AdCalendarDate.get_daily_wins(dates)

        self.assertEqual(wins[dates[0]][self.cat1.pk]['ad_id'], self.ad2.pk)

    def test_forecast(self):

        AdTimetable.objects.create(
            ad=self.ad1,
            start_date=date(2019, 3, 30),
            day_count=5,
            weekdays=list(settings.WEEKDAYS_DICT.keys()),
            cpm=10,
        )

        AdTimetable.objects.create(
            ad=self.ad2,
            start_date=date(2019, 3, 30),
            day_count=2,
            weekdays=list(settings.WEEKDAYS_DICT.keys()),
            cpm=20,
        )

        AdTimetable.objects.create(
            ad=self.ad3,
            start_date=date(2019, 3, 30),
            day_count=2,
            weekdays=list(settings.WEEKDAYS_DICT.keys()),
            cpm=5,
        )

        dates = [date(2019, 3, 30)]

        # check if ad2 wins all cat1 views
        total_views, warnings = self.ad2.get_views_forecast(dates)
        self.assertEqual(total_views, self.cat1.stat_views_daily)

        # check if ad1 has cat2 views
        total_views, warnings = self.ad1.get_views_forecast(dates)
        self.assertEqual(total_views, self.cat2.stat_views_daily)

        # check if ad1 has ca1+cat2 views, when ad2 is inactive
        total_views, warnings = self.ad1.get_views_forecast([date(2019, 4, 2)])
        self.assertEqual(total_views, self.cat1.stat_views_daily + self.cat2.stat_views_daily)

        # check if ad3 looses it all
        total_views, warnings = self.ad3.get_views_forecast(dates)
        self.assertEqual(total_views, 0)
        self.assertEqual(len(warnings), 1)

        # warning contains category name
        self.assertTrue(self.cat2.name in warnings[0]['category'])
