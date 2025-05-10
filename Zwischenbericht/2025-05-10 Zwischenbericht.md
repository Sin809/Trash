# Zwischenbericht – Projekt "Trashy"  
**Stand:** 11.05.2025  
**Team:** Marius Mattes, Felix Lang, Sinan Licina, Andre Schambach

---

## 🖥️ Frontend

### Aktueller Stand:


### Nächste Schritte:


---

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

### Nächste Schritte:

---

## 📋 Projektmanagement

### Aktueller Stand:

### Nächste Schritte:

---

**Bemerkungen / Offene Punkte:**

![Testbild](Bilder/Test.png)
