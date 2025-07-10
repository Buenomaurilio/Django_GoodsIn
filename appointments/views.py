# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Appointment
# from .forms import AppointmentForm
# from django.contrib.auth.decorators import login_required

# @login_required
# def appointment_list(request):
#     data_filter = request.GET.get('date')
#     if data_filter:
#         appointments = Appointment.objects.filter(scheduled_date=data_filter)
#     else:
#         appointments = Appointment.objects.all().order_by('-scheduled_date', '-scheduled_time')

#     form = AppointmentForm()
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('appointments')

#     return render(request, 'appointments/appointment_list.html', {
#         'form': form,
#         'appointments': appointments,
#         'data_filter': data_filter
#     })

# @login_required
# def edit_appointment(request, pk):
#     appointment = get_object_or_404(Appointment, pk=pk)
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST, instance=appointment)
#         if form.is_valid():
#             form.save()
#             return redirect('appointment_list')
#     else:
#         form = AppointmentForm(instance=appointment)

#     return render(request, 'appointments/edit_appointment.html', {
#         'form': form,
#         'appointment': appointment
#     })


# def add_appointment(request):
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('appointment_list')
#     else:
#         form = AppointmentForm()
#     return render(request, 'appointments/add_appointment.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from .forms import AppointmentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import time
from .forms import CheckerForm
from .models import Checker
import csv
from django.http import HttpResponse
import io
from django.contrib import messages

@login_required
def appointment_list(request):
    data_filter = request.GET.get('date')

    if data_filter:
        appointments = Appointment.objects.filter(scheduled_date=data_filter).order_by('scheduled_time')
    else:
        appointments = Appointment.objects.all().order_by('-scheduled_date', '-scheduled_time')

    # Filtro por turno
    morning_shift = appointments.filter(scheduled_time__gte=time(5, 0), scheduled_time__lt=time(13, 30))
    back_shift = appointments.filter(scheduled_time__gte=time(13, 0), scheduled_time__lt=time(21, 30))

    # Cálculos de resumo
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
    print("Entrou na view de adicionar checker") 
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
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)

            for row in reader:
                Appointment.objects.create(
                    description=row['descricao'],
                    scheduled_date=row['data'],
                    scheduled_time=row['hora'],
                    po=row['p.o'],
                    qtd_pallet=row['qty'],
                    hall=1  # ou um valor padrão
                )
            messages.success(request, "Appointments imported successfully.")
            return redirect('appointment_list')
    else:
        form = CSVImportForm()
    return render(request, 'appointments/import_csv.html', {'form': form})
