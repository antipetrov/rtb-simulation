from django import forms
from datetime import date

W_MONDAY = ('mon', 'Понедельник')
W_TUESDAY = ('tue', 'Вторник')
W_WEDNESDAY = ('wed', 'Среда')
W_THURSDAY = ('thr', 'Четверг')
W_FRIDAY = ('fri', 'Пятница')
W_SATURDAY = ('sat', 'Суббота')
W_SUNDAY = ('sun', 'Воскресенье')

WEEKDAYS = (W_MONDAY, W_TUESDAY, W_WEDNESDAY, W_THURSDAY, W_FRIDAY, W_SATURDAY, W_SUNDAY)


class AdTimetableForm(forms.Form):
    start_date = forms.DateField(label='Дата Начала', widget=forms.DateInput, )
    category_ids = forms.MultipleChoiceField(label="В категориях", choices=[], widget=forms.CheckboxSelectMultiple)
    weekdays = forms.MultipleChoiceField(label="Дни недели", choices=WEEKDAYS, widget=forms.CheckboxSelectMultiple)
    day_count = forms.IntegerField(label="Дней показа")
    cpm = forms.IntegerField(label="CPM (руб. за 1000 показов)")