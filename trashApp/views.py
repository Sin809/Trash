import os
import uuid
import smtplib
from lxml import etree as ET
from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse

XML_PATH = os.path.join(os.getcwd(), 'trashApp', 'static', 'db', 'benutzer.xml')

#A
class Benutzer:
    def __init__(self, benutzername, email, passwort, rolle='user'):
        self.id = str(uuid.uuid4())
        self.benutzername = benutzername
        self.email = email
        self.passwort = passwort
        self.rolle = rolle

    def als_xml_speichern(self):
        user = ET.Element('benutzer', id=self.id)
        ET.SubElement(user, 'benutzername').text = self.benutzername
        ET.SubElement(user, 'email').text = self.email
        ET.SubElement(user, 'passwort').text = self.passwort
        ET.SubElement(user, 'rolle').text = self.rolle
        return user
#A    
def lade_benutzer():
    if not os.path.exists(XML_PATH):
        return []
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    return root.xpath('//benutzer')

#A
def registrieren_html(request):
    if request.method == 'POST':
        benutzername = request.POST['benutzername']
        email = request.POST['email']
        passwort = request.POST['passwort']
        pw_wiederholung = request.POST['passwort_wiederholen']

        if passwort != pw_wiederholung:
            return HttpResponse("Passwörter stimmen nicht überein")

        if not os.path.exists(XML_PATH):
            root = ET.Element('benutzerliste')
            tree = ET.ElementTree(root)
        else:
            tree = ET.parse(XML_PATH)
            root = tree.getroot()

        if root.xpath(f"benutzer[benutzername='{benutzername}' or email='{email}']"):
            return HttpResponse("Benutzername oder E-Mail bereits registriert")

        neuer_benutzer = Benutzer(benutzername, email, passwort)#neue user klasse anlegen
        root.append(neuer_benutzer.als_xml_speichern())# klasse als xml speichern
        tree.write(XML_PATH, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return redirect('login')

    return render(request, 'trashApp/registrieren.html')

#A
def benutzer_ist_eingeloggt(request):
    if not request.session.get('uuid'):
        return redirect('login')
    return None

#A    
def login_html(request):
    if request.method == 'POST':
        benutzername = request.POST['benutzername']
        passwort = request.POST['passwort']

        if not os.path.exists(XML_PATH):
            return HttpResponse("Keine Benutzer vorhanden")

        tree = ET.parse(XML_PATH)
        root = tree.getroot()

        benutzer = root.xpath(f"benutzer[benutzername='{benutzername}' and passwort='{passwort}']")

        if benutzer:
            benutzer = benutzer[0]
            request.session['uuid'] = benutzer.attrib['id']
            rolle = benutzer.find('rolle').text
            if rolle == 'admin':
                return redirect('admin')
            else:
                return redirect('dashboard')

        return HttpResponse("Falsche Zugangsdaten")

    return render(request, 'trashApp/login.html')

#A
def profil_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check

    uuid_value = request.session.get('uuid')
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    benutzer_element = root.xpath(f"benutzer[@id='{uuid_value}']")

    if not benutzer_element:
        return HttpResponse("Benutzer nicht gefunden")

    benutzer_element = benutzer_element[0]
    benutzer = {
        'benutzername': benutzer_element.findtext('benutzername'),
        'email': benutzer_element.findtext('email'),
        'passwort': benutzer_element.findtext('passwort')
    }

    return render(request, 'trashApp/profil.html', {'benutzer': benutzer})

#A
def profil_bearbeiten(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check

    if request.method == 'POST':
        uuid_value = request.session.get('uuid')
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
        benutzer_element = root.xpath(f"benutzer[@id='{uuid_value}']")

        if not benutzer_element:
            return HttpResponse("Benutzer nicht gefunden")

        benutzer_element = benutzer_element[0]
        benutzer_element.find('benutzername').text = request.POST['vorname']
        benutzer_element.find('email').text = request.POST['email']
        benutzer_element.find('passwort').text = request.POST['passwort']

        tree.write(XML_PATH, encoding='utf-8', xml_declaration=True, pretty_print=True)

    return redirect('profil')

def dashboard_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check
    return render(request, 'trashApp/dashboard.html')

def admin_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check
    return render(request, 'trashApp/admin.html')

def logout(request):
    request.session.flush()
    return redirect('login')

#A
def kontakt_email(request):
    if request.method == 'POST':
        betreff = request.POST.get('betreff')
        nachricht = request.POST.get('nachricht')
        empfaenger = ["chronoszeitbuchung@gmail.com"]
        email_senden(empfaenger, betreff, nachricht)
        return HttpResponse("""
            <script>
                alert("Nachricht wurde gesendet.");
                window.location.href = document.referrer;
            </script>
        """)
    return redirect('profil')

#A
def email_senden(emails, betreff, inhalt):
    adresse = "chronoszeitbuchung@gmail.com"
    passwort = "wmrh ayvh aprj vllx"

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(adresse, passwort)

    for email in emails:
        msg = EmailMessage()
        msg["From"] = adresse
        msg["To"] = email
        msg["Subject"] = betreff
        msg.set_content(inhalt)
        server.send_message(msg)
    server.quit()
# class EmailMessage(Message):
#     def __init__(self):
#         super().__init__()
#         self._headers = []  # Liste der Header-Felder (z. B. "From", "To", "Subject")
#         self._payload = None  # Der Inhalt der E-Mail
#         self._charset = "utf-8"  # Standard-Zeichensatz für den Inhalt

#     def set_content(self, content, subtype="plain", charset="utf-8"):
#         self._payload = content  # Speichert den Inhalt der Nachricht
#         self._charset = charset

#     def __setitem__(self, key, value):
#         self._headers.append((key, value))  # Fügt Header hinzu, z. B. "From", "To", "Subject"

# chronoszeitbuchung@gmail.com
# Name: Chronos
# Nachname: Zeitbuchung
# PW: ChronosDVM2023++
# Wiederherstellung: schambach_andre@teams.hs-ludwigsburg.de
# App: chronoszeitbuchung
# App-Passwort: wmrh ayvh aprj vllx
