from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from .forms import AppointmentForm, CheckerForm
from .models import Checker
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import time, datetime
import csv
import io
from django.http import HttpResponse
from django.contrib import messages
from django import forms
from django.utils.dateparse import parse_date, parse_time
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.utils.timezone import now
from django.shortcuts import render
from .models import Appointment


class CSVImportForm(forms.Form):
    file = forms.FileField()


@login_required
def appointment_list(request):
    data_filter = request.GET.get('date')

    if data_filter:
        appointments = Appointment.objects.filter(scheduled_date=data_filter).order_by('scheduled_time')
    else:
        appointments = Appointment.objects.all().order_by('-scheduled_date', '-scheduled_time')

    morning_shift = appointments.filter(scheduled_time__gte=time(5, 0), scheduled_time__lt=time(13, 30))
    back_shift = appointments.filter(scheduled_time__gte=time(13, 0), scheduled_time__lt=time(21, 30))

    total_appointments = appointments.count()
    morning_count = morning_shift.count()
    back_count = back_shift.count()

    morning_pallets = morning_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0
    back_pallets = back_shift.aggregate(Sum('qtd_pallet'))['qtd_pallet__sum'] or 0

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'data_filter': data_filter,
        'total_appointments': total_appointments,
        'morning_count': morning_count,
        'back_count': back_count,
        'morning_pallets': morning_pallets,
        'back_pallets': back_pallets,
    })


@login_required
def edit_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/edit_appointment.html', {
        'form': form,
        'appointment': appointment
    })


@login_required
def add_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/add_appointment.html', {'form': form})


@login_required
def add_checker(request):
    if request.method == 'POST':
        form = CheckerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = CheckerForm()
    return render(request, 'appointments/add_checker.html', {'form': form})


@login_required
def export_appointments_csv(request):
    data_filter = request.GET.get('date')
    appointments = Appointment.objects.all()
    if data_filter:
        appointments = appointments.filter(scheduled_date=data_filter)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Description', 'Date', 'Time', 'P.O', 'Qty', 'Hall', 'Tipped', 'Checked', 'Checker'])

    for appt in appointments:
        writer.writerow([
            appt.id,
            appt.description,
            appt.scheduled_date,
            appt.scheduled_time,
            appt.po,
            appt.qtd_pallet,
            appt.hall,
            appt.tipped,
            appt.checked,
            appt.checker.name if appt.checker else ''
        ])

    return response


@login_required
def import_appointments_csv(request):
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                decoded_file = io.TextIOWrapper(file, encoding='utf-8')
                reader = csv.DictReader(decoded_file)

                for row in reader:
                    try:
                        Appointment.objects.create(
                            description=row['Description'],
                            scheduled_date=parse_date(row['Date']),
                            scheduled_time=parse_time(row['Time']),
                            po=row['P.O'],
                            qtd_pallet=int(row['Qty']),
                        )
                    except Exception as e:
                        messages.warning(request, f"Erro ao importar linha {row}: {e}")

                messages.success(request, "Appointments imported successfully.")
                return redirect('appointment_list')
            except Exception as e:
                messages.error(request, f"Erro ao processar arquivo: {e}")
                return redirect('appointment_list')
    else:
        form = CSVImportForm()

    return render(request, 'appointments/import_csv.html', {'form': form})


@login_required
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.delete()
    messages.success(request, "Appointment deleted successfully.")
    return redirect('appointment_list')

from django.template.loader import render_to_string
from django.http import JsonResponse

@login_required
def appointment_table_partial(request):
    data_filter = request.GET.get('date')
    if data_filter:
        appointments = Appointment.objects.filter(scheduled_date=data_filter).order_by('scheduled_time')
    else:
        appointments = Appointment.objects.all().order_by('-scheduled_date', '-scheduled_time')

    return JsonResponse({
        'table_html': render_to_string('appointments/appointment_table_partial.html', {
            'appointments': appointments
        })
    })

def dashboard_view(request):
    today = now().date()
    month = today.month
    year = today.year

    # Pallets totais
    pallets_today = Appointment.objects.filter(scheduled_date=today).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_month = Appointment.objects.filter(scheduled_date__month=month, scheduled_date__year=year).aggregate(total=Sum('qtd_pallet'))['total'] or 0
    pallets_total = Appointment.objects.aggregate(total=Sum('qtd_pallet'))['total'] or 0

    # Pallets por checker (mensal)
    checker_month = (
        Appointment.objects.filter(scheduled_date__month=month, scheduled_date__year=year)
        .values('checker__name')
        .annotate(total=Sum('qtd_pallet'))
        .order_by('-total')
    )

    # Loads por status
    loads_status_day = (
        Appointment.objects.filter(scheduled_date=today)
        .values('status_load')
        .annotate(count=Count('id'))
    )

    loads_status_month = (
        Appointment.objects.filter(scheduled_date__month=month, scheduled_date__year=year)
        .values('status_load')
        .annotate(count=Count('id'))
    )

    context = {
        'pallets_today': pallets_today,
        'pallets_month': pallets_month,
        'pallets_total': pallets_total,
        'checker_month': checker_month,
        'loads_status_day': loads_status_day,
        'loads_status_month': loads_status_month,
    }

    return render(request, 'appointments/dashboard.html', context)
