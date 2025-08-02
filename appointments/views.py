from django.db.models import Sum, Count
from django.utils.timezone import now
from django.utils.dateparse import parse_date, parse_time
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django import forms
import csv
import io

from .models import Appointment, Checker
from .forms import AppointmentForm, CheckerForm

class CSVImportForm(forms.Form):
    file = forms.FileField()

@login_required
def appointment_list(request):
    today = now().date()
    data_filter = request.GET.get('date', today)
    po_filter = request.GET.get('po', '').strip()

    if isinstance(data_filter, str):
        data_filter = parse_date(data_filter)

    appointments = Appointment.objects.filter(scheduled_date=data_filter)

    if po_filter:
        appointments = appointments.filter(po__icontains=po_filter)

    appointments = appointments.order_by('scheduled_time')

    morning_shift = appointments.filter(scheduled_time__gte=parse_time("05:00"), scheduled_time__lt=parse_time("13:30"))
    back_shift = appointments.filter(scheduled_time__gte=parse_time("13:00"), scheduled_time__lt=parse_time("21:30"))

    context = {
        'appointments': appointments,
        'data_filter': data_filter,
        'total_appointments': appointments.count(),
        'morning_count': morning_shift.count(),
        'back_count': back_shift.count(),
        'morning_pallets': morning_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0,
        'back_pallets': back_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0,
    }
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def dashboard_view(request):
    date_str = request.GET.get('date')
    selected_date = parse_date(date_str) if date_str else now().date()

    year = selected_date.year
    month = selected_date.month
    weekday = selected_date.weekday()
    start_of_week = selected_date - timedelta(days=weekday)
    end_of_week = start_of_week + timedelta(days=5)

    pallets_today = Appointment.objects.filter(scheduled_date=selected_date).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_week = Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week)).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_month = Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_total = Appointment.objects.aggregate(total=Sum('qtd_pallet'))['total'] or 0

    loads_today = Appointment.objects.filter(scheduled_date=selected_date).count()
    loads_week = Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week)).count()
    loads_month = Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month).count()
    loads_total = Appointment.objects.count()

    checker_day = (
        Appointment.objects.filter(scheduled_date=selected_date)
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )
    checker_week = (
        Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week))
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )
    checker_month = (
        Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month)
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )

    loads_status_day = (
        Appointment.objects.filter(scheduled_date=selected_date)
        .values('status_load')
        .annotate(count=Count('id'))
    )
    loads_status_week = (
        Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week))
        .values('status_load')
        .annotate(count=Count('id'))
    )
    loads_status_month = (
        Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month)
        .values('status_load')
        .annotate(count=Count('id'))
    )

    context = {
        'selected_date': selected_date,
        'pallets_today': pallets_today,
        'pallets_week': pallets_week,
        'pallets_month': pallets_month,
        'pallets_total': pallets_total,
        'loads_today': loads_today,
        'loads_week': loads_week,
        'loads_month': loads_month,
        'loads_total': loads_total,
        'checker_day': list(checker_day),
        'checker_week': list(checker_week),
        'checker_month': list(checker_month),
        'loads_status_day': list(loads_status_day),
        'loads_status_week': list(loads_status_week),
        'loads_status_month': list(loads_status_month),
    }

    return render(request, 'appointments/dashboard.html', context)

# As outras views como edit_appointment, add_appointment, add_checker, import/export etc
# já estavam OK e não precisam ser alteradas, a menos que queira.

# # views.py
# from django.shortcuts import render
# from django.db.models import Sum, Count
# from django.utils.timezone import now
# from django.utils.dateparse import parse_date
# from datetime import timedelta
# from .models import Appointment

# @login_required
# def dashboard_view(request):
#     date_str = request.GET.get('date')
#     selected_date = parse_date(date_str) if date_str else now().date()

#     year = selected_date.year
#     month = selected_date.month
#     weekday = selected_date.weekday()
#     start_of_week = selected_date - timedelta(days=weekday)  # Monday
#     end_of_week = start_of_week + timedelta(days=5)  # Saturday

#     pallets_today = Appointment.objects.filter(scheduled_date=selected_date).aggregate(total=Sum('qtd_pallet'))['total'] or 0
#     pallets_week = Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week)).aggregate(total=Sum('qtd_pallet'))['total'] or 0
#     pallets_month = Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month).aggregate(total=Sum('qtd_pallet'))['total'] or 0
#     pallets_total = Appointment.objects.aggregate(total=Sum('qtd_pallet'))['total'] or 0

#     checker_month = (
#         Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month)
#         .values('checker__name')
#         .annotate(total=Sum('qtd_pallet'))
#         .order_by('-total')
#     )

#     loads_status_day = (
#         Appointment.objects.filter(scheduled_date=selected_date)
#         .values('status_load')
#         .annotate(count=Count('id'))
#     )

#     loads_status_month = (
#         Appointment.objects.filter(scheduled_date__year=year, scheduled_date__month=month)
#         .values('status_load')
#         .annotate(count=Count('id'))
#     )

#     loads_status_week_qs = (
#         Appointment.objects.filter(scheduled_date__range=(start_of_week, end_of_week))
#         .values('status_load')
#         .annotate(count=Count('id'))
#     )

#     status_by_week = {
#         'labels': [s['status_load'].title() for s in loads_status_week_qs],
#         'datasets': [{
#             'label': 'Status Week',
#             'data': [s['count'] for s in loads_status_week_qs]
#         }]
#     }

#     context = {
#         'selected_date': selected_date,
#         'pallets_today': pallets_today,
#         'pallets_week': pallets_week,
#         'pallets_month': pallets_month,
#         'pallets_total': pallets_total,
#         'checker_month': checker_month,
#         'loads_status_day': loads_status_day,
#         'loads_status_month': loads_status_month,
#         'status_by_week': status_by_week,
#     }

#     return render(request, 'appointments/dashboard.html', context)

# @login_required
# def dashboard_view(request):
#     date_str = request.GET.get('date')
#     selected_date = parse_date(date_str) if date_str else now().date()

#     month = selected_date.month
#     year = selected_date.year

#     pallets_today = Appointment.objects.filter(scheduled_date=selected_date).aggregate(total=Sum('qtd_pallet'))['total'] or 0
#     pallets_month = Appointment.objects.filter(scheduled_date__month=month, scheduled_date__year=year).aggregate(total=Sum('qtd_pallet'))['total'] or 0
#     pallets_total = Appointment.objects.aggregate(total=Sum('qtd_pallet'))['total'] or 0

#     checker_month = (
#         Appointment.objects.filter(scheduled_date__month=month, scheduled_date__year=year)
#         .values('checker__name')
#         .annotate(total=Sum('qtd_pallet'))
#         .order_by('-total')
#     )

#     loads_status_day = (
#         Appointment.objects.filter(scheduled_date=selected_date)
#         .values('status_load')
#         .annotate(count=Count('id'))
#     )

#     loads_status_month = (
#         Appointment.objects.filter(scheduled_date__month=month, scheduled_date__year=year)
#         .values('status_load')
#         .annotate(count=Count('id'))
#     )

#     context = {
#         'selected_date': selected_date,
#         'pallets_today': pallets_today,
#         'pallets_month': pallets_month,
#         'pallets_total': pallets_total,
#         'checker_month': checker_month,
#         'loads_status_day': loads_status_day,
#         'loads_status_month': loads_status_month,
#     }

#     return render(request, 'appointments/dashboard.html', context)
