import os, json, csv, smtplib
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from email.message import EmailMessage

# Create your views here.

def login_html(request):
    return render(request, 'trashApp/login.html')

def registrieren_html(request):
    return render(request, 'trashApp/registrieren.html')

def profil_html(request):
    return render(request, 'trashApp/profil.html')

def profil_bearbeiten(request):
    return render(request, 'trashApp/profil.html')

def dashboard_html(request):
    return render(request, 'trashApp/dashboard.html')

def admin_html(request):
    return render(request, 'trashApp/admin.html')

def logout(request):
    return redirect('login')

def kontakt_email(request):
    return HttpResponse("""
                            <script>
                                alert("Noch nichts.");
                                window.history.back();
                            </script>
                        """, status=400)