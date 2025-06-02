import os
import uuid
import smtplib
from lxml import etree as ET #alternative zu "xml.etree.ElementTree"
from email.message import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime

#A noch unklar
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings


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

#S    
def xmlStrukturieren():
    parser = ET.XMLParser(remove_blank_text=True)
    return ET.parse(XML_PATH, parser)

#A    
def lade_benutzer():
    if not os.path.exists(XML_PATH):
        return []
    tree = xmlStrukturieren()
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
            return HttpResponse("""
                            <script>
                                alert("Passwörter stimmen nicht überein");
                                window.history.back();
                            </script>
                            """)

        if not os.path.exists(XML_PATH):
            root = ET.Element('benutzerliste')
            tree = ET.ElementTree(root)
        else:
            tree = xmlStrukturieren()
            root = tree.getroot()

        if root.xpath(f"benutzer[benutzername='{benutzername}' or email='{email}']"):
            return HttpResponse("""
                            <script>
                                alert("Benutzername oder E-Mail bereits registriert");
                                window.history.back();
                            </script>
                            """)
        
        neuer_benutzer = Benutzer(benutzername, email, passwort) #neue user klasse anlegen
        root.append(neuer_benutzer.als_xml_speichern())  #klasse als xml speichern
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
            return HttpResponse("""
                            <script>
                                alert("Keine Benutzer vorhanden");
                                window.history.back();
                            </script>
                            """)

        tree = xmlStrukturieren()
        root = tree.getroot()

        benutzer = root.xpath(f"benutzer[benutzername='{benutzername}' and passwort='{passwort}']")

        if benutzer:
            uuid = benutzer[0].xpath('@id')[0] #xpath abfragen geben immer listen als antwort, deswegen [0]
            rolle = benutzer[0].xpath('rolle/text()')[0] 

            request.session['uuid'] = uuid
            if rolle == 'admin':
                return redirect('admin')
            else:
                return redirect('dashboard')

        return HttpResponse("""
                <script>
                    alert("Falsche Zugangsdaten");
                    window.history.back();
                </script>
                """)

    return render(request, 'trashApp/login.html')

#A
def profil_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check

    uuid_wert = request.session.get('uuid')
    tree = xmlStrukturieren()
    root = tree.getroot()
    benutzer_element = root.xpath(f"benutzer[@id='{uuid_wert}']")

    if not benutzer_element:
        return HttpResponse("""
                            <script>
                                alert("Benutzer nicht gefunden");
                                window.history.back();
                            </script>
                            """)

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
        tree = xmlStrukturieren()
        root = tree.getroot()
        benutzer_element = root.xpath(f"benutzer[@id='{uuid_value}']")

        if not benutzer_element:
            return HttpResponse("""
                            <script>
                                alert("Benutzer nicht gefunden");
                                window.history.back();
                            </script>
                            """)

        benutzer_element = benutzer_element[0]
        benutzer_element.find('benutzername').text = request.POST['vorname']
        benutzer_element.find('email').text = request.POST['email']
        benutzer_element.find('passwort').text = request.POST['passwort']

        tree.write(XML_PATH, encoding='utf-8', xml_declaration=True, pretty_print=True)

    return redirect('profil')

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
                eintraege.append({'zeit': zeit, 'art': art})
                if art in zaehler:
                    zaehler[art] += 1

    # Füllstände max 10
    fuellstaende = {}
    for art, count in zaehler.items():
        prozent = min(round((count / 10) * 100), 100)
        fuellstaende[art.lower()] = prozent

    return render(request, 'trashApp/dashboard.html', {
        'logbuch_eintraege': eintraege,
        'fuellstaende': fuellstaende
    })

#S
BENUTZER_XML_PATH = os.path.join(settings.BASE_DIR, "trashApp", "static", "db", "benutzer.xml")
def xmlStrukturierenBenutzer():
    parser = ET.XMLParser(remove_blank_text=True)
    return ET.parse(BENUTZER_XML_PATH, parser)

#S
def finde_benutzername(uuid):
    if not os.path.exists(BENUTZER_XML_PATH):
        return None
    tree = xmlStrukturierenBenutzer()
    root = tree.getroot()
    benutzer = root.find(f"benutzer[@id='{uuid}']")
    if benutzer is not None:
        return benutzer.findtext('benutzername')
    return None

LOGBUCH_XML_PATH = os.path.join(os.getcwd(), 'trashApp', 'static', 'db', 'logbuch.xml')

def xmlStrukturierenLogbuch():
    parser = ET.XMLParser(remove_blank_text=True)
    return ET.parse(LOGBUCH_XML_PATH, parser)

#S
def logbuchEintragHtml(request):
    if request.method == 'POST':
        art = request.POST.get('art')
        uuid_value = request.session.get('uuid')
        benutzername = finde_benutzername(uuid_value)

        if not os.path.exists(LOGBUCH_XML_PATH):
            root = ET.Element('logbuch')
            tree = ET.ElementTree(root)
        else:
            tree = xmlStrukturierenLogbuch()
            root = tree.getroot()

        benutzer_element = root.find(f"benutzer[@benutzer_id='{uuid_value}']")
        if benutzer_element is None:
            benutzer_element = ET.SubElement(root, 'benutzer', benutzer_id=uuid_value)

        zeitstempel = datetime.now().strftime("%d.%m.%Y %H:%M")
        eintrag = ET.SubElement(benutzer_element, 'eintrag')
        ET.SubElement(eintrag, 'zeit').text = zeitstempel
        ET.SubElement(eintrag, 'art').text = art
        ET.SubElement(eintrag, 'bild_url').text = "Kein Bild gemacht"
        ET.SubElement(eintrag, 'benutzername').text = benutzername

        tree.write(LOGBUCH_XML_PATH, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return redirect('dashboard')

    return redirect('dashboard')

#S
def eintragLoeschen(request):
    if request.method == 'POST':
        logbucheintragloeschen = request.POST.get('loeschen')
        if not logbucheintragloeschen:
            print("Kein zu löschender Zeitstempel übergeben")
            return redirect('dashboard')

        if os.path.exists(LOGBUCH_XML_PATH):
            tree = xmlStrukturierenLogbuch()
            root = tree.getroot()

            uuid_value = request.session.get('uuid')
            print(f"UUID aus Session: {uuid_value}")

            benutzer_element = root.find(f"benutzer[@benutzer_id='{uuid_value}']")
            if benutzer_element is None:
                print("Benutzer mit dieser UUID nicht gefunden")
                return redirect('dashboard')

            gefunden = False
            for eintrag in benutzer_element.findall('eintrag'):
                zeit_text = eintrag.findtext('zeit').strip()
                print(f"Prüfe Eintrag mit Zeit: {zeit_text}")
                if zeit_text == logbucheintragloeschen.strip():
                    benutzer_element.remove(eintrag)
                    tree.write(LOGBUCH_XML_PATH, encoding='utf-8', xml_declaration=True, pretty_print=True)
                    print("Eintrag gelöscht!")
                    gefunden = True
                    break

            if not gefunden:
                print("Eintrag mit diesem Zeitstempel nicht gefunden")

        return redirect('dashboard')

    return redirect('dashboard')


#S
def admin_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check
    return render(request, 'trashApp/admin.html')

#S
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

#A
UPLOAD_DIR = os.path.join(settings.BASE_DIR, "trashApp", "static", "uploadbilder")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@csrf_exempt
def api_upload(request):
    if request.method == "POST":
        bild = request.FILES.get("bild")
        label = request.POST.get("label", "Unbekannt")
        datum = request.POST.get("datum", None)
        uhrzeit = request.POST.get("uhrzeit", None)
        uuid_value = request.POST.get("uuid", None)

        if not all([bild, datum, uhrzeit, uuid_value]):
            return JsonResponse({"error": "Fehlende Felder"}, status=400)

        benutzer_baum = xmlStrukturierenBenutzer()
        benutzer_root = benutzer_baum.getroot()
        benutzer_element = benutzer_root.find(f"benutzer[@id='{uuid_value}']")
        if benutzer_element is None:
            return JsonResponse({"error": "Ungültige UUID"}, status=403)

        benutzername = benutzer_element.findtext("benutzername")

        speicherpfad = os.path.join(settings.BASE_DIR, "trashApp", "static", "klassifikation", benutzername)
        os.makedirs(speicherpfad, exist_ok=True)

        dateiname = f"{datum.replace('-', '')}_{uhrzeit.replace(':', '')}_{label}.jpg"
        zielpfad = os.path.join(speicherpfad, dateiname)

        with open(zielpfad, "wb") as datei:
            datei.write(bild.read())

        logbuch_baum = xmlStrukturierenLogbuch() if os.path.exists(LOGBUCH_XML_PATH) else ET.ElementTree(ET.Element("logbuch"))
        logbuch_root = logbuch_baum.getroot()
        benutzer_log = logbuch_root.find(f"benutzer[@benutzer_id='{uuid_value}']")
        if benutzer_log is None:
            benutzer_log = ET.SubElement(logbuch_root, 'benutzer', benutzer_id=uuid_value)

        url = f"/static/klassifikation/{benutzername}/{dateiname}"
        eintrag = ET.SubElement(benutzer_log, "eintrag")
        ET.SubElement(eintrag, "zeit").text = f"{datum.replace('-', '.')} {uhrzeit}"
        ET.SubElement(eintrag, "art").text = label
        ET.SubElement(eintrag, "bild_url").text = url
        ET.SubElement(eintrag, "benutzername").text = benutzername

        logbuch_baum.write(LOGBUCH_XML_PATH, encoding="utf-8", xml_declaration=True, pretty_print=True)

        return JsonResponse({"status": "erfolgreich", "filename": dateiname})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)



