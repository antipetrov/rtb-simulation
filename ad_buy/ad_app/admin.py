from django.contrib import admin

# Register your models here.
from .models import Ad, Category, AdTimetable, AdCalendarDate

admin.site.register(Ad)
# admin.site.register(Category)
admin.site.register(AdTimetable)
# admin.site.register(StatDailyView)

@admin.register(AdCalendarDate)
class AdCalendarDateAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'ad', 'timetable', 'category', 'cpm']
    list_filter = ['date', 'ad', 'category']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag', 'stat_views_daily']
