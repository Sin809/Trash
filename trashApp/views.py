import os
import uuid
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect
from django.http import HttpResponse

#A
XML_PATH = os.path.join(os.getcwd(), 'trashApp', 'static', 'db', 'benutzer.xml')
class Benutzer:
    def __init__(self, benutzername, email, passwort, rolle='user'):
        self.id = str(uuid.uuid4())
        self.benutzername = benutzername
        self.email = email
        self.passwort = passwort
        self.rolle = rolle

    def als_xml_speichern(self):
        user = ET.Element('benutzer', attrib={'id': self.id})
        ET.SubElement(user, 'benutzername').text = self.benutzername
        ET.SubElement(user, 'email').text = self.email
        ET.SubElement(user, 'passwort').text = self.passwort
        ET.SubElement(user, 'rolle').text = self.rolle
        return user
#A    
def lade_benutzer():
    if not os.path.exists(XML_PATH):
        return [] #leere liste, damit login_html etwas zum druchsuchen hat, falls es noch keine benutzer geben sollte
    tree = ET.parse(XML_PATH)
    root = tree.getroot()
    return root.findall('benutzer')

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

        for benutzer in root.findall('benutzer'):
            if benutzer.find('benutzername').text == benutzername:
                return HttpResponse("Benutzername bereits registriert")

        neuer_benutzer = Benutzer(benutzername, email, passwort)#neue user klasse anlegen
        root.append(neuer_benutzer.als_xml_speichern())# klasse als xml speichern
        tree.write(XML_PATH, encoding='utf-8', xml_declaration=True)
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

        benutzerliste = lade_benutzer()

        for benutzer in benutzerliste:
            if benutzer.find('benutzername').text == benutzername and benutzer.find('passwort').text == passwort:
                request.session['uuid'] = benutzer.attrib['id']
                rolle = benutzer.find('rolle').text
                if rolle == 'admin':
                    return redirect('admin')
                else:
                    return redirect('dashboard')

        return HttpResponse("Falsche Zugangsdaten")

    return render(request, 'trashApp/login.html')


def profil_html(request):
    return render(request, 'trashApp/profil.html')

def profil_bearbeiten(request):
    return render(request, 'trashApp/profil.html')

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

def kontakt_email(request):
    return HttpResponse("""
                            <script>
                                alert("Noch nichts.");
                                window.history.back();
                            </script>
                        """, status=400)