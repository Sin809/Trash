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
import json

#A noch unklar
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings


#A
class Benutzer:
    def __init__(self, benutzername, email, passwort, rolle='user', status='aktiv'):
        self.id = str(uuid.uuid4())
        self.benutzername = benutzername
        self.email = email
        self.passwort = passwort
        self.rolle = rolle
        self.status = status

    def als_xml_speichern(self):
        user = ET.Element('benutzer', id=self.id)
        ET.SubElement(user, 'benutzername').text = self.benutzername
        ET.SubElement(user, 'email').text = self.email
        ET.SubElement(user, 'passwort').text = self.passwort
        ET.SubElement(user, 'rolle').text = self.rolle
        ET.SubElement(user, 'status').text = self.status
        return user

#Allgemeine Pfade für die XMls
benutzerXmlPfad = os.path.join(os.getcwd(), 'trashApp', 'static', 'db', 'benutzer.xml')
logbuchXmlPfad = os.path.join(os.getcwd(), 'trashApp', 'static', 'db', 'logbuch.xml')


#Hilfsfunktionen für die Verarbeitung der XML
#S    
def xmlStrukturierenBenutzer():
    parser = ET.XMLParser(remove_blank_text=True)
    return ET.parse(benutzerXmlPfad, parser)

#S
def xmlStrukturierenLogbuch():
    parser = ET.XMLParser(remove_blank_text=True)
    return ET.parse(logbuchXmlPfad, parser)

#A    
def lade_benutzer():
    if not os.path.exists(benutzerXmlPfad):
        return []
    tree = xmlStrukturierenBenutzer()
    root = tree.getroot()
    return root.xpath('//benutzer')

#Hilfsfunktion login checken
#A
def benutzer_ist_eingeloggt(request):
    if not request.session.get('uuid'):
        return redirect('login')
    return None


#Registrierung
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

        if not os.path.exists(benutzerXmlPfad):
            root = ET.Element('benutzerliste')
            tree = ET.ElementTree(root)
        else:
            tree = xmlStrukturierenBenutzer()
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
        tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return redirect('login')

    return render(request, 'trashApp/registrieren.html')


#Login
#A    
def login_html(request):
    if request.method == 'POST':
        benutzername = request.POST['benutzername']
        passwort = request.POST['passwort']

        if not os.path.exists(benutzerXmlPfad):
            return HttpResponse("""
                            <script>
                                alert("Keine Benutzer vorhanden");
                                window.history.back();
                            </script>
                            """)

        tree = xmlStrukturierenBenutzer()
        root = tree.getroot()

        benutzer = root.xpath(f"benutzer[benutzername='{benutzername}' and passwort='{passwort}']")

        if benutzer:
            status = benutzer[0].xpath('status/text()')[0]

            if status != "aktiv":
                return HttpResponse("""
                    <script>
                        alert("Ihr Benutzerkonto ist gesperrt.");
                        window.history.back();
                    </script>
                """)

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


#Profil
#A
def profil_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check: return check

    uuid_wert = request.session.get('uuid')
    tree = xmlStrukturierenBenutzer()
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
        tree = xmlStrukturierenBenutzer()
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

        tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)

    return redirect('profil')

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


#System und PI-Überprüfung
#S
def system_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check:
        return check
    
    benutzer_id = request.session.get('uuid')

    if not benutzer_id or not ist_admin(str(benutzer_id)):
        return HttpResponse("""
            <script>
                alert("Du bist kein Admin und hast somit keine Zugangsberechtigung für die Systemdaten.");
                window.history.back();
            </script>
        """)
    
    hostname = request.POST.get("hostname", "")
    benutzername = request.POST.get("benutzername", "")
    passwort = request.POST.get("passwort", "")
    port = int(request.POST.get("port", 22))

    rpi_online = checkRPiOnline(hostname, port)
    login_history = []

    if rpi_online and benutzername and passwort:
        login_history = readLoginHistory(hostname, port, benutzername, passwort)
        system_resources = get_system_resources(hostname, port, benutzername, passwort)
    else:
        system_resources = {}

    return render(request, 'trashApp/system.html', {
        "rpi_online": rpi_online,
        "login_history": login_history,
        "hostname": hostname,
        "port": port,
        "passwort": passwort,
        "benutzername": benutzername,
        "system_resources": system_resources,
    })

#S
def checkRPiOnline(hostname, port=22, timeout=1):
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except:
        return False
    
#S
def readLoginHistory(hostname, port, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=port, username=username, password=password, timeout=5)
        stdin, stdout, stderr = ssh.exec_command("last -n 10")
        history_raw = stdout.read().decode('utf-8')
        ssh.close()

        lines = history_raw.splitlines()
        login_history = []
        nummer = 1

        for line in lines:
            line = line.strip()
            if line and not line.startswith(("wtmp begins", "reboot", "shutdown")):
                login_history.append({
                    "nummer": nummer,
                    "text": line
                })
                nummer += 1

        return login_history

    except Exception as e:
        return [{"nummer": "-", "text": f"Fehler beim Lesen der Login-Historie: {e}"}]

#S
def parse_last_line_simple(line):
    return line.strip()

#S
def get_system_resources(host, port, user, password):
    commands = {
        "RAM": "free -h",
        "Laufzeit": "uptime -p",
        "Load Average": "cat /proc/loadavg",
        "GPU-Speicher (Pi)": "vcgencmd get_mem gpu",
        "Temperatur (Pi)": "vcgencmd measure_temp",
        "Spannung (Pi)": "vcgencmd measure_volts",
        "CPU Info": "lscpu",
        "CPU Details": "cat /proc/cpuinfo"
    }

    results = {}

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=user, password=password)

        for key, cmd in commands.items():
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if error:
                results[key] = f"Error: {error.strip()}"
            else:
                filtered_output = output.strip()

                if key == "CPU Details":
                    lines = filtered_output.splitlines()
                    filtered_lines = [line for line in lines if "Features" not in line]
                    filtered_output = "\n".join(filtered_lines)

                elif key == "CPU Info":
                    lines = filtered_output.splitlines()
                    filtered_lines = [line for line in lines if ("Vulnerability" not in line and "Flags" not in line)]
                    filtered_output = "\n".join(filtered_lines)

                results[key] = filtered_output

        ssh.close()
    except Exception as e:
        return {"error": str(e)}

    return results


#Dashboard
#S
from datetime import datetime

def dashboard_html(request):
    check = benutzer_ist_eingeloggt(request)
    if check:
        return check

    uuid_value = request.session.get('uuid')
    eintraege = []
    zaehler = {'Papier': 0, 'Plastik': 0, 'Restmüll': 0, 'Uneindeutig': 0}
    reset_zeitpunkte = {}

    if os.path.exists(logbuchXmlPfad):
        tree = xmlStrukturierenLogbuch()
        root = tree.getroot()

        benutzer_element = root.find(f"benutzer[@benutzer_id='{uuid_value}']")
        if benutzer_element is not None:
            # Lade Reset-Zeitpunkte
            reset_element = benutzer_element.find('reset')
            if reset_element is not None:
                for art in zaehler.keys():
                    zeit_text = reset_element.get(art.lower())
                    if zeit_text:
                        try:
                            reset_zeitpunkte[art] = datetime.strptime(zeit_text, "%d.%m.%Y %H:%M:%S")
                        except ValueError:
                            pass

            for eintrag in benutzer_element.findall('eintrag'):
                zeit = eintrag.findtext('zeit')
                art = eintrag.findtext('art')
                bild_url = eintrag.findtext('bild_url', default='Kein Bild gemacht')

                eintraege.append({'zeit': zeit, 'art': art, 'bild_url': bild_url})

                if art in zaehler:
                    try:
                        eintragszeit = datetime.strptime(zeit, "%d.%m.%Y %H:%M")
                        reset_zeit = reset_zeitpunkte.get(art)
                        if reset_zeit is None or eintragszeit > reset_zeit:
                            zaehler[art] += 1
                    except ValueError:
                        pass

    # Max 10 Einträge für 100 %
    fuellstaende = {
        art.lower(): min(round((count / 10) * 100), 100)
        for art, count in zaehler.items()
    }

    rpi_online = False
    if request.method == "POST":
        rpi_online = checkRPiOnline("sinanpi", 22)

    return render(request, 'trashApp/dashboard.html', {
        "logbuch_eintraege": eintraege,
        "fuellstaende": fuellstaende,
        "rpi_online": rpi_online,
    })


#S
def reset_fuellstand(request):
    if request.method != 'POST':
        return redirect('dashboard')

    art = request.POST.get('art')
    uuid_value = request.session.get('uuid')
    if not art or not uuid_value:
        return redirect('dashboard')

    if not os.path.exists(logbuchXmlPfad):
        return redirect('dashboard')

    try:
        tree = xmlStrukturierenLogbuch()
        root = tree.getroot()
        benutzer = root.find(f"benutzer[@benutzer_id='{uuid_value}']")
        if benutzer is None:
            return redirect('dashboard')

        # Finde oder erstelle ein "reset" Element, um Rücksetz-Zeitpunkt zu speichern
        reset_element = benutzer.find('reset')
        if reset_element is None:
            reset_element = ET.SubElement(benutzer, 'reset')

        # Setze Rücksetzzeit für die gegebene Müllart
        reset_element.set(art.lower(), datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

        tree.write(logbuchXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)

    except Exception as e:
        print(f"Fehler beim Zurücksetzen des Füllstands: {e}")

    return redirect('dashboard')

#S
def finde_benutzername(uuid):
    if not os.path.exists(benutzerXmlPfad):
        return None
    tree = xmlStrukturierenBenutzer()
    root = tree.getroot()
    benutzer = root.find(f"benutzer[@id='{uuid}']")
    if benutzer is not None:
        return benutzer.findtext('benutzername')
    return None

#S
def logbuchEintragHtml(request):
    if request.method == 'POST':
        art = request.POST.get('art')
        uuid_value = request.session.get('uuid')
        benutzername = finde_benutzername(uuid_value)

        if not os.path.exists(logbuchXmlPfad):
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

        tree.write(logbuchXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return redirect('dashboard')

    return redirect('dashboard')

"""
Bild soll angezeigt
Art muss von 0 Plastik auf nur Plastik geändert werden
Ändern-splate damit mit nem tabelle button art ändern und die datei auch umbenannt wird
"""

#S
def eintragLoeschen(request):
    if request.method == 'POST':
        logbucheintragloeschen = request.POST.get('loeschen')
        if not logbucheintragloeschen:
            print("Kein zu löschender Zeitstempel übergeben")
            return redirect('dashboard')

        if os.path.exists(logbuchXmlPfad):
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
                    tree.write(logbuchXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)
                    print("Eintrag gelöscht!")
                    gefunden = True
                    break

            if not gefunden:
                print("Eintrag mit diesem Zeitstempel nicht gefunden")

        return redirect('dashboard')

    return redirect('dashboard')

#Allgemiene Pfade für Bildordner
#S
BILDER_ORDNER_REL_XML = '/static/klassifikation'
BILDER_ORDNER_ABS = os.path.join(settings.BASE_DIR, 'trashApp', 'static', 'klassifikation')

#S
def finde_datei_rekursiv(start_ordner, dateiname):
    for root, dirs, files in os.walk(start_ordner):
        if dateiname in files:
            return os.path.join(root, dateiname)
    return None

#S
@csrf_exempt
def eintragArtAendern(request):
    if request.method == "POST":
        uuid_value = request.POST.get("uuid")
        alte_zeit = request.POST.get("zeit")
        neue_art = request.POST.get("neue_art")

        if not all([uuid_value, alte_zeit, neue_art]):
            return JsonResponse({"error": "Fehlende Daten"}, status=400)

        try:
            tree = ET.parse(logbuchXmlPfad)
            root = tree.getroot()
        except Exception as e:
            return JsonResponse({"error": f"XML konnte nicht geladen werden: {e}"}, status=500)

        benutzer = root.find(f"benutzer[@benutzer_id='{uuid_value}']")
        if benutzer is None:
            return JsonResponse({"error": "Benutzer nicht gefunden"}, status=404)

        gefunden = False
        for eintrag in benutzer.findall("eintrag"):
            if eintrag.findtext("zeit") == alte_zeit:
                eintrag.find("art").text = neue_art

                bild_url = eintrag.findtext("bild_url")
                if bild_url:
                    alter_dateiname = os.path.basename(bild_url)

                    # Dateiname anpassen
                    name, ext = os.path.splitext(alter_dateiname)
                    teile = name.split('_')
                    if len(teile) >= 3:
                        teile[-1] = neue_art
                        neuer_dateiname = "_".join(teile) + ext
                    else:
                        neuer_dateiname = f"{alte_zeit}_{neue_art}{ext}"

                    # Rekursive Suche nach der Datei
                    alter_pfad = finde_datei_rekursiv(BILDER_ORDNER_ABS, alter_dateiname)
                    if not alter_pfad:
                        return JsonResponse({"error": "Bilddatei nicht gefunden"}, status=404)

                    ordner_von_alter_pfad = os.path.dirname(alter_pfad)
                    neuer_pfad = os.path.join(ordner_von_alter_pfad, neuer_dateiname)

                    try:
                        os.rename(alter_pfad, neuer_pfad)

                        # Relativer Pfad im XML (inklusive Unterordner)
                        rel_ordner = os.path.relpath(ordner_von_alter_pfad, BILDER_ORDNER_ABS).replace(os.sep, '/')
                        if rel_ordner == '.':
                            rel_ordner = ''  # direkt im Hauptordner
                        else:
                            rel_ordner = '/' + rel_ordner

                        neuer_rel_pfad = f"{BILDER_ORDNER_REL_XML}{rel_ordner}/{neuer_dateiname}"
                        eintrag.find("bild_url").text = neuer_rel_pfad
                    except Exception as e:
                        return JsonResponse({"error": f"Fehler beim Umbenennen der Bilddatei: {e}"}, status=500)

                gefunden = True
                break

        if not gefunden:
            return JsonResponse({"error": "Eintrag nicht gefunden"}, status=404)

        try:
            tree.write(logbuchXmlPfad, encoding="utf-8", xml_declaration=True, pretty_print=True)
        except Exception as e:
            return JsonResponse({"error": f"XML konnte nicht gespeichert werden: {e}"}, status=500)

        return redirect('/tr/dashboard')

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)


#Admin
#S
def admin_html(request):
    benutzer_id = request.session.get('uuid')

    if not benutzer_id or not ist_admin(str(benutzer_id)):
        return HttpResponse("""
            <script>
                alert("Du bist kein Admin und hast somit keine Zugangsberechtigung für die Admin-Verwaltung.");
                window.history.back();
            </script>
        """)

    # Benutzerdaten laden
    benutzer_liste = []
    with open(benutzerXmlPfad, 'r', encoding='utf-8') as f:
        tree = ET.parse(f)
        root = tree.getroot()

        for benutzer in root.findall('benutzer'):
            benutzer_liste.append({
                'id': benutzer.get('id'),
                'benutzername': benutzer.findtext('benutzername'),
                'email': benutzer.findtext('email'),
                'rolle': benutzer.findtext('rolle'),
                'status': benutzer.findtext('status'),
            })

    return render(request, 'trashApp/admin.html', {'benutzer_liste': benutzer_liste})

#S
def ist_admin(benutzer_id):
    try:
        tree = ET.parse(benutzerXmlPfad)
        root = tree.getroot()

        for benutzer in root.findall('benutzer'):
            if benutzer.get('id') == benutzer_id:
                return benutzer.findtext('rolle') == 'admin'
    except:
        return False

    return False

#S
def rolle_hochsetzen(request, benutzer_id):
    tree = ET.parse(benutzerXmlPfad)
    root = tree.getroot()

    for benutzer in root.findall('benutzer'):
        if benutzer.get('id') == str(benutzer_id):
            rolle_element = benutzer.find('rolle')
            if rolle_element is not None:
                rolle_element.text = 'admin'
                tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True)
                break
    return redirect('admin')

#S
def rolle_runtersetzen(request, benutzer_id):
    tree = ET.parse(benutzerXmlPfad)
    root = tree.getroot()

    for benutzer in root.findall('benutzer'):
        if benutzer.get('id') == str(benutzer_id):
            rolle_element = benutzer.find('rolle')
            if rolle_element is not None:
                rolle_element.text = 'user'
                tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True)
                break
    return redirect('admin')

#S
def sperren_benutzer(request, benutzer_id):
    login_check = benutzer_ist_eingeloggt(request)
    if login_check:
        return login_check

    tree = xmlStrukturierenBenutzer()
    root = tree.getroot()

    benutzer_element = root.find(f"benutzer[@id='{benutzer_id}']")
    if benutzer_element is not None:
        status_element = benutzer_element.find('status')
        if status_element is None:
            status_element = ET.SubElement(benutzer_element, 'status')
        status_element.text = "gesperrt"

        tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return redirect('admin')

    return HttpResponse("""
        <script>
            alert("Benutzer nicht gefunden.");
            window.history.back();
        </script>
    """, status=400)

#S
def entsperren_benutzer(request, benutzer_id):
    login_check = benutzer_ist_eingeloggt(request)
    if login_check:
        return login_check

    tree = xmlStrukturierenBenutzer()
    root = tree.getroot()

    benutzer_element = root.find(f"benutzer[@id='{benutzer_id}']")
    if benutzer_element is not None:
        status_element = benutzer_element.find('status')
        if status_element is None:
            status_element = ET.SubElement(benutzer_element, 'status')
        status_element.text = "aktiv"

        tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)
        return redirect('admin')

    return HttpResponse("""
        <script>
            alert("Benutzer nicht gefunden.");
            window.history.back();
        </script>
    """, status=400)

#S
def update_benutzer_status(benutzer_id, neuer_status):
    tree = ET.parse(benutzerXmlPfad)
    root = tree.getroot()

    for benutzer in root.findall('benutzer'):
        if benutzer.get('id') == str(benutzer_id):
            status_el = benutzer.find('status')
            if status_el is None:
                status_el = ET.SubElement(benutzer, 'status')
            status_el.text = neuer_status
            break

    tree.write(benutzerXmlPfad, encoding='utf-8', xml_declaration=True, pretty_print=True)

    return redirect('admin')


#Logout
#S
def logout(request):
    request.session.flush()
    return redirect('login')


#Bilder vom Pi hochladen/bearbeiten
#A
UPLOAD_DIR = os.path.join(settings.BASE_DIR, "trashApp", "static", "uploadbilder")
os.makedirs(UPLOAD_DIR, exist_ok=True)

#A
@csrf_exempt
def api_upload(request):
    if request.method == "POST":
        bild = request.FILES.get("bild")
        label = request.POST.get("label", "Unbekannt")
        datum = request.POST.get("datum")
        uhrzeit = request.POST.get("uhrzeit")
        wahrscheinlichkeit = request.POST.get("wahrscheinlichkeit", "0")
        pi_id = request.POST.get("pi_id")

        if not all([bild, datum, uhrzeit, pi_id]):
            return JsonResponse({"error": "Fehlende Felder"}, status=400)

    
        pi_benutzer = os.path.join(settings.BASE_DIR, 'trashApp', 'static', 'db', 'pi_user.json')
        if not os.path.exists(pi_benutzer):
            return JsonResponse({"error": "Keine Pi-Zuordnungsdatei gefunden"}, status=500)

        with open(pi_benutzer, "r") as f:
            pi_mapping = json.load(f)

        uuid_value = pi_mapping.get(pi_id)
        if not uuid_value:
            return JsonResponse({"error": "Unbekannte Pi-ID"}, status=403)

        benutzer_baum = xmlStrukturierenBenutzer()
        benutzer_root = benutzer_baum.getroot()
        benutzer_element = benutzer_root.find(f"benutzer[@id='{uuid_value}']")
        if benutzer_element is None:
            return JsonResponse({"error": "Ungültige Benutzer-UUID"}, status=403)

        benutzername = benutzer_element.findtext("benutzername")

        speicherpfad = os.path.join(settings.BASE_DIR, "trashApp", "static", "klassifikation", benutzername)
        os.makedirs(speicherpfad, exist_ok=True)

        dateiname = f"{datum.replace('-', '')}_{uhrzeit.replace(':', '')}_{label}_{wahrscheinlichkeit}.jpg"
        zielpfad = os.path.join(speicherpfad, dateiname)

        with open(zielpfad, "wb") as datei:
            datei.write(bild.read())

        logbuch_baum = xmlStrukturierenLogbuch() if os.path.exists(logbuchXmlPfad) else ET.ElementTree(ET.Element("logbuch"))
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

        logbuch_baum.write(logbuchXmlPfad, encoding="utf-8", xml_declaration=True, pretty_print=True)

        return JsonResponse({"status": "erfolgreich", "filename": dateiname})

    return JsonResponse({"error": "Nur POST erlaubt"}, status=405)



"""

BILDER_ORDNER = os.path.join(settings.BASE_DIR, "trashApp", "static", "klassifikation", "Ben")

def test_view(request):
    bilder = [f for f in os.listdir(BILDER_ORDNER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return render(request, 'trashApp/test.html', {'bilder': bilder})


@csrf_exempt  # Nur zum Testen, im Produktivbetrieb CSRF-Schutz nutzen!
def aendere_art(request):
    if request.method == "POST":
        alter_dateiname = request.POST.get("bildname")
        neue_art = request.POST.get("neue_art")

        if not alter_dateiname or not neue_art:
            return redirect('test')

        # Datei umbennen: z.B. 20250601_115859_Papier.jpg -> 20250601_115859_Plastik.jpg
        name, ext = os.path.splitext(alter_dateiname)
        teile = name.split('_')
        if len(teile) >= 3:
            teile[-1] = neue_art
            neuer_name = "_".join(teile) + ext
        else:
            return redirect('test')

        alter_pfad = os.path.join(BILDER_ORDNER, alter_dateiname)
        neuer_pfad = os.path.join(BILDER_ORDNER, neuer_name)

        if os.path.exists(neuer_pfad):
            # Datei mit neuem Namen existiert schon
            return redirect('test')

        try:
            os.rename(alter_pfad, neuer_pfad)
        except Exception as e:
            print("Fehler beim Umbenennen:", e)

        return redirect('test')

    return redirect('test')
"""


#Flyer
#S
def flyer_html(request):
    return render(request, 'trashApp/flyer.html')