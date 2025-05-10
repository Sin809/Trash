# Zwischenbericht – Projekt "Trashy"  
**Stand:** 11.05.2025  
**Team:** Marius Mattes, Felix Lang, Sinan Licina, Andre Schambach


## 🖥️ Frontend

### Aktueller Stand:

Modularer Aufbau mit Django-Templates:
Durch die Verwendung von {% include %}-Anweisungen für die Navigationsleiste und das Banner wird der HTML-Code übersichtlich und wiederverwendbar gestaltet.

Interaktive Benutzer- und Mülleimerverwaltung:
Admins sollen Benutzer einsehen und per Klick sperren können. Ebenso soll man Mülleimer hinzufügen oder entfernen können. Diese Funktionen sind in Tabellen mit interaktiven Buttons eingebunden.
![Admin-Verwaltungs-Seite](https://i.postimg.cc/gk9x5j9J/Screenshot-2025-05-10-105711.png)

Füllstandsanzeige mit Fortschrittsbalken:
Die Füllstände der Mülleimer soll grafisch durch Balken dargestellt werden, die den aktuellen Prozentsatz visualisieren. Eine Dropdown-Auswahl erlaubt die Filterung nach Zeitraum (z. B. heute, diese Woche).

Logbuch und Systemstatus in Echtzeit:
Ein Logbuch soll die letzten Sortiervorgänge mit Zeitstempel zeigen. Der Systemstatus soll informieren, ob der Raspberry Pi online ist.
![Dashboard-Seite](https://i.postimg.cc/t4bQLQCW/Screenshot-2025-05-10-110031.png)

Profil- und Kontaktbereich:
Benutzer können ihre Profildaten wie Name, E-Mail und Passwort bearbeiten. Über ein integriertes Kontaktformular können sie Nachrichten direkt an die Developer senden, die per E-Mail weitergeleitet werden.
![Profil-Seite](https://i.postimg.cc/1tsKQBVW/Screenshot-2025-05-10-110239.png)


### Nächste Schritte:

Live-Feed der Müllsortierung:
Ein Echtzeit-Stream der Kamera soll zukünftig im Frontend eingebettet werden, um den Sortiervorgang live mitzuverfolgen. So können Benutzer direkt beobachten, wie der Müll erkannt und zugeordnet wird – integriert auf der Dashboard-Seite.

Fehlermeldungen und Erfolgshinweise anzeigen:
Rückmeldungen an den Benutzer bei erfolgreichen Änderungen oder Eingabefehlern sollen deutlicher gemacht werden. Dies soll durch Pop-ups erfolgen, die visuelle Hinweise zur Fehlerbehebung oder Erfolgsmeldungen liefern.

## 🛠️ Backend

### Aktueller Stand:
Objektorientierte Benutzerverwaltung:
Benutzer werden nun über eine eigene Benutzer-Klasse erzeugt, was die Verwaltung, Erweiterung und Strukturierung der Benutzerlogik stark vereinfacht.

Verwendung von lxml und XPath:
Statt der Standardbibliothek xml.etree.ElementTree wird nun die leistungsfähigere Bibliothek lxml verwendet. Dadurch können präzise und performante XPath-Abfragen durchgeführt werden, z. B. zur Identifikation oder Bearbeitung eines Benutzers über benutzer[@id='...'].

Datenhaltung in XML statt JSON:
Die Benutzerdaten werden nicht mehr in JSON-Dateien gespeichert, sondern in einer strukturierteren XML-Datei (benutzer.xml). Dies erleichtert die direkte Verarbeitung mit XPath und unterstützt komplexere hierarchische Datenmodelle.

UUID statt eigener Zähler für IDs:
Jeder Benutzer erhält eine eindeutige ID (UUID), die automatisch beim Anlegen vergeben wird. Dadurch entfällt die Notwendigkeit, eigene ID-Zähler zu pflegen, was besonders bei parallelem Zugriff von Vorteil ist.

Session-Verwaltung mit UUID:
Nach dem Login wird die UUID des Benutzers in der Session gespeichert. Alle geschützten Views überprüfen den Zugriff über diese ID.

Funktionierende Benutzerbearbeitung:
Benutzer können ihre Profildaten direkt im System ändern. Die Änderungen werden in der XML-Datei gespeichert und stehen sofort zur Verfügung.

Kontaktformular mit E-Mail-Anbindung:
Benutzer können über ein Formular auf der Profilseite direkt eine Nachricht an die Projektverantwortlichen senden. Die Nachricht wird automatisch per E-Mail an eine zentrale Adresse weitergeleitet.

### Nächste Schritte:
GPIO-Anbindung unter Apache lösen:
Aktuell läuft das RPi.GPIO-Modul nicht zuverlässig unter Apache auf dem Pi 5. Eine temporäre Lösung über subprocess ist im Einsatz, soll aber ggf. durch eine einfachere Alternative von Tim Hauser ersetzt werden.

Kommunikation zwischen Webserver und Hardware aufbauen:
Ziel ist eine stabile Verbindung zwischen Weboberfläche, Django-Backend und den GPIO-gesteuerten Hardwarekomponenten, um Benutzeraktionen zuverlässig weiterzuleiten.

---

## 🔌 Hardware

### Aktueller Stand:
Herr Lang hatte beim Projekt verschiedene Aufgaben. Die zentralste Aufgabe, welche er zugeteilt bekommen hatte, war die Hardware Beschaffung. Für diese informierte er sich vorab über verschiedenste Bauteile, welche für unser Projekt von Relevanz sein könnten. Wir entschieden uns Letzten Endes für eine Erkennung mithilfe von Kameras in Kombination mit „Computer-Vision“, da anderweitige Sensorik nicht realistisch nutzbar war oder finanziell zu belastend gewesen wäre.
Vor der Hardwarebeschaffung entwarf er eine grobe Skizze über den Aufbau des Konstrukts. Diese wurde im Anschluss mit den Gedanken aller Beteiligten mehrfach überarbeitet, sodass die Konstruktion stark vereinfacht werden konnte und die Funktionalität durch simple Anpassungen verbessert wurde. Ursprünglich war ein System angedacht, welches aus mehreren Fließbändern bestehen sollte und mithilfe von Schranken die Sortierung durchführen sollte (Siehe Abb.1).
![Skizze](https://i.postimg.cc/jj1NVymB/Screenshot-20250110-135454-Infinite-Painter.jpg)

Diese Konstruktion wurde verworfen und verbessert, da die Sorge bestand, dass die Schranken nicht ausreichen, um die Abfälle den jeweiligen Fließbändern zuzuweisen. Stattdessen wurde das Konzept mit Kolben verbessert. Diese sollten die Befördernisse direkt auf das jeweilige weitere Fließband schieben, wie in der folgenden Abbildung zu sehen.
![Neuer Entwurf](https://i.postimg.cc/Y9j50BXh/Medien.png)
 
Dies sollte mithilfe von Elektromotoren geschehen, was jedoch das Risiko bot, dass zwischen dem Fließband und dem Kolben die Befördernisse stecken bleiben. Aus diesem Grund überlegten wir eine Option ohne Kolben und Schranken. Wir reduzierten das Konstrukt auf die nötigsten Teile und hatten nurnoch zwei Fließbänder, wobei auf dem Ersten der Abfall erkannt wird und im Anschluss auf das zweite Fließband fällt. Das zweite Fließband hatte noch die Sonderfunktion mithilfe eines Servo-Motors sich auszurichten, um in verschiedene Behälter zu zeigen, sodass die Fördermittel von alleine in die jeweilige Tonne fielen.
Zusätzlich dazu wollten wir die Fließbänder mit den Motoren verbinden und benötigten eine Art Konstruktion hierfür. Herr Lang hatte Zugriff zu einem 3D-Drucker und einem AutoCAD Programm, womit er erste Modelle für die Fließbänder erstellte. Um diese an unsere Komponenten anzupassen, wurden jedoch die Hardware Komponenten benötigt. Auch die Beschaffung führte Herr Lang durch. Nachdem wir unseren Bedarf festgestellt hatten durch unsere Überlegungen stellte er eine Materialliste zusammen. Beim Eintreffen der Komponenten konnten diese erfolgreich ausgemessen werden und mithilfe der Motoren eine Halterung für die Achsen der Fließbänder modelliert werden. Diese wurden jedoch noch nicht ausgedruckt.
![Modell](https://i.postimg.cc/RVWLDbjv/Bild.png)

### Nächste Schritte:

---

## 📋 Projektmanagement

### Aktueller Stand:

### Nächste Schritte:

---

**Bemerkungen / Offene Punkte:**

![Testbild](Test.png)
