from django.test import TestCase
import os
import uuid
import smtplib
from lxml import etree as ET #alternative zu "xml.etree.ElementTree"
from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
import socket
import paramiko

#A noch unklar
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
# Create your tests here.

"""
#S
def dashboard_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check:
        return check

    uuid_value = request.session.get('uuid')
    eintraege = []
    zaehler = {'Papier': 0, 'Plastik': 0, 'Restmüll': 0, 'Uneindeutig': 0}

    if os.path.exists(LOGBUCH_XML_PATH):
        tree = xmlStrukturierenLogbuch()
        root = tree.getroot()

        benutzer_element = root.find(f"benutzer[@benutzer_id='{uuid_value}']")
        
        if benutzer_element is not None:
            for eintrag in benutzer_element.findall('eintrag'):
                zeit = eintrag.findtext('zeit')
                art = eintrag.findtext('art')
                bild_url = eintrag.findtext('bild_url', default='Kein Bild gemacht')
                eintraege.append({'zeit': zeit, 'art': art, 'bild_url': bild_url})
                if art in zaehler:
                    zaehler[art] += 1

    # Füllstände max 10
    fuellstaende = {}
    for art, count in zaehler.items():
        prozent = min(round((count / 10) * 100), 100)
        fuellstaende[art.lower()] = prozent

"""

"""
    rPiHostname = "sinanpi" #hier einfach ip vom eigenen pi eintragen, dann wird ne TCP-Verbindung aufgebaut
    rPiOnline = checkRPiOnline(rPiHostname)
"""
    
"""

    #login_history = ""

    #if rpi_online and passwort:
     #   login_history = readLoginHistory(hostname, benutzername, passwort, port)
    hostname = request.POST.get('hostname', '')
    benutzername = request.POST.get('benutzername', '')
    passwort = request.POST.get('passwort', '')
    port = int(request.POST.get('port', 22))
    message=""
    rpi_online = False

    if request.method == "POST":
        hostname = request.POST.get('hostname', '')
        benutzername = request.POST.get('benutzername', '')
        passwort = request.POST.get('passwort', '')
        port = int(request.POST.get('port', 22))

        # Prüfe, ob Neustart oder Herunterfahren gewünscht ist
        action = request.POST.get('action')
        if request.method == 'POST':
            action = request.POST.get('action')

        
        rpi_online = checkRPiOnline(hostname, port)

        if action in ['restart', 'shutdown'] and rpi_online:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname, port=port, username=benutzername, password=passwort, timeout=5)

                if action == 'restart':
                    ssh.exec_command('sudo reboot')
                    message = "Neustart-Befehl erfolgreich gesendet."
                elif action == 'shutdown':
                    ssh.exec_command('sudo shutdown -h now')
                    message = "Herunterfahren-Befehl erfolgreich gesendet."

                ssh.close()
            except Exception as e:
                message = f"Fehler bei Verbindung: {str(e)}"

    return render(request, 'trashApp/dashboard.html', {
        'logbuch_eintraege': eintraege,
        'fuellstaende': fuellstaende,
        'rpi_online': rpi_online,
        #'login_history': login_history,
        'hostname': hostname,
        'benutzername': benutzername,
        'passwort': passwort,
        'port': port,
        'message': message,
    })
"""