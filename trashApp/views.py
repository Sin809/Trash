import os, json, csv, smtplib
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from email.message import EmailMessage

# Create your views here.

def login_html(request):
    return render(request, 'login.html')

def registrieren_html(request):
    return render(request, 'registrieren.html')

def profil_html(request):
    return render(request, 'profil.html')

def profil_bearbeiten(request):
    return render(request, 'profil.html')

def dashboard_html(request):
    return render(request, 'dashboard.html')

def logout(request):
    return redirect('login')

def kontakt_email(request):
    return HttpResponse("""
                            <script>
                                alert("Noch nichts.");
                                window.history.back();
                            </script>
                        """, status=400)