from .models import Checker
from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # Lista de campos que vão aparecer no formulário:
        fields = [
            'description',
            'scheduled_date',
            'scheduled_time',
            'po',
            'qtd_pallet',
            'hall',
            'tipped',
            'checked',
            'checker',
            'arrival_time',
            'check_out_time',
            'bay1',
        ]
        widgets = {
            'scheduled_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'arrival_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'check_out_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'scheduled_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }



# class AppointmentForm(forms.ModelForm):
#     class Meta:
#         model = Appointment
#         fields = [
#             'description', 'scheduled_date', 'scheduled_time', 'po', 'qtd_pallet',
#             'hall', 'tipped', 'checked', 'checker', 'feeder', 'putaway_driver',
#             'arrival_time', 'check_out_time', 'bay1', 'bay2', 'bay3'
#         ]
#         widgets = {
#             'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
#             'scheduled_time': forms.TimeInput(attrs={'type': 'time'}),
#             'arrival_time': forms.TimeInput(attrs={'type': 'time'}),
#             'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
#         }


class CheckerForm(forms.ModelForm):
    class Meta:
        model = Checker
        fields = ['name']


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
