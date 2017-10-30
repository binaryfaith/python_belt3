# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.db.models import Count
from .models import User, Appointment
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, date
from time import strftime
import time
import datetime
import bcrypt
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


def index(request):
    return render(request, "my_app/index.html")

def register(request):

    errors = User.objects.add_validator(request.POST)

    if errors:
        for e in errors:
            messages.error(request, e)
        return redirect("/index")

    user = User.objects.create(
        name=request.POST['name'],
        email=request.POST['email'],
        date_of_birth=datetime.datetime.strptime(request.POST['date_of_birth'], '%m/%d/%Y'),
        password=bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()),
    )

    request.session['id'] = user.id

    return redirect("/display_appointments")

def login(request):

    errors = User.objects.login_validator(request.POST)

    if errors:
        for e in errors:
            messages.error(request, e)
        return redirect("/login")

    user = User.objects.get(email=request.POST['email'])

    request.session['id'] = user.id
    return redirect("/display_appointments")

def display_appointments(request):
    print request.session['id']
    user = User.objects.get(id=request.session['id'])
    context = {
        "user" : User.objects.get(id=request.session['id']),
        "today" : datetime.datetime.now().date(),
        "appointments_today" : Appointment.objects.filter(user_id=User.objects.get(id=request.session['id'])).filter(date=datetime.datetime.now().date()).order_by('time'),
        "appointments_future" : Appointment.objects.filter(user_id=User.objects.get(id=request.session['id'])).exclude(date=datetime.datetime.now().date()).order_by('date'),
        "appointments" : Appointment.objects.all()
        }
    return render(request, 'my_app/display_appointments.html', context)



def add_appointment(request):
    check = True 
 
    if len(request.POST['date']) < 6:
        messages.error(request, "Valid date pwease")
        check = False
    elif datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date() < datetime.datetime.now().date():
        messages.error(request, "You are not Kyle Reese so you cannot travel back in time to father your best friend please enter a valid date in the future when the machines ultimately take over") 
        check = False        
    if len(request.POST['time']) < 4:
        messages.error(request, "Valid time please")
        check = False  
    if len(request.POST['name']) < 1:
        messages.error(request, "Um enter something or do you want to remember to do nothing?")
        check = False
  
    if not check:
        return redirect('/display_appointments')

    try:
        Appointment.objects.get(time=request.POST['time'], date=request.POST['date'])
    except ObjectDoesNotExist:
        then = True
    else:
        messages.error(request, "Your already doing something member?")
        return redirect('/display_appointments')   

    Appointment.objects.create(user_id=User.objects.get(id=request.session['id']), name=request.POST['name'], status="Pending", date=request.POST['date'], time=request.POST['time'])  
    return redirect('/display_appointments')

def update_appointment(request, id):
    check = True
    if len(request.POST['date']) < 6:
        messages.error(request, "Valid date pwease")
        check = False
    elif datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date() < datetime.datetime.now().date():
        messages.error(request, "Get in your Delorean and go back to the future, see what i did there") 
        check = False        
    if len(request.POST['time']) < 4:
        messages.error(request, "Valid time pwease")
        check = False    
    if len(request.POST['name']) < 1:
        messages.error(request, "Enter as task any task")
        check = False
        return redirect('/')
    if not check:
        return redirect('/edit/'+ str(Appointment.objects.get(id=id).id))
    try:
        Appointment.objects.exclude(id=id).get(time=request.POST['time'], date=request.POST['date'])
    except ObjectDoesNotExist:
        then = True
    else:
        messages.error("Good thing you have this app otherwise you'd double schedule all the time")
        return redirect('/edit/'+ str(Appointment.objects.get(id=id).id))       
    appointment = Appointment.objects.get(id=id)
    appointment.name = request.POST['name']   
    appointment.status = request.POST['status']
    appointment.date = request.POST['date']
    appointment.time = request.POST['time']
    appointment.save()
    return redirect('/display_appointments')

def edit(request, id):
    context = {
        "appointment" : Appointment.objects.get(id=id),
        "date" : str(Appointment.objects.get(id=id).date),
        "time" : str(Appointment.objects.get(id=id).time)
    } 
    return render(request, 'my_app/edit_appointments.html', context) 

def delete(request, id):
    Appointment.objects.get(id=id).delete()
    return redirect('/display_appointments') 

def logout(request):
    request.session.clear()
    messages.add_message(request, messages.INFO, "And your out!")
    return redirect('/')