from django import forms
from django.core import validators
from . models import WEEKDAYS



class AdTimetableForm(forms.Form):
    start_date = forms.DateField(
        label='Начало показа',
        widget=forms.DateInput(attrs={'class': 'form-control'}),
    )

    day_count = forms.IntegerField(
        label="Длительность показа",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validators.MinValueValidator(1)]
    )

    category_ids = forms.MultipleChoiceField(
        label="Показывать только в этих категориях",
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
     )

    weekdays = forms.MultipleChoiceField(
        label="Показывать только в эти дни недели",
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple()
    )

    cpm = forms.IntegerField(
        label="CPM (руб. за 1000 показов)",
        widget = forms.TextInput(attrs={'class': 'form-control'})
    )