from django.contrib import admin

# Register your models here.
from .models import Ad, Category, AdTimetable, AdCalendarDate

admin.site.register(Ad)
admin.site.register(Category)
admin.site.register(AdTimetable)
# admin.site.register(AdCalendarDate)

@admin.register(AdCalendarDate)
class AdCalendarDateAdmin(admin.ModelAdmin):
    list_display = ['date', 'ad', 'timetable', 'cpm']
