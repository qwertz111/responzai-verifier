# Arbeitsanweisung: responzai Multi-Agent Verification System

## Vollständige Umsetzungsanleitung für Claude Code

**Projekt:** responzai Multi-Agent Verification & Improvement System
**Version:** 1.0
**Datum:** März 2026
**Erstellt für:** Umsetzung mit Claude Code (Mischform: autonom mit Rückfragen bei wichtigen Entscheidungen)

---

## Wichtige Regeln für dieses Dokument

**Sprache:** Klar und einfach wie für ein Kind ab 7, aber inhaltlich für Erwachsene. Kurze Sätze. Alltägliche Wörter. Wenn ein Fachbegriff nötig ist, wird er sofort erklärt. Keine Gedankenstriche. Keine abgenutzten Metaphern. Keine pseudokreativen Sprachbilder. Lieber ein Satz mehr als ein unverständlicher Satz.

**Didaktik:** Bei jedem Schritt wird erklärt: Was machen wir? Wie machen wir es? Warum machen wir es so? Das Ziel ist, dass jemand ohne tiefe Programmierkenntnisse jeden Schritt nachvollziehen kann.

**Oberflächen:** Alle Plattformen (Hetzner, GitHub, n8n, Cloudflare) werden mit ihren deutschen Menübezeichnungen referenziert.

**Agenten:** Durchgängig werden die menschlichen Namen verwendet. Das technische Kürzel steht in Klammern beim ersten Auftreten.

---

## Inhaltsverzeichnis

1. Was ist responzai?
2. Gesamtarchitektur: Das große Bild
3. Die acht Agenten im Detail
4. Infrastruktur aufsetzen (Server, Docker, Datenbank)
5. Repository-Struktur anlegen
6. Wissensbasis aufbauen (responzai-knowledge)
7. Dokument-Upload: Jedes Format prüfen
8. Prüfteam umsetzen (Simon, Vera, Conrad, Sven, Pia)
9. Verbesserungsteam umsetzen (Lena, David, Uma)
10. Pipeline-Orchestrierung mit LangGraph
11. Automatisierung mit n8n
12. Integration mit responzai.eu
13. Skills für die Agenten
14. Stilguide für David (DRAFT)
15. Anhang: Konfigurationsdateien und Referenzen

---

## 1. Was ist responzai?

responzai ist eine Marke für verlässlichen KI-Einsatz in Unternehmen. Die Kernthemen sind der EU AI Act, KI-Governance und KI-Kompetenz (Artikel 4 des EU AI Act).

**Bestehende Produkte und Formate:**

- **EVIDENCE:** Eine App zur Dokumentation des rechtskonformen KI-Einsatzes in HR-Prozessen.
- **GUIDES:** Ein KI-Governance-Framework für Unternehmen. Das sind Word-Dokument-Vorlagen, die Unternehmen durch den Prozess führen.
- **"KI & Kopf-Arbeit":** Ein wöchentlicher LinkedIn-Newsletter.
- **Website:** responzai.eu

**Zielgruppe:** HR-Verantwortliche, Compliance-Teams, Geschäftsführung und Berater im KI- und Regulierungsumfeld.

---

## 2. Gesamtarchitektur: Das große Bild

### 2.1 Was das System tut

Das System prüft Texte automatisch auf Richtigkeit, Aktualität und Konsistenz. Und es verbessert sie. Es besteht aus acht spezialisierten KI-Agenten, die in einer festen Reihenfolge arbeiten. Jeder Agent hat genau eine Aufgabe.

Das Besondere: Die Agenten kontrollieren sich gegenseitig. Nicht ein einzelnes KI-Modell macht alles allein (und kann dabei halluzinieren). Stattdessen gibt es eine Kette von Prüfinstanzen mit einer eingebauten Gegenprüfung.

### 2.2 Zwei Teams, acht Agenten

Das System besteht aus zwei Teams:

**Das Prüfteam** findet Probleme:

- **Simon (SCOUT):** Findet jede Behauptung in einem Text.
- **Vera (VERIFY):** Prüft jede Behauptung gegen Originalquellen.
- **Conrad (CONTRA):** Versucht aktiv, die Ergebnisse zu widerlegen.
- **Sven (SYNC):** Findet Widersprüche zwischen verschiedenen Texten.
- **Pia (PULSE):** Erkennt veraltete Informationen.

**Das Verbesserungsteam** löst die Probleme:

- **Lena (LEGAL):** Aktualisiert rechtliche Verweise mit Quellennachweis.
- **David (DRAFT):** Macht Texte verständlich und lesbar.
- **Uma (UX):** Macht Dokumente nutzerfreundlich.

### 2.3 Der Datenfluss

So fließen die Daten durch das System:

```
EINGABE (drei Wege):
1. URL eingeben         → Website crawlen → Text
2. Text direkt eingeben → Text
3. Datei hochladen      → Format erkennen → Parser → Text

PRÜFPIPELINE:
Text → Simon (SCOUT) → Claim-Datenbank → Vera (VERIFY)
    → Konfidenz hoch genug?
        JA  → Conrad (CONTRA) → Überlebt die Gegenprüfung?
                JA  → Sven (SYNC) → Pia (PULSE) → Prüfbericht
                NEIN → Claim als "widerlegt" markiert + Korrekturvorschlag
        NEIN → Claim als "ungeprüft" markiert → Mensch muss prüfen

VERBESSERUNGSPIPELINE:
Prüfbericht → Lena (LEGAL) → David (DRAFT) → Uma (UX)
    → Änderungsbericht → Mensch prüft und gibt frei
```

**Warum diese Reihenfolge?**

Simon muss zuerst arbeiten, weil ohne Behauptungen nichts geprüft werden kann. Vera kommt vor Conrad, weil Conrad nur Claims bekommt, die schon eine erste Prüfung bestanden haben. Das spart Kosten. Sven und Pia kommen am Ende, weil sie den Gesamtüberblick brauchen.

Im Verbesserungsteam kommt Lena zuerst, weil rechtliche Änderungen den Inhalt bestimmen. David kommt danach, weil er den neuen Text sprachlich poliert. Uma kommt zum Schluss, weil die Nutzerfreundlichkeit auf dem fertigen Text aufbaut.

### 2.4 Drei Repositories

Das System wird in drei getrennten Code-Projekten (Repositories) organisiert:

**Repository 1: `responzai-web`**
Die Website. Hier ändert sich nur wenig. Später kommt eine Komponente dazu, die Prüfergebnisse anzeigt.

**Repository 2: `responzai-verifier`**
Das Herzstück. Hier leben alle acht Agenten, die Pipeline und die API.

**Repository 3: `responzai-knowledge`**
Die Wissensbasis. Hier wird definiert, welche Quellen reinkommen und wie sie verarbeitet werden.

**Warum drei statt eins?**

Jedes Projekt hat einen eigenen Lebensrhythmus. Die Website wird aktualisiert, wenn sich Inhalte ändern. Die Agenten werden verbessert, wenn die Prüflogik besser werden soll. Die Wissensbasis wird aktualisiert, wenn neue Gesetze oder Leitlinien erscheinen. Trennung macht alles übersichtlicher und einfacher zu warten.

### 2.5 Infrastruktur

```
responzai.eu              responzai-verifier          responzai-knowledge
(Cloudflare Pages)        (Hetzner CX33 Server)       (gleicher Server)
                                  |                           |
  ← API-Aufruf ──────────── FastAPI                          |
                                  |                           |
                           Agenten-Pipeline                   |
                                  |                           |
                                  ├── RAG-Abfragen ──────────→|
                                  |                           |
                                  └── Claims speichern ──→ PostgreSQL + pgvector
```

**Die Bestandteile erklärt:**

- **Cloudflare Pages:** Dort läuft die Website responzai.eu. Das hast du schon.
- **Hetzner CX33:** Ein Cloud-Server in Helsinki. 4 CPUs, 8 GB Arbeitsspeicher, 80 GB Festplatte. Darauf laufen der Verifier, die Datenbank und n8n.
- **PostgreSQL + pgvector:** Eine Datenbank, die sowohl normale Daten als auch Vektoren (das sind mathematische Darstellungen von Texten) speichern kann. Damit kann das System Texte vergleichen und ähnliche Passagen finden.
- **FastAPI:** Ein Python-Framework, das die Schnittstelle (API) bereitstellt. Darüber kann die Website Prüfungen anstoßen und Ergebnisse abrufen.
- **Docker:** Jede Anwendung läuft in einem eigenen Container. Das ist wie eine abgeschlossene Box: Wenn eine Anwendung abstürzt, laufen die anderen weiter.
- **n8n:** Eine Automatisierungsplattform. Damit laufen Prüfungen automatisch, ohne dass jemand sie manuell anstoßen muss.

### 2.6 Kosten

```
Hetzner CX33 (Server)           ~  6,53 Euro/Monat
IPv4-Adresse                     ~  0,60 Euro/Monat (in den 6,53 enthalten)
Claude API (Prüfläufe)           ~ 12,00 Euro/Monat (Mittelwert)
Embeddings (Voyage-3)            ~  2,00 Euro/Monat
n8n (selbst gehostet)            ~  0,00 Euro/Monat
Cloudflare Pages (Website)       ~  0,00 Euro/Monat (Free Tier)
─────────────────────────────────────────────────────
Gesamt                           ~ 21 Euro/Monat
```

---

## 3. Die acht Agenten im Detail

### 3.1 Simon (SCOUT) — Content-Analyse

**Was Simon tut:**
Simon liest einen Text und zerlegt ihn in einzelne, prüfbare Behauptungen. Aus dem Satz "Der EU AI Act verpflichtet Unternehmen ab Februar 2025 zur KI-Kompetenz" macht Simon zwei Behauptungen:
1. "Der EU AI Act verpflichtet Unternehmen zur KI-Kompetenz" (Kategorie: LEGAL_CLAIM)
2. "Die Verpflichtung gilt ab Februar 2025" (Kategorie: LEGAL_CLAIM)

**Kategorien:**
- LEGAL_CLAIM: Rechtliche Aussagen (Gesetze, Pflichten, Fristen)
- PRODUCT_CLAIM: Aussagen über eigene Produkte (EVIDENCE, GUIDES)
- MARKET_CLAIM: Aussagen über den Markt oder die Branche
- TARGET_GROUP: Aussagen über die Zielgruppe

**Technologie:**
- Scrapy und BeautifulSoup zum Crawlen (automatisches Lesen) von Webseiten
- Claude API für die Zerlegung in Behauptungen
- PostgreSQL zum Speichern der Behauptungen

**Persönlichkeit:** Gründlich, systematisch, unermüdlich.
**Zitat:** "Jeder Satz enthält Behauptungen. Ich finde sie alle."

**Warum Simon wichtig ist:**
Ohne Simon gibt es nichts zu prüfen. Er ist das Fundament. Wenn Simon eine Behauptung übersieht, kann sie nicht geprüft werden. Deshalb ist er so gründlich: lieber eine Behauptung zu viel extrahieren als eine zu wenig.

### 3.2 Vera (VERIFY) — Faktenprüfung

**Was Vera tut:**
Vera nimmt jede einzelne Behauptung von Simon und sucht in der Wissensbasis nach Belegen. Sie nutzt dafür RAG (Retrieval Augmented Generation). Das bedeutet: Vera sucht zuerst die passende Stelle im Gesetzestext oder in einer anderen Quelle, und dann bewertet sie, ob die Behauptung mit dieser Quelle übereinstimmt.

**Ergebnis pro Behauptung:**
- Ein Konfidenz-Score zwischen 0 und 1 (0 = keine Übereinstimmung, 1 = perfekte Übereinstimmung)
- Status: verified (bestätigt) / uncertain (unsicher) / contradicted (widerlegt)
- Die Quellenpassage, die als Beleg dient

**Schwellenwert:** Nur Behauptungen mit einem Score über 0.8 gehen weiter an Conrad. Alles darunter wird als "ungeprüft" markiert und braucht menschliche Aufmerksamkeit.

**Technologie:**
- LangChain für die RAG-Pipeline
- pgvector für die Vektorsuche in der Datenbank
- Claude API für die Bewertung
- Voyage-3 Embeddings für die mathematische Darstellung der Texte

**Persönlichkeit:** Präzise, quellenorientiert, unbestechlich.
**Zitat:** "Vertrauen ist gut. Quellennachweis ist besser."

**Warum Vera so arbeitet:**
Vera könnte auch einfach Claude fragen "Stimmt diese Behauptung?" Aber dann würde Claude aus seinem Trainingswissen antworten, und das kann veraltet oder falsch sein. Stattdessen sucht Vera immer zuerst die Originalquelle und lässt Claude nur die Übereinstimmung bewerten. So bleibt alles nachprüfbar.

### 3.3 Conrad (CONTRA) — Gegenprüfung

**Was Conrad tut:**
Conrad ist der eingebaute Gegenspieler. Wenn Vera sagt "Diese Behauptung stimmt", versucht Conrad aktiv, sie zu widerlegen. Er sucht nach Ausnahmen, Sonderfällen, neueren Quellen und versteckten Annahmen.

**Conrads Strategien:**
1. Ausnahmensuche: Gibt es Fälle, in denen die Behauptung nicht gilt?
2. Zeitliche Prüfung: Gibt es neuere Quellen, die etwas anderes sagen?
3. Annahmenprüfung: Welche versteckten Voraussetzungen stecken in der Behauptung?
4. Gegenbeispiele: Gibt es konkrete Fälle, die der Behauptung widersprechen?

**Ergebnis pro Behauptung:**
- survived (überlebt): Conrad konnte die Behauptung nicht widerlegen.
- weakened (geschwächt): Conrad hat Einschränkungen gefunden.
- refuted (widerlegt): Conrad hat einen klaren Widerspruch gefunden.

**Technologie:**
- Claude API mit einem speziellen "inversen" Prompt (der Prompt fordert Claude auf, Gegenargumente zu finden)
- Eigene RAG-Abfrage mit umgekehrter Suchstrategie
- Optional: Web-Suche für aktuelle Informationen

**Persönlichkeit:** Kritisch, hartnäckig, konstruktiv unbequem.
**Zitat:** "Wenn ich es nicht widerlegen kann, stimmt es wahrscheinlich."

**Warum Conrad das Besondere am System ist:**
Die meisten Faktencheck-Systeme haben nur einen Prüfer (wie Vera). Das Problem: Ein KI-Modell neigt dazu, seine eigene Einschätzung zu bestätigen. Conrad bricht dieses Muster. Er ist wie ein Anwalt, der die Gegenposition einnimmt. Das kennt man aus der IT-Sicherheit als "Red Teaming": Ein Team greift das eigene System an, um Schwachstellen zu finden.

### 3.4 Sven (SYNC) — Konsistenzprüfung

**Was Sven tut:**
Sven vergleicht alle Behauptungen miteinander und über alle Kanäle hinweg. Steht auf der Website etwas anderes als im Newsletter? Widerspricht eine Behauptung auf der Startseite einer Behauptung auf der Produktseite? Sven baut eine "Widerspruchskarte" und bewertet den Schweregrad jedes Widerspruchs.

**Ergebnis:**
- Eine Contradiction-Map (Widerspruchskarte) mit allen gefundenen Inkonsistenzen
- Schweregrad pro Widerspruch: critical / major / minor
- Betroffene Quellen und Textstellen

**Technologie:**
- Embedding-Similarity: Sven vergleicht die mathematischen Darstellungen aller Behauptungen, um ähnliche Aussagen zu finden
- Claude API für die inhaltliche Bewertung
- Graph-Datenbank (Neo4j) oder alternativ PostgreSQL für die Beziehungen zwischen Behauptungen

**Persönlichkeit:** Vernetzt denkend, aufmerksam, ganzheitlich.
**Zitat:** "Wer überall dasselbe sagt, wird überall geglaubt."

### 3.5 Pia (PULSE) — Aktualitätsprüfung

**Was Pia tut:**
Pia erkennt Zeitbezüge in Behauptungen und prüft, ob die zugrundeliegenden Quellen noch aktuell sind. Ein Claim kann inhaltlich korrekt sein, aber trotzdem veraltet. Zum Beispiel: "Die Leitlinien des AI Office empfehlen..." Wenn seit dieser Aussage neue Leitlinien erschienen sind, markiert Pia das.

**Ergebnis pro Behauptung:**
- fresh (aktuell): Quelle ist auf dem neuesten Stand.
- stale (nicht mehr ganz frisch): Quelle ist älter, aber noch gültig.
- outdated (veraltet): Quelle wurde durch eine neuere Version ersetzt.
- Dazu: Ein Update-Vorschlag, wenn vorhanden.

**Was Pia überwacht:**
- EUR-Lex (das offizielle Rechtsportal der EU)
- Bundesgesetzblatt
- RSS-Feeds relevanter Behörden und Institutionen
- Veröffentlichungen des AI Office

**Technologie:**
- Scheduled Jobs (zeitgesteuerte Aufgaben)
- RSS-Parser
- Claude API für die Bewertung
- Webhooks (automatische Benachrichtigungen bei Änderungen)

**Persönlichkeit:** Wachsam, proaktiv, immer aktuell.
**Zitat:** "Was gestern stimmte, kann heute veraltet sein. Ich behalte das im Blick."

### 3.6 Lena (LEGAL) — Rechtliche Aktualisierung

**Was Lena tut:**
Lena gleicht jeden rechtlichen Bezug in den GUIDES-Vorlagen gegen die Wissensbasis ab. Aber anders als Vera prüft sie nicht nur, ob etwas stimmt. Sie schreibt den aktualisierten Text. Wenn sich eine Frist geändert hat oder eine neue Leitlinie erschienen ist, formuliert Lena den Ersatztext inklusive Quellenangabe.

**Anti-Halluzinations-Mechanismen (extrem wichtig):**

Lena darf nichts erfinden. Sie darf nur Informationen verwenden, die in den mitgelieferten Quellen stehen. Dafür gibt es vier Sicherheitsnetze:

1. **Nur verifizierte Quellen als Input:** Lena bekommt ausschließlich Behauptungen, die Vera geprüft und Conrad nicht widerlegt hat. Dazu die exakten Quellenpassagen.

2. **Quellenbindung im Prompt:** Jeder Satz, den Lena schreibt, muss mit einer Quellenreferenz enden. Wenn keine Quelle verfügbar ist, muss Lena das als Lücke markieren statt etwas zu erfinden.

3. **Rückprüfung:** Jeder Textvorschlag von Lena geht nochmal durch Vera und Conrad. So wird sichergestellt, dass Lenas Vorschläge die gleiche Prüfung bestehen wie der Originaltext.

4. **Quellen-Hashing:** Jede Quellenpassage bekommt einen digitalen Fingerabdruck (Hash). Lenas Output muss diese Fingerabdrücke referenzieren. So kann maschinell geprüft werden, ob Lena sich wirklich auf die mitgelieferten Quellen bezieht.

**Zusätzlich:** Lena läuft mit temperature=0 (keine kreative Variation), generiert nur Änderungen am bestehenden Text (nie ein komplett neues Dokument), und kein Vorschlag wird automatisch übernommen. Der Mensch gibt immer frei.

**Ergebnis:**
- Aktualisierter Textbaustein mit Quellenreferenz
- Coverage-Wert: Wie viel Prozent des Textes sind quellengestützt?
- Lücken-Liste: Stellen, an denen Quellen fehlen

**Persönlichkeit:** Präzise, verlässlich, ruhig bestimmt. Nie alarmistisch, immer fundiert.
**Zitat:** "Kein Satz ohne Rechtsgrundlage. Kein Verweis ohne Aktenzeichen."

### 3.7 David (DRAFT) — Textoptimierung

**Was David tut:**
David verbessert Texte sprachlich. Er kennt den responzai-Stilguide (siehe Kapitel 14) und sorgt dafür, dass alle Dokumente verständlich und konsistent klingen. David hasst Bürokratendeutsch, Nominalstil und überflüssige Wörter.

**Davids Regeln:**
- Wenn ein Zehnjähriger den Satz nicht versteht, muss er umgeschrieben werden.
- Kurze Sätze statt langer Schachtelsätze.
- Alltägliche Wörter statt Fachsprache (wenn Fachsprache nötig ist, wird sie erklärt).
- Keine Gedankenstriche.
- Keine abgenutzten Metaphern.
- Aktiv statt passiv formulieren.
- Konkrete Handlungsanweisungen statt vager Empfehlungen.

**Ergebnis:**
- Umformulierungsvorschlag mit Begründung
- Lesbarkeits-Score (vorher/nachher)
- Markierte Stellen, die sprachlich problematisch sind

**Persönlichkeit:** Kreativ-pragmatisch, sprachverliebt, leicht ungeduldig mit Bürokratendeutsch.
**Zitat:** "Wenn es niemand versteht, schützt es auch niemanden."

### 3.8 Uma (UX) — Bedienungsfreundlichkeit

**Was Uma tut:**
Uma prüft Dokumente aus Nutzerperspektive. Sie fragt: "Was macht der Anwender an dieser Stelle?" Uma analysiert Dokumentstruktur, Ausfüllhilfen, Reihenfolge und Verständlichkeit.

**Umas Prüfkriterien:**
- Sind die Anweisungen verständlich?
- Fehlen Ausfüllhilfen oder Beispiele?
- Ist die Reihenfolge logisch?
- Gibt es Stellen, an denen ein Anwender nicht weiß, was er eintragen soll?
- Sind lange Listen sinnvoll gruppiert?
- Ist klar, wer für welchen Schritt zuständig ist?

**Ergebnis:**
- Konkrete Änderungsanweisungen mit Begründung
- Priorisierung nach Auswirkung auf die Nutzererfahrung
- Vorher/Nachher-Vergleich der Dokumentstruktur

**Persönlichkeit:** Empathisch, strukturiert, freundlich hartnäckig. Vertritt immer die Person, die das Dokument am Ende in den Händen hält.
**Zitat:** "Ein Dokument ist erst fertig, wenn es jeder nutzen kann. Nicht nur der, der es geschrieben hat."

---

## 4. Infrastruktur aufsetzen

### 4.1 Voraussetzungen

Bevor wir anfangen, brauchst du:
- Einen Hetzner-Account (registriert und verifiziert)
- Einen SSH-Key (Anleitung folgt)
- Git installiert auf deinem Computer
- Einen GitHub-Account (oder GitLab, beides funktioniert)
- Einen Text-Editor (Visual Studio Code empfohlen, kostenlos)

### 4.2 SSH-Key erzeugen (Windows)

Ein SSH-Key ist wie ein digitaler Schlüssel. Er besteht aus zwei Teilen: einem privaten Schlüssel (den behältst du auf deinem Computer, nie weitergeben!) und einem öffentlichen Schlüssel (den gibst du dem Server, damit er dich erkennt).

**Schritt 1:** Öffne PowerShell.
Drücke die Windows-Taste, tippe "PowerShell" und drücke Enter.

**Schritt 2:** Erzeuge den Schlüssel.
Tippe diesen Befehl und drücke Enter:

```bash
ssh-keygen -t ed25519 -C "responzai"
```

**Was passiert:** Das Programm fragt dich drei Dinge.

- "Enter file in which to save the key": Einfach Enter drücken. Der Standardpfad ist gut.
- "Enter passphrase": Du kannst ein Passwort eingeben (sicherer) oder leer lassen (bequemer). Für den Anfang ist leer lassen in Ordnung.
- "Enter same passphrase again": Nochmal Enter.

**Schritt 3:** Zeige den öffentlichen Schlüssel an.
Tippe diesen Befehl:

```bash
cat ~/.ssh/id_ed25519.pub
```

**Was du siehst:** Eine lange Zeile, die mit `ssh-ed25519` anfängt. Das ist dein öffentlicher Schlüssel. Markiere die gesamte Zeile und kopiere sie (Rechtsklick → Kopieren).

### 4.3 Server bei Hetzner bestellen

**Schritt 1:** Öffne die Hetzner Cloud Console: console.hetzner.com

**Schritt 2:** Erstelle ein Projekt.
Klicke auf "Neues Projekt" und nenne es "responzai".

**Schritt 3:** Erstelle einen Server.
Klicke im Projekt auf "Server hinzufügen".

**Konfiguration:**

| Einstellung | Wert | Warum |
|---|---|---|
| Standort | Helsinki (oder Nürnberg/Falkenstein wenn verfügbar) | EU-Standort, DSGVO-konform |
| Image | Ubuntu 24.04 | Stabiles, weit verbreitetes Betriebssystem |
| Typ | CX33 (4 vCPUs, 8 GB RAM, 80 GB SSD) | Genug Leistung für Verifier + n8n + Datenbank |
| Netzwerk | Öffentliche IPv4 und IPv6 | Standard, damit der Server erreichbar ist |
| SSH-Keys | Deinen kopierten öffentlichen Schlüssel einfügen | Sichere Verbindung ohne Passwort |
| Backups | Aktivieren | Tägliche Sicherung für den Notfall |
| Name | responzai-verifier | Klarer Name für den Server |

**Schritt 4:** Klicke auf "Kostenpflichtig erstellen".

Der Server ist in etwa 30 Sekunden fertig. Du siehst danach eine IP-Adresse (z.B. 95.216.xx.xx). Diese brauchst du im nächsten Schritt.

### 4.4 Erste Verbindung zum Server

**Schritt 1:** Öffne PowerShell.

**Schritt 2:** Verbinde dich mit dem Server.
Ersetze DEINE-IP mit der Adresse aus der Hetzner Console:

```bash
ssh root@DEINE-IP
```

**Was passiert:** Beim ersten Mal fragt der Computer, ob du dem Server vertraust. Tippe "yes" und drücke Enter. Danach bist du auf dem Server. Du erkennst das daran, dass die Zeile jetzt mit `root@responzai-verifier:~#` beginnt.

### 4.5 Server absichern

**Warum:** Der Server ist gerade offen im Internet. Wir schließen die Türen, die wir nicht brauchen.

**Schritt 1:** System aktualisieren.

```bash
apt update && apt upgrade -y
```

Was das tut: Lädt die neueste Liste aller verfügbaren Programme herunter (update) und installiert alle Aktualisierungen (upgrade). Das `-y` bedeutet "ja, mach einfach, ohne nochmal zu fragen".

**Schritt 2:** Einen normalen Benutzer anlegen (statt immer als root zu arbeiten).

```bash
adduser responzai
usermod -aG sudo responzai
```

Was das tut: Erstellt einen neuen Benutzer namens "responzai" und gibt ihm das Recht, Befehle als Administrator auszuführen (sudo). Du wirst nach einem Passwort gefragt. Wähle ein sicheres Passwort.

**Schritt 3:** SSH-Key für den neuen Benutzer einrichten.

```bash
mkdir -p /home/responzai/.ssh
cp /root/.ssh/authorized_keys /home/responzai/.ssh/
chown -R responzai:responzai /home/responzai/.ssh
chmod 700 /home/responzai/.ssh
chmod 600 /home/responzai/.ssh/authorized_keys
```

Was das tut: Kopiert deinen SSH-Key auch für den neuen Benutzer. So kannst du dich als "responzai" anmelden statt als "root".

**Schritt 4:** Firewall einrichten.

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

Was das tut: Erlaubt nur drei Arten von Verbindungen: SSH (damit du dich verbinden kannst), HTTP (Port 80, für Webverkehr) und HTTPS (Port 443, für verschlüsselten Webverkehr). Alles andere wird blockiert.

**Ab jetzt verbindest du dich so:**

```bash
ssh responzai@DEINE-IP
```

### 4.6 Docker installieren

**Was ist Docker?**
Docker packt Programme in abgeschlossene Container. Jeder Container hat alles, was das Programm braucht. Wenn ein Container abstürzt, laufen die anderen weiter. Außerdem kann man Container einfach starten, stoppen und löschen, ohne den Rest des Servers zu beeinflussen.

**Installation:**

```bash
# Voraussetzungen installieren
sudo apt install -y ca-certificates curl gnupg

# Dockers offiziellen GPG-Schlüssel hinzufügen
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Docker-Repository hinzufügen
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker installieren
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Benutzer zur Docker-Gruppe hinzufügen (damit du Docker ohne sudo nutzen kannst)
sudo usermod -aG docker responzai
```

**Wichtig:** Nach dem letzten Befehl musst du dich einmal abmelden und wieder anmelden, damit die Gruppenänderung wirkt:

```bash
exit
ssh responzai@DEINE-IP
```

**Prüfen, ob Docker funktioniert:**

```bash
docker run hello-world
```

Wenn du eine Nachricht siehst, die mit "Hello from Docker!" beginnt, funktioniert alles.

### 4.7 Docker Compose einrichten

**Was ist Docker Compose?**
Docker Compose verwaltet mehrere Container gleichzeitig. Statt jeden Container einzeln zu starten, beschreibst du alle in einer einzigen Datei, und Docker Compose startet sie zusammen.

Erstelle das Projektverzeichnis und die Compose-Datei:

```bash
mkdir -p ~/responzai-verifier
cd ~/responzai-verifier
```

Erstelle die Datei `docker-compose.yml`:

```yaml
version: "3.8"

services:
  # ─────────────────────────────────────────
  # PostgreSQL mit pgvector
  # Die Datenbank für Claims und Embeddings
  # ─────────────────────────────────────────
  postgres:
    image: pgvector/pgvector:pg16
    container_name: responzai-db
    restart: always
    environment:
      POSTGRES_USER: responzai
      POSTGRES_PASSWORD: HIER_SICHERES_PASSWORT_EINSETZEN
      POSTGRES_DB: verifier
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U responzai -d verifier"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ─────────────────────────────────────────
  # n8n Automatisierung
  # Steuert die automatischen Prüfläufe
  # ─────────────────────────────────────────
  n8n:
    image: n8nio/n8n
    container_name: responzai-n8n
    restart: always
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=HIER_SICHERES_PASSWORT_EINSETZEN
      - N8N_HOST=n8n.DEINE-DOMAIN.de
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.DEINE-DOMAIN.de/
    volumes:
      - n8ndata:/home/node/.n8n
    ports:
      - "5678:5678"

  # ─────────────────────────────────────────
  # responzai Verifier API
  # Die Pipeline mit allen 8 Agenten
  # ─────────────────────────────────────────
  verifier:
    build: .
    container_name: responzai-verifier
    restart: always
    environment:
      - ANTHROPIC_API_KEY=HIER_DEINEN_API_KEY_EINSETZEN
      - DATABASE_URL=postgresql://responzai:HIER_SICHERES_PASSWORT_EINSETZEN@postgres:5432/verifier
      - VOYAGE_API_KEY=HIER_DEINEN_VOYAGE_KEY_EINSETZEN
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  pgdata:
  n8ndata:
```

**Was die einzelnen Teile bedeuten:**

- `image`: Welches Programm soll in dem Container laufen.
- `container_name`: Ein lesbarer Name für den Container.
- `restart: always`: Wenn der Container abstürzt, wird er automatisch neu gestartet.
- `environment`: Einstellungen und Passwörter für das Programm.
- `volumes`: Daten, die auch nach einem Neustart erhalten bleiben sollen.
- `ports`: Welcher Port von außen erreichbar sein soll.
- `depends_on`: Dieser Container startet erst, wenn der andere bereit ist.

**Container starten:**

```bash
docker compose up -d
```

Das `-d` bedeutet "im Hintergrund" (detached). Die Container laufen, auch wenn du die Verbindung zum Server schließt.

**Prüfen, ob alles läuft:**

```bash
docker compose ps
```

Du solltest drei Container sehen, alle mit dem Status "Up".

---

## 5. Repository-Struktur anlegen

### 5.1 Warum diese Struktur?

Jedes Repository hat eine klare Verantwortung. Das macht es einfacher, Fehler zu finden und Änderungen vorzunehmen. Wenn du an Simons (SCOUT) Logik arbeitest, musst du nicht durch den Code der Wissensbasis navigieren. Und wenn du eine neue Quelle hinzufügst, musst du nicht den Agenten-Code anfassen.

### 5.2 Repository: responzai-verifier

Das ist das Herzstück. Hier leben alle acht Agenten und die Pipeline.

```
responzai-verifier/
├── agents/
│   ├── simon_scout/               # Simon: Content-Analyse
│   │   ├── __init__.py
│   │   ├── prompt.py              # Simons Prompt-Template
│   │   ├── crawler.py             # Website-Crawling
│   │   └── parser.py              # Text in Claims zerlegen
│   ├── vera_verify/               # Vera: Faktenprüfung
│   │   ├── __init__.py
│   │   ├── prompt.py              # Veras Prompt-Template
│   │   ├── rag_query.py           # Abfrage gegen Wissensbasis
│   │   └── scoring.py             # Konfidenz-Berechnung
│   ├── conrad_contra/             # Conrad: Gegenprüfung
│   │   ├── __init__.py
│   │   ├── prompt.py              # Conrads inverser Prompt
│   │   ├── strategies.py          # Widerlegungs-Strategien
│   │   └── evaluation.py          # Bewertung der Ergebnisse
│   ├── sven_sync/                 # Sven: Konsistenzprüfung
│   │   ├── __init__.py
│   │   ├── prompt.py              # Svens Prompt-Template
│   │   ├── consistency.py         # Kanalübergreifender Vergleich
│   │   └── contradiction_map.py   # Widerspruchskarte erstellen
│   ├── pia_pulse/                 # Pia: Aktualitätsprüfung
│   │   ├── __init__.py
│   │   ├── prompt.py              # Pias Prompt-Template
│   │   ├── monitors.py            # EUR-Lex, RSS-Feeds überwachen
│   │   └── freshness.py           # Datumsabgleich
│   ├── lena_legal/                # Lena: Rechtliche Aktualisierung
│   │   ├── __init__.py
│   │   ├── prompt.py              # Lenas quellengebundener Prompt
│   │   ├── source_mapper.py       # Passende Rechtsquelle finden
│   │   ├── text_generator.py      # Aktualisierten Text schreiben
│   │   └── verification_loop.py   # Rückprüfung durch Vera + Conrad
│   ├── david_draft/               # David: Textoptimierung
│   │   ├── __init__.py
│   │   ├── prompt.py              # Davids Prompt-Template
│   │   ├── style_guide.py         # responzai-Stilregeln
│   │   └── rewriter.py            # Konkrete Umformulierungen
│   └── uma_ux/                    # Uma: Bedienungsfreundlichkeit
│       ├── __init__.py
│       ├── prompt.py              # Umas Prompt-Template
│       ├── structure_analyzer.py  # Dokumentstruktur prüfen
│       └── usability_rules.py     # Regeln für gute Vorlagen
├── document_ingestion/
│   ├── __init__.py
│   ├── router.py                  # Erkennt das Format und wählt den Parser
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py          # PDF-Dateien (inkl. gescannte PDFs via OCR)
│   │   ├── docx_parser.py         # Word-Dokumente (.docx)
│   │   ├── xlsx_parser.py         # Excel-Tabellen (.xlsx)
│   │   ├── pptx_parser.py         # PowerPoint-Präsentationen (.pptx)
│   │   ├── odt_parser.py          # OpenDocument-Text (.odt, .ods, .odp)
│   │   ├── html_parser.py         # HTML-Dateien
│   │   ├── markdown_parser.py     # Markdown-Dateien (.md)
│   │   ├── txt_parser.py          # Reine Textdateien (.txt, .csv)
│   │   ├── email_parser.py        # E-Mail-Dateien (.eml, .msg)
│   │   └── image_parser.py        # Bilder mit Text (OCR: .png, .jpg, .tiff)
│   ├── preprocessor.py            # Text bereinigen und normalisieren
│   ├── metadata_extractor.py      # Autor, Datum, Seitenzahl etc. auslesen
│   └── storage.py                 # Hochgeladene Dateien sicher speichern
├── pipeline/
│   ├── __init__.py
│   ├── orchestrator.py            # LangGraph-Pipeline
│   ├── config.py                  # Schwellenwerte, Modell-Auswahl
│   └── reporting.py               # Prüfbericht und Änderungsbericht
├── skills/
│   ├── claim_extraction.md        # Skill für Simon
│   ├── fact_check.md              # Skill für Vera
│   ├── adversarial_check.md       # Skill für Conrad
│   ├── consistency_check.md       # Skill für Sven
│   ├── freshness_check.md         # Skill für Pia
│   ├── legal_update.md            # Skill für Lena
│   ├── text_optimization.md       # Skill für David
│   ├── ux_review.md               # Skill für Uma
│   └── report_generation.md       # Skill für die Berichterstellung
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI-Hauptdatei
│   └── routes/
│       ├── verify.py              # POST /verify (URL oder Text prüfen)
│       ├── upload.py              # POST /verify/document (Datei hochladen und prüfen)
│       ├── improve.py             # POST /improve (GUIDES verbessern)
│       └── reports.py             # GET /reports (Berichte abrufen)
├── database/
│   ├── models.py                  # Datenbankmodelle
│   ├── connection.py              # Datenbankverbindung
│   └── migrations/                # Datenbankänderungen verwalten
├── tests/
│   ├── test_simon.py
│   ├── test_vera.py
│   ├── test_conrad.py
│   ├── test_sven.py
│   ├── test_pia.py
│   ├── test_lena.py
│   ├── test_david.py
│   ├── test_uma.py
│   ├── test_pipeline.py
│   └── test_document_ingestion.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example                   # Vorlage für Umgebungsvariablen
└── README.md
```

### 5.3 Repository: responzai-knowledge

Die Wissensbasis. Hier wird definiert, welche Quellen reinkommen und wie sie verarbeitet werden.

```
responzai-knowledge/
├── sources/
│   ├── primary/                   # Schicht 1: Primärquellen
│   │   ├── eu_ai_act.py           # EUR-Lex Fetcher
│   │   ├── delegated_acts.py      # Delegierte Verordnungen
│   │   └── ai_office.py           # Leitlinien des AI Office
│   ├── secondary/                 # Schicht 2: Sekundärquellen
│   │   └── curated/               # Manuell gepflegte Dokumente
│   │       └── README.md          # Anleitung zum Hinzufügen
│   └── own_content/               # Schicht 3: Eigene Inhalte
│       ├── website_crawler.py     # responzai.eu crawlen
│       └── newsletter_import.py   # Newsletter importieren
├── processing/
│   ├── chunking.py                # Dokumente in Stücke zerlegen
│   ├── embedding.py               # Embeddings erzeugen
│   └── metadata.py                # Quelle, Datum, Kategorie anhängen
├── database/
│   ├── schema.sql                 # PostgreSQL-Tabellen + pgvector
│   ├── migrations/
│   └── seed.py                    # Erstbefüllung der Datenbank
├── maintenance/
│   ├── update_checker.py          # Neue Versionen erkennen
│   └── reindex.py                 # Wissensbasis neu aufbauen
├── requirements.txt
└── README.md
```

### 5.4 Repository: responzai-web

Die Website. Das bestehende Projekt mit einer kleinen Erweiterung.

```
responzai-web/
├── src/
│   ├── components/
│   │   ├── AgentTeamPage.jsx      # Die Agenten-Vorstellungsseite
│   │   ├── ArchitectureViz.jsx    # Interaktive Architektur
│   │   ├── VerificationBadge.jsx  # Prüfergebnis-Anzeige
│   │   ├── DocumentUpload.jsx     # Drag-and-Drop-Upload mit Fortschrittsanzeige
│   │   ├── VerificationDashboard.jsx  # Ergebnis-Dashboard nach der Prüfung
│   │   └── ReportViewer.jsx       # Detailansicht eines Prüfberichts
│   ├── pages/
│   │   └── verify.jsx             # Die Prüfseite (/verify)
│   └── styles/
├── public/
├── package.json
└── README.md
```

---

## 6. Wissensbasis aufbauen

### 6.1 Was ist die Wissensbasis?

Die Wissensbasis ist das Gedächtnis des Systems. Hier sind alle Informationen gespeichert, gegen die das System prüft. Ohne Wissensbasis kann Vera keine Behauptungen verifizieren, Conrad keine Gegenargumente finden und Lena keine Rechtstexte aktualisieren.

### 6.2 Die drei Schichten

**Schicht 1: Primärquellen (höchste Autorität)**

Das sind die Originalquellen. Wenn es um den EU AI Act geht, ist das der Gesetzestext selbst, nicht ein Blogpost darüber.

Quellen:
- EU AI Act Volltext (Verordnung (EU) 2024/1689) von EUR-Lex
- Delegierte Verordnungen und Durchführungsrechtsakte
- Leitlinien des AI Office
- Nationale Umsetzungsgesetze (wenn vorhanden)

**Schicht 2: Autoritative Sekundärquellen (manuell kuratiert)**

Das sind vertrauenswürdige Interpretationen und Einordnungen.

Quellen:
- Fachkommentare von anerkannten Juristen
- Stellungnahmen der Datenschutzbehörden
- Whitepapers der EU-Kommission

Wichtig: Diese Quellen werden von Hand ausgewählt. Nicht alles, was im Internet steht, kommt hier rein. Nur Quellen, die von anerkannten Institutionen oder Experten stammen.

**Schicht 3: Eigene Inhalte (für Konsistenzprüfung)**

Das sind alle Texte von responzai selbst.

Quellen:
- Alle Seiten von responzai.eu
- Newsletter-Ausgaben ("KI & Kopf-Arbeit")
- LinkedIn-Posts
- GUIDES-Vorlagen

Diese Schicht braucht vor allem Sven (SYNC) für die Konsistenzprüfung.

### 6.3 Datenbank-Schema

Die Datenbank hat vier Haupttabellen:

```sql
-- pgvector-Erweiterung aktivieren
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabelle 1: Quellen
-- Speichert Informationen über jede Quelle
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,                    -- z.B. "EU AI Act"
    source_type TEXT NOT NULL,              -- primary / secondary / own
    url TEXT,                               -- Wo die Quelle herkommt
    fetched_at TIMESTAMP DEFAULT NOW(),     -- Wann sie abgerufen wurde
    last_checked TIMESTAMP,                 -- Wann zuletzt geprüft
    hash TEXT,                              -- Digitaler Fingerabdruck
    metadata JSONB                          -- Zusätzliche Informationen
);

-- Tabelle 2: Chunks
-- Speichert die zerlegten Textstücke mit ihren Embeddings
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    content TEXT NOT NULL,                  -- Der Textinhalt
    embedding vector(1024),                 -- Mathematische Darstellung
    chunk_index INTEGER,                    -- Position im Dokument
    metadata JSONB                          -- Kapitel, Artikel, etc.
);

-- Index für schnelle Ähnlichkeitssuche
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Tabelle 3: Claims
-- Speichert die extrahierten Behauptungen
CREATE TABLE claims (
    id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,               -- Wo die Behauptung steht
    claim_text TEXT NOT NULL,               -- Der Text der Behauptung
    category TEXT NOT NULL,                 -- LEGAL_CLAIM, etc.
    extracted_at TIMESTAMP DEFAULT NOW(),
    extracted_by TEXT DEFAULT 'simon',      -- Wer hat sie extrahiert
    
    -- Ergebnisse der Prüfung
    fact_check_score FLOAT,                -- Veras Score (0 bis 1)
    adversarial_result TEXT,               -- Conrads Ergebnis
    consistency_score FLOAT,               -- Svens Score
    freshness_status TEXT,                 -- Pias Status
    overall_confidence FLOAT,              -- Gesamtwert
    
    -- Verbesserungsvorschläge
    legal_suggestion TEXT,                 -- Lenas Vorschlag
    draft_suggestion TEXT,                 -- Davids Vorschlag
    ux_suggestion TEXT,                    -- Umas Vorschlag
    
    action_required BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- Tabelle 4: Prüfberichte
-- Speichert die fertigen Berichte
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    report_type TEXT NOT NULL,             -- verification / improvement
    source_url TEXT,
    total_claims INTEGER,
    verified_claims INTEGER,
    issues_found INTEGER,
    report_data JSONB,                     -- Der vollständige Bericht als JSON
    status TEXT DEFAULT 'completed'
);
```

**Warum diese Struktur?**

Die `sources`-Tabelle weiß, woher jede Information kommt. Die `chunks`-Tabelle speichert die zerlegten Texte mit ihren Vektoren, damit Vera und Conrad schnell ähnliche Stellen finden können. Die `claims`-Tabelle ist das zentrale Arbeitsobjekt: Hier fließen die Ergebnisse aller acht Agenten zusammen. Die `reports`-Tabelle speichert die fertigen Berichte.

### 6.4 Chunking-Strategie

**Was ist Chunking?**
Ein Gesetzestext hat manchmal hunderte Seiten. Das KI-Modell kann nicht den ganzen Text auf einmal verarbeiten. Also zerlegen wir den Text in kleinere Stücke (Chunks). Aber nicht wahllos, sondern so, dass jedes Stück inhaltlich zusammengehört.

**Strategie für Rechtstexte:**
- Jeder Artikel wird ein eigener Chunk.
- Wenn ein Artikel sehr lang ist (mehr als 500 Wörter), wird er an Absatzgrenzen geteilt.
- Jeder Chunk bekommt Metadaten: Welcher Artikel? Welcher Absatz? Welche Verordnung?

**Beispiel:**

```python
# Eingabe: Artikel 4 des EU AI Act
# Ausgabe: Ein Chunk mit diesen Metadaten:
{
    "content": "Anbieter und Betreiber von KI-Systemen ergreifen Maßnahmen...",
    "metadata": {
        "source": "Verordnung (EU) 2024/1689",
        "article": "Art. 4",
        "title": "KI-Kompetenz",
        "eur_lex_id": "32024R1689"
    }
}
```

### 6.5 Embeddings erzeugen

**Was sind Embeddings?**
Embeddings sind mathematische Darstellungen von Texten als Zahlenlisten (Vektoren). Zwei Texte, die inhaltlich ähnlich sind, haben ähnliche Vektoren. So kann das System schnell finden, welche Stelle in der Wissensbasis zu einer Behauptung passt.

**Beispiel vereinfacht:**
- "Unternehmen müssen KI-Kompetenz sicherstellen" → [0.23, 0.87, 0.12, ...]
- "Betreiber von KI-Systemen ergreifen Maßnahmen für KI-Kompetenz" → [0.25, 0.85, 0.14, ...]
- "Das Wetter ist heute schön" → [0.91, 0.03, 0.67, ...]

Die ersten beiden Vektoren sind sich ähnlich (die Zahlen liegen nah beieinander), weil die Texte inhaltlich ähnlich sind. Der dritte ist komplett anders.

**Code für die Embedding-Erzeugung:**

```python
# processing/embedding.py

import voyageai
from typing import List

# Voyage-3 Client initialisieren
client = voyageai.Client(api_key="DEIN_VOYAGE_API_KEY")

def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Erzeugt Embeddings für eine Liste von Texten.
    
    Was passiert hier?
    1. Wir schicken die Texte an die Voyage-3 API.
    2. Die API gibt für jeden Text einen Vektor zurück.
    3. Wir speichern diese Vektoren in der Datenbank.
    
    Warum Voyage-3?
    Voyage-3 ist speziell für die Suche in Dokumenten optimiert.
    Es versteht den Zusammenhang zwischen Frage und Antwort
    besser als allgemeine Embedding-Modelle.
    """
    result = client.embed(
        texts,
        model="voyage-3",
        input_type="document"  # Für Dokumente in der Wissensbasis
    )
    return result.embeddings


def create_query_embedding(query: str) -> List[float]:
    """
    Erzeugt ein Embedding für eine Suchanfrage.
    
    Warum ein separater Typ?
    Voyage-3 unterscheidet zwischen "document" (der gespeicherte Text)
    und "query" (die Suchanfrage). Das verbessert die Suchergebnisse.
    """
    result = client.embed(
        [query],
        model="voyage-3",
        input_type="query"  # Für Suchanfragen
    )
    return result.embeddings[0]
```

### 6.6 Erstbefüllung der Wissensbasis

**Schritt 1: EU AI Act herunterladen**

```python
# sources/primary/eu_ai_act.py

import requests
from bs4 import BeautifulSoup

def fetch_eu_ai_act():
    """
    Lädt den EU AI Act von EUR-Lex herunter.
    
    Warum EUR-Lex?
    Das ist das offizielle Rechtsportal der EU.
    Der Text dort ist die verbindliche Fassung.
    Alles andere sind Kopien, die veraltet sein könnten.
    """
    url = "https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32024R1689"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    # EUR-Lex strukturiert Artikel in bestimmten HTML-Elementen
    # Die genaue Struktur muss beim ersten Durchlauf geprüft werden
    
    return articles
```

**Schritt 2: Texte in Chunks zerlegen und Embeddings erzeugen**

```python
# processing/chunking.py

def chunk_legal_text(text: str, metadata: dict, max_words: int = 500):
    """
    Zerlegt einen Rechtstext in Chunks.
    
    Warum max. 500 Wörter?
    Zu kleine Chunks verlieren den Kontext.
    Zu große Chunks verwässern die Suche.
    500 Wörter sind ein guter Mittelwert für Rechtstexte.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len((current_chunk + paragraph).split()) > max_words:
            if current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": metadata
                })
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph
    
    if current_chunk:
        chunks.append({
            "content": current_chunk.strip(),
            "metadata": metadata
        })
    
    return chunks
```

**Schritt 3: In die Datenbank speichern**

```python
# database/seed.py

import asyncpg
from processing.embedding import create_embeddings
from processing.chunking import chunk_legal_text

async def seed_database():
    """
    Befüllt die Datenbank zum ersten Mal.
    
    Dieser Prozess läuft einmal am Anfang und dann
    bei jeder Aktualisierung der Quellen.
    """
    conn = await asyncpg.connect("postgresql://responzai:PASSWORT@localhost/verifier")
    
    # 1. Quelle registrieren
    source_id = await conn.fetchval("""
        INSERT INTO sources (title, source_type, url)
        VALUES ($1, $2, $3)
        RETURNING id
    """, "EU AI Act", "primary", "https://eur-lex.europa.eu/...")
    
    # 2. Text in Chunks zerlegen
    chunks = chunk_legal_text(ai_act_text, {"source": "EU AI Act"})
    
    # 3. Embeddings erzeugen (in Batches von 50)
    for i in range(0, len(chunks), 50):
        batch = chunks[i:i+50]
        texts = [c["content"] for c in batch]
        embeddings = create_embeddings(texts)
        
        # 4. In Datenbank speichern
        for chunk, embedding in zip(batch, embeddings):
            await conn.execute("""
                INSERT INTO chunks (source_id, content, embedding, metadata)
                VALUES ($1, $2, $3, $4)
            """, source_id, chunk["content"], embedding, chunk["metadata"])
    
    await conn.close()
    print(f"Wissensbasis befüllt: {len(chunks)} Chunks gespeichert.")
```

---

## 7. Dokument-Upload: Jedes Format prüfen

### 7.1 Was dieses Modul tut

Das System kann nicht nur Webseiten und eingetippten Text prüfen. Es kann auch Dateien verarbeiten, die hochgeladen werden. Egal ob PDF, Word, Excel, PowerPoint, E-Mail oder Bild: Das System erkennt das Format automatisch, extrahiert den Text und schickt ihn durch die Prüfpipeline.

**Warum ist das wichtig?**

Die GUIDES-Vorlagen sind Word-Dokumente. Newsletter kommen manchmal als PDF. Präsentationen liegen als PowerPoint vor. Wenn das System nur Webseiten prüfen kann, deckt es nur einen Teil der Inhalte ab. Mit dem Dokument-Upload kann alles geprüft werden, was Text enthält.

### 7.2 Unterstützte Formate

| Format | Dateitypen | Parser | Besonderheiten |
|---|---|---|---|
| PDF | .pdf | PyMuPDF (fitz) | Text-PDFs und gescannte PDFs (via OCR) |
| Word | .docx | python-docx | Tabellen, Kopfzeilen, Fußzeilen werden miterfasst |
| Excel | .xlsx | openpyxl | Jedes Blatt wird einzeln verarbeitet |
| PowerPoint | .pptx | python-pptx | Folientext und Notizen werden extrahiert |
| OpenDocument | .odt, .ods, .odp | odfpy | LibreOffice-kompatible Formate |
| HTML | .html, .htm | BeautifulSoup | Wie beim Web-Crawling, aber als lokale Datei |
| Markdown | .md | markdown-it | Formatierung wird in Struktur umgewandelt |
| Text | .txt, .csv | eingebaut | Direktes Lesen, kein Parser nötig |
| E-Mail | .eml, .msg | email (stdlib), extract-msg | Betreff, Text und Anhänge |
| Bilder | .png, .jpg, .tiff | Tesseract OCR | Text aus Bildern erkennen |

### 7.3 Der Format-Router

Der Router erkennt das Format anhand der Dateiendung und des MIME-Types. Er wählt automatisch den richtigen Parser.

```python
# document_ingestion/router.py

import mimetypes
from pathlib import Path
from typing import Optional

from .parsers.pdf_parser import parse_pdf
from .parsers.docx_parser import parse_docx
from .parsers.xlsx_parser import parse_xlsx
from .parsers.pptx_parser import parse_pptx
from .parsers.odt_parser import parse_odt
from .parsers.html_parser import parse_html
from .parsers.markdown_parser import parse_markdown
from .parsers.txt_parser import parse_txt
from .parsers.email_parser import parse_email
from .parsers.image_parser import parse_image

# Zuordnung: MIME-Type oder Endung → Parser-Funktion
PARSERS = {
    "application/pdf": parse_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": parse_xlsx,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": parse_pptx,
    "application/vnd.oasis.opendocument.text": parse_odt,
    "text/html": parse_html,
    "text/markdown": parse_markdown,
    "text/plain": parse_txt,
    "text/csv": parse_txt,
    "message/rfc822": parse_email,
    "image/png": parse_image,
    "image/jpeg": parse_image,
    "image/tiff": parse_image,
}

# Zusätzliche Zuordnung über Dateiendungen (als Fallback)
EXTENSION_MAP = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".ods": "application/vnd.oasis.opendocument.spreadsheet",
    ".odp": "application/vnd.oasis.opendocument.presentation",
    ".html": "text/html",
    ".htm": "text/html",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".eml": "message/rfc822",
    ".msg": "message/rfc822",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


def detect_format(filename: str, content_type: Optional[str] = None) -> str:
    """
    Erkennt das Format einer Datei.

    Zwei Wege:
    1. Der Browser schickt den Content-Type mit (zuverlässiger).
    2. Wir schauen auf die Dateiendung (Fallback).

    Warum beides?
    Manchmal schickt der Browser den falschen Content-Type.
    Manchmal hat die Datei eine ungewöhnliche Endung.
    Mit beiden Methoden zusammen erkennen wir fast alles.
    """
    if content_type and content_type in PARSERS:
        return content_type

    ext = Path(filename).suffix.lower()
    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    # Letzter Versuch: mimetypes-Bibliothek
    guessed, _ = mimetypes.guess_type(filename)
    if guessed and guessed in PARSERS:
        return guessed

    raise ValueError(
        f"Unbekanntes Dateiformat: {filename}. "
        f"Unterstützte Formate: {', '.join(EXTENSION_MAP.keys())}"
    )


async def ingest_document(
    file_path: str,
    filename: str,
    content_type: Optional[str] = None
) -> dict:
    """
    Hauptfunktion: Nimmt eine Datei entgegen und gibt
    strukturierten Text zurück.

    Ablauf:
    1. Format erkennen
    2. Richtigen Parser wählen
    3. Text extrahieren
    4. Text bereinigen und normalisieren
    5. Metadaten auslesen (Autor, Datum, Seitenzahl)

    Rückgabe:
    {
        "filename": "vertrag.pdf",
        "format": "application/pdf",
        "pages": 12,
        "text": "Der extrahierte Text...",
        "sections": [...],    # Text aufgeteilt nach Abschnitten
        "metadata": {...},    # Autor, Datum etc.
    }
    """
    from .preprocessor import clean_text
    from .metadata_extractor import extract_metadata

    mime_type = detect_format(filename, content_type)
    parser = PARSERS[mime_type]

    # Text extrahieren
    raw_result = await parser(file_path)

    # Text bereinigen
    cleaned_text = clean_text(raw_result["text"])

    # Metadaten auslesen
    metadata = extract_metadata(file_path, mime_type)

    return {
        "filename": filename,
        "format": mime_type,
        "pages": raw_result.get("pages", 1),
        "text": cleaned_text,
        "sections": raw_result.get("sections", []),
        "metadata": metadata,
        "raw_length": len(raw_result["text"]),
        "cleaned_length": len(cleaned_text),
    }
```

### 7.4 Die Parser im Detail

**PDF-Parser (der wichtigste):**

```python
# document_ingestion/parsers/pdf_parser.py

import fitz  # PyMuPDF
import subprocess
import os

async def parse_pdf(file_path: str) -> dict:
    """
    Extrahiert Text aus PDF-Dateien.

    Zwei Fälle:
    1. Text-PDF: Der Text ist direkt im PDF gespeichert.
       Das ist der einfache Fall. PyMuPDF liest ihn direkt.
    2. Gescanntes PDF: Das PDF ist eigentlich ein Bild.
       Hier brauchen wir OCR (Texterkennung).

    Wie unterscheiden wir die beiden?
    Wir versuchen zuerst, Text direkt zu lesen.
    Wenn kaum Text gefunden wird (weniger als 50 Zeichen
    pro Seite im Durchschnitt), ist es wahrscheinlich ein Scan.
    """
    doc = fitz.open(file_path)
    pages = []
    total_text = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page": page_num + 1,
            "text": text
        })
        total_text += text + "\n\n"

    # Prüfen, ob OCR nötig ist
    avg_chars_per_page = len(total_text) / max(len(pages), 1)

    if avg_chars_per_page < 50:
        # Wahrscheinlich ein gescanntes PDF. OCR verwenden.
        total_text = await _ocr_pdf(file_path)
        # Seiten neu aufteilen (OCR gibt den gesamten Text zurück)
        pages = [{"page": 1, "text": total_text}]

    doc.close()

    return {
        "text": total_text,
        "pages": len(pages),
        "sections": pages,
        "ocr_used": avg_chars_per_page < 50
    }


async def _ocr_pdf(file_path: str) -> str:
    """
    OCR für gescannte PDFs mit Tesseract.

    Ablauf:
    1. PDF in einzelne Bilder umwandeln (mit PyMuPDF)
    2. Jedes Bild durch Tesseract schicken
    3. Erkannten Text zusammenfügen

    Warum Tesseract?
    Tesseract ist die beste Open-Source-OCR-Engine.
    Sie unterstützt Deutsch und viele andere Sprachen.
    Sie läuft lokal, es werden keine Daten an externe
    Dienste geschickt.
    """
    import pytesseract
    from PIL import Image
    import io

    doc = fitz.open(file_path)
    full_text = ""

    for page in doc:
        # Seite als Bild rendern (300 DPI für gute Erkennung)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        # OCR durchführen (Deutsch + Englisch)
        text = pytesseract.image_to_string(img, lang="deu+eng")
        full_text += text + "\n\n"

    doc.close()
    return full_text
```

**Word-Parser:**

```python
# document_ingestion/parsers/docx_parser.py

from docx import Document

async def parse_docx(file_path: str) -> dict:
    """
    Extrahiert Text aus Word-Dokumenten.

    Word-Dokumente haben eine klare Struktur:
    Überschriften, Absätze, Tabellen, Kopfzeilen, Fußzeilen.
    Wir behalten diese Struktur bei, weil sie für die
    Agenten wertvoll ist. Simon kann so erkennen, in welchem
    Kapitel eine Behauptung steht.
    """
    doc = Document(file_path)
    sections = []
    full_text = ""
    current_section = {"heading": "", "text": ""}

    for paragraph in doc.paragraphs:
        # Überschriften erkennen
        if paragraph.style.name.startswith("Heading"):
            # Vorherige Sektion speichern
            if current_section["text"].strip():
                sections.append(current_section.copy())
            current_section = {
                "heading": paragraph.text,
                "level": int(paragraph.style.name.replace("Heading ", "") or "1"),
                "text": ""
            }
        else:
            current_section["text"] += paragraph.text + "\n"

        full_text += paragraph.text + "\n"

    # Letzte Sektion speichern
    if current_section["text"].strip():
        sections.append(current_section)

    # Tabellen extrahieren
    for table in doc.tables:
        table_text = "\n"
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            table_text += " | ".join(cells) + "\n"
        full_text += table_text

    return {
        "text": full_text,
        "sections": sections,
        "pages": len(doc.sections)
    }
```

**Excel-Parser:**

```python
# document_ingestion/parsers/xlsx_parser.py

from openpyxl import load_workbook

async def parse_xlsx(file_path: str) -> dict:
    """
    Extrahiert Text aus Excel-Tabellen.

    Warum Excel prüfen?
    GUIDES-Vorlagen enthalten manchmal Checklisten oder
    Bewertungsmatrizen als Excel-Tabellen. Diese enthalten
    Behauptungen, die geprüft werden müssen.

    Jedes Blatt (Sheet) wird einzeln verarbeitet.
    Die Zellinhalte werden als Tabelle formatiert.
    """
    wb = load_workbook(file_path, read_only=True, data_only=True)
    sections = []
    full_text = ""

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        sheet_text = f"Blatt: {sheet_name}\n"

        for row in ws.iter_rows(values_only=True):
            # Leere Zellen überspringen
            cells = [str(cell) if cell is not None else "" for cell in row]
            if any(cells):
                sheet_text += " | ".join(cells) + "\n"

        sections.append({
            "heading": f"Blatt: {sheet_name}",
            "text": sheet_text
        })
        full_text += sheet_text + "\n\n"

    wb.close()

    return {
        "text": full_text,
        "sections": sections,
        "pages": len(wb.sheetnames)
    }
```

**PowerPoint-Parser:**

```python
# document_ingestion/parsers/pptx_parser.py

from pptx import Presentation

async def parse_pptx(file_path: str) -> dict:
    """
    Extrahiert Text aus PowerPoint-Präsentationen.

    PowerPoint hat zwei Textquellen:
    1. Der sichtbare Folieninhalt (Textboxen, Titel)
    2. Die Sprechernotizen (oft enthalten die mehr Inhalt)

    Wir extrahieren beides, weil in den Notizen oft
    detailliertere Behauptungen stehen als auf der Folie.
    """
    prs = Presentation(file_path)
    sections = []
    full_text = ""

    for slide_num, slide in enumerate(prs.slides, 1):
        slide_text = f"Folie {slide_num}:\n"

        # Text aus allen Textboxen
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    slide_text += paragraph.text + "\n"

        # Sprechernotizen
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text
            if notes.strip():
                slide_text += f"\nNotizen: {notes}\n"

        sections.append({
            "heading": f"Folie {slide_num}",
            "text": slide_text
        })
        full_text += slide_text + "\n\n"

    return {
        "text": full_text,
        "sections": sections,
        "pages": len(prs.slides)
    }
```

**Bild-Parser (OCR):**

```python
# document_ingestion/parsers/image_parser.py

import pytesseract
from PIL import Image

async def parse_image(file_path: str) -> dict:
    """
    Erkennt Text in Bildern mit Tesseract OCR.

    Wann kommt das vor?
    Manchmal werden Screenshots von Texten geschickt.
    Oder eingescannte Briefe und Formulare als einzelne Bilder.

    Einschränkung: OCR ist nicht perfekt. Bei schlechter
    Bildqualität sinkt die Erkennungsrate. Das System markiert
    OCR-extrahierten Text als "ocr_extracted", damit die
    Agenten wissen, dass der Text Fehler enthalten könnte.
    """
    img = Image.open(file_path)

    # OCR durchführen (Deutsch + Englisch)
    text = pytesseract.image_to_string(img, lang="deu+eng")

    # OCR-Konfidenz berechnen
    data = pytesseract.image_to_data(
        img, lang="deu+eng", output_type=pytesseract.Output.DICT
    )
    confidences = [int(c) for c in data["conf"] if int(c) > 0]
    avg_confidence = sum(confidences) / max(len(confidences), 1)

    return {
        "text": text,
        "pages": 1,
        "sections": [{"heading": "OCR-Text", "text": text}],
        "ocr_used": True,
        "ocr_confidence": round(avg_confidence, 1)
    }
```

### 7.5 Text bereinigen und normalisieren

```python
# document_ingestion/preprocessor.py

import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Bereinigt den extrahierten Text.

    Warum ist das nötig?
    PDF-Parser liefern oft kaputten Text: doppelte Leerzeichen,
    Zeilenumbrüche mitten im Wort, seltsame Sonderzeichen.
    Word-Dokumente haben manchmal unsichtbare Steuerzeichen.

    Diese Funktion räumt auf, ohne den Inhalt zu verändern.
    """
    # Unicode normalisieren (verschiedene Darstellungen vereinheitlichen)
    text = unicodedata.normalize("NFKC", text)

    # Steuerzeichen entfernen (außer Zeilenumbruch und Tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Mehrfache Leerzeichen zu einem
    text = re.sub(r"[ \t]+", " ", text)

    # Mehr als zwei aufeinanderfolgende Leerzeilen zu zwei
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Bindestrich-Trennungen am Zeilenende zusammenfügen
    # "Verant-\nwortung" → "Verantwortung"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Leerzeichen am Anfang und Ende jeder Zeile entfernen
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)

    return text.strip()
```

### 7.6 Metadaten auslesen

```python
# document_ingestion/metadata_extractor.py

import os
from datetime import datetime

def extract_metadata(file_path: str, mime_type: str) -> dict:
    """
    Liest Metadaten aus der Datei.

    Warum Metadaten?
    Pia braucht das Datum, um die Aktualität zu beurteilen.
    Simon nutzt den Dokumenttitel für den Kontext.
    Sven braucht den Autor, um Quellen zuzuordnen.
    """
    stat = os.stat(file_path)

    metadata = {
        "file_size_bytes": stat.st_size,
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }

    # Dokumentspezifische Metadaten
    if mime_type == "application/pdf":
        metadata.update(_pdf_metadata(file_path))
    elif "wordprocessingml" in mime_type:
        metadata.update(_docx_metadata(file_path))

    return metadata


def _pdf_metadata(file_path: str) -> dict:
    import fitz
    doc = fitz.open(file_path)
    meta = doc.metadata
    doc.close()
    return {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "subject": meta.get("subject", ""),
        "creator": meta.get("creator", ""),
        "creation_date": meta.get("creationDate", ""),
    }


def _docx_metadata(file_path: str) -> dict:
    from docx import Document
    doc = Document(file_path)
    props = doc.core_properties
    return {
        "title": props.title or "",
        "author": props.author or "",
        "subject": props.subject or "",
        "created": props.created.isoformat() if props.created else "",
        "modified": props.modified.isoformat() if props.modified else "",
    }
```

### 7.7 Sichere Dateispeicherung

```python
# document_ingestion/storage.py

import os
import uuid
import hashlib
from pathlib import Path

UPLOAD_DIR = Path("/app/data/uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Erlaubte Dateitypen (Sicherheit: keine ausführbaren Dateien)
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".odt", ".ods", ".odp",
    ".html", ".htm", ".md", ".txt", ".csv",
    ".eml", ".msg",
    ".png", ".jpg", ".jpeg", ".tiff", ".tif",
}


async def save_upload(file_content: bytes, filename: str) -> dict:
    """
    Speichert eine hochgeladene Datei sicher auf dem Server.

    Sicherheitsmaßnahmen:
    1. Nur erlaubte Dateitypen (keine .exe, .sh, .py etc.)
    2. Maximale Dateigröße: 50 MB
    3. Dateiname wird durch eine UUID ersetzt (verhindert
       Path-Traversal-Angriffe wie "../../etc/passwd")
    4. Dateien werden in einem eigenen Verzeichnis gespeichert
    5. Hash wird berechnet, um Duplikate zu erkennen
    """
    # Dateityp prüfen
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Dateityp '{ext}' nicht erlaubt. "
            f"Erlaubt: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Dateigröße prüfen
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            f"Datei zu groß: {len(file_content)} Bytes. "
            f"Maximum: {MAX_FILE_SIZE} Bytes (50 MB)."
        )

    # Hash berechnen (für Duplikat-Erkennung)
    file_hash = hashlib.sha256(file_content).hexdigest()

    # Sicheren Dateinamen generieren
    safe_name = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / safe_name

    # Verzeichnis erstellen, falls nicht vorhanden
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Datei speichern
    with open(file_path, "wb") as f:
        f.write(file_content)

    return {
        "stored_path": str(file_path),
        "original_name": filename,
        "hash": file_hash,
        "size": len(file_content),
    }
```

### 7.8 API-Endpunkt für den Dokument-Upload

```python
# api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from document_ingestion.router import ingest_document
from document_ingestion.storage import save_upload
from pipeline.orchestrator import build_pipeline

router = APIRouter()

@router.post("/verify/document")
async def verify_document(
    file: UploadFile = File(...),
    mode: str = "full"
):
    """
    Nimmt eine Datei entgegen, extrahiert den Text und
    startet die Prüfpipeline.

    Ablauf:
    1. Datei sicher speichern
    2. Format erkennen und Text extrahieren
    3. Text an die Prüfpipeline übergeben
    4. Ergebnis zurückgeben

    Parameter:
    - file: Die hochgeladene Datei (beliebiges unterstütztes Format)
    - mode: "full" (alle 8 Agenten) oder "quick" (nur Simon + Vera)

    Beispiel mit curl:
    curl -X POST "https://api.responzai.eu/verify/document" \
         -F "file=@mein_dokument.pdf" \
         -F "mode=full"
    """
    # Schritt 1: Datei speichern
    content = await file.read()
    try:
        stored = await save_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Schritt 2: Text extrahieren
    try:
        document = await ingest_document(
            stored["stored_path"],
            file.filename,
            file.content_type
        )
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    # Schritt 3: Pipeline starten
    pipeline = build_pipeline()

    initial_state = {
        "source_url": f"upload://{file.filename}",
        "source_text": document["text"],
        "claims": [],
        "verified_claims": [],
        "unverified_claims": [],
        "survived_claims": [],
        "weakened_claims": [],
        "refuted_claims": [],
        "contradictions": [],
        "consistency_score": 0.0,
        "freshness_results": [],
        "legal_updates": [],
        "text_improvements": [],
        "ux_issues": [],
        "verification_report": None,
        "improvement_report": None,
    }

    result = await pipeline.ainvoke(initial_state)

    return {
        "filename": file.filename,
        "format": document["format"],
        "pages": document["pages"],
        "text_length": document["cleaned_length"],
        "metadata": document["metadata"],
        "total_claims": len(result["claims"]),
        "verified_claims": len(result["verified_claims"]),
        "issues_found": len(result["refuted_claims"]) + len(result["weakened_claims"]),
        "report": result["verification_report"],
    }
```

### 7.9 Die Upload-Route in der API registrieren

In der Datei `api/main.py` muss die neue Route eingebunden werden:

```python
# In api/main.py folgende Zeilen ergänzen:

from api.routes.upload import router as upload_router

app.include_router(upload_router)
```

### 7.10 Docker: Tesseract für OCR installieren

Im Dockerfile muss Tesseract installiert werden, damit OCR funktioniert:

```dockerfile
# Basis-Image: Python 3.11 (schlank)
FROM python:3.11-slim

# Tesseract OCR und deutsche Sprachdaten installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-deu \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten zuerst kopieren (für Cache-Optimierung)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Upload-Verzeichnis erstellen
RUN mkdir -p /app/data/uploads

# Port freigeben
EXPOSE 8000

# Anwendung starten
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.11 Zusätzliche Python-Abhängigkeiten

Diese Pakete kommen zur `requirements.txt` dazu:

```
# Dokument-Parsing
PyMuPDF==1.23.8              # PDF lesen und rendern
python-docx==1.1.0           # Word-Dokumente lesen
openpyxl==3.1.2              # Excel-Tabellen lesen
python-pptx==0.6.23          # PowerPoint lesen
odfpy==1.4.1                 # OpenDocument-Formate lesen
pytesseract==0.3.10          # OCR (Texterkennung in Bildern)
Pillow==10.2.0               # Bildverarbeitung (für OCR)
extract-msg==0.48.0          # Outlook .msg Dateien lesen
python-multipart==0.0.6      # Datei-Upload in FastAPI
```

### 7.12 Wie Simon mit hochgeladenen Dokumenten umgeht

Simon muss wissen, ob der Text von einer Webseite oder aus einem Dokument kommt. Bei Dokumenten ist die Quelle das Dokument selbst, nicht eine URL.

Die Erkennung funktioniert über das `source_url`-Feld: Wenn es mit `upload://` beginnt, weiß Simon, dass es ein hochgeladenes Dokument ist. Der Dateiname hilft bei der Zuordnung.

Bei Dokumenten mit Sektionen (Überschriften in Word, Folien in PowerPoint, Blätter in Excel) verarbeitet Simon jede Sektion einzeln. So kann er genauer sagen, in welchem Kapitel oder auf welcher Folie eine Behauptung steht.

### 7.13 Sicherheitshinweise

1. **Keine ausführbaren Dateien:** Das System akzeptiert nur Dokumentformate. Keine .exe, .sh, .bat, .py oder andere ausführbare Dateien.
2. **Dateigröße begrenzt:** Maximum 50 MB. Das reicht für die meisten Dokumente, verhindert aber Missbrauch.
3. **Dateinamen werden ersetzt:** Der Originalname wird gespeichert, aber die Datei bekommt einen zufälligen Namen (UUID). Das verhindert Angriffe über manipulierte Dateinamen.
4. **Kein automatisches Ausführen:** Die Parser lesen nur Text. Sie führen keine Makros, Skripte oder eingebetteten Objekte aus.
5. **Aufräumen:** Hochgeladene Dateien werden nach der Verarbeitung nicht automatisch gelöscht. Ein Cronjob sollte Dateien älter als 7 Tage entfernen.

---

## 8. Prüfteam umsetzen

### 8.1 Simon (SCOUT) — Claims extrahieren

Simon ist der erste Agent in der Kette. Er bekommt einen Text (oder eine URL) und gibt eine Liste von strukturierten Behauptungen zurück.

**Der Prompt:**

```python
# agents/simon_scout/prompt.py

SIMON_SYSTEM_PROMPT = """Du bist Simon, der Content-Analyst im responzai-Prüfteam.

DEINE AUFGABE:
Zerlege den folgenden Text in einzelne, prüfbare Behauptungen (Claims).
Jede Behauptung muss so formuliert sein, dass man sie eindeutig als
wahr oder falsch bewerten kann.

REGELN:
1. Jede Behauptung besteht aus Subjekt, Prädikat und Objekt.
2. Eine Behauptung pro Aussage. Wenn ein Satz zwei Dinge behauptet,
   mache zwei Behauptungen daraus.
3. Kategorisiere jede Behauptung:
   - LEGAL_CLAIM: Rechtliche Aussagen (Gesetze, Pflichten, Fristen)
   - PRODUCT_CLAIM: Aussagen über responzai-Produkte
   - MARKET_CLAIM: Aussagen über den Markt oder die Branche
   - TARGET_GROUP: Aussagen über die Zielgruppe
4. Bewerte die Prüfbarkeit jeder Behauptung: high / medium / low
5. Extrahiere den Originaltext, aus dem die Behauptung stammt.

AUSGABEFORMAT (JSON):
{
  "claims": [
    {
      "id": "claim_001",
      "claim_text": "Die prüfbare Behauptung als klarer Satz",
      "category": "LEGAL_CLAIM",
      "verifiability": "high",
      "original_text": "Der Originalsatz aus dem Quelltext",
      "source_url": "https://...",
      "implicit_assumptions": ["Liste versteckter Annahmen"]
    }
  ],
  "summary": {
    "total_claims": 15,
    "by_category": {
      "LEGAL_CLAIM": 8,
      "PRODUCT_CLAIM": 4,
      "MARKET_CLAIM": 2,
      "TARGET_GROUP": 1
    }
  }
}
"""
```

**Die Crawler-Logik:**

```python
# agents/simon_scout/crawler.py

import requests
from bs4 import BeautifulSoup

def crawl_page(url: str) -> dict:
    """
    Liest eine Webseite und extrahiert den Text.
    
    Warum BeautifulSoup?
    Webseiten enthalten viel mehr als nur Text: Navigation,
    Footer, Werbung, Skripte. BeautifulSoup hilft uns, nur
    den eigentlichen Inhalt zu finden.
    """
    response = requests.get(url, headers={
        "User-Agent": "responzai-verifier/1.0"
    })
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Navigation, Footer und Skripte entfernen
    for element in soup.find_all(["nav", "footer", "script", "style"]):
        element.decompose()
    
    # Hauptinhalt finden
    # (Die genauen Selektoren hängen von der Website ab)
    main_content = soup.find("main") or soup.find("article") or soup.body
    
    return {
        "url": url,
        "title": soup.title.string if soup.title else "",
        "text": main_content.get_text(separator="\n", strip=True),
        "crawled_at": datetime.now().isoformat()
    }
```

**Die Parser-Logik (Simon in Aktion):**

```python
# agents/simon_scout/parser.py

import anthropic
from .prompt import SIMON_SYSTEM_PROMPT
import json

client = anthropic.Anthropic()

async def extract_claims(text: str, source_url: str) -> dict:
    """
    Schickt den Text an Claude und bekommt strukturierte Claims zurück.
    
    Warum temperature=0?
    Wir wollen, dass Simon bei demselben Text immer dieselben
    Behauptungen findet. Kreativität ist hier nicht erwünscht.
    Reproduzierbarkeit ist wichtiger.
    """
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0,
        system=SIMON_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""Analysiere diesen Text und extrahiere 
                alle prüfbaren Behauptungen.
                
                URL: {source_url}
                
                TEXT:
                {text}
                """
            }
        ]
    )
    
    # Antwort parsen
    response_text = message.content[0].text
    
    # JSON aus der Antwort extrahieren
    # (Claude gibt manchmal Text vor/nach dem JSON zurück)
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    claims_data = json.loads(response_text[json_start:json_end])
    
    return claims_data
```

### 8.2 Vera (VERIFY) — Faktenprüfung

Vera bekommt jeden Claim von Simon und prüft ihn gegen die Wissensbasis.

**Der Prompt:**

```python
# agents/vera_verify/prompt.py

VERA_SYSTEM_PROMPT = """Du bist Vera, die Faktenprüferin im responzai-Prüfteam.

DEINE AUFGABE:
Prüfe die folgende Behauptung (Claim) gegen die bereitgestellten
Quellenpassagen aus der Wissensbasis.

REGELN:
1. Bewerte NUR auf Basis der bereitgestellten Quellenpassagen.
2. Verwende KEIN eigenes Wissen.
3. Wenn die Quellenpassagen nicht ausreichen, sage das ehrlich.
4. Gib einen Konfidenz-Score zwischen 0.0 und 1.0 an.

BEWERTUNGSSKALA:
- 0.9 bis 1.0: Die Behauptung wird direkt und eindeutig belegt.
- 0.7 bis 0.9: Die Behauptung wird weitgehend belegt, kleine Unschärfen.
- 0.5 bis 0.7: Die Behauptung wird teilweise belegt, aber es fehlen Details.
- 0.3 bis 0.5: Die Behauptung hat nur schwache Belege.
- 0.0 bis 0.3: Die Behauptung wird nicht belegt oder widersprochen.

AUSGABEFORMAT (JSON):
{
  "claim_id": "claim_001",
  "score": 0.85,
  "status": "verified",
  "reasoning": "Warum dieser Score vergeben wurde",
  "supporting_passages": [
    {
      "chunk_id": 42,
      "text": "Die relevante Stelle aus der Quelle",
      "source": "EU AI Act, Art. 4",
      "relevance": 0.92
    }
  ],
  "gaps": ["Was in den Quellen nicht abgedeckt wird"]
}
"""
```

**Die RAG-Abfrage:**

```python
# agents/vera_verify/rag_query.py

import asyncpg
from processing.embedding import create_query_embedding

async def find_relevant_chunks(claim_text: str, top_k: int = 5) -> list:
    """
    Sucht die relevantesten Stellen in der Wissensbasis.
    
    Wie funktioniert das?
    1. Wir wandeln die Behauptung in einen Vektor um.
    2. Wir suchen in der Datenbank nach den ähnlichsten Vektoren.
    3. Die ähnlichsten Stellen sind am wahrscheinlichsten relevant.
    
    top_k=5 bedeutet: Wir holen die 5 besten Treffer.
    Warum 5? Genug für Kontext, aber nicht so viel, dass
    irrelevante Stellen die Bewertung verwässern.
    """
    query_embedding = create_query_embedding(claim_text)
    
    conn = await asyncpg.connect("postgresql://responzai:PASSWORT@localhost/verifier")
    
    rows = await conn.fetch("""
        SELECT c.id, c.content, c.metadata, s.title,
               1 - (c.embedding <=> $1::vector) AS similarity
        FROM chunks c
        JOIN sources s ON c.source_id = s.id
        ORDER BY c.embedding <=> $1::vector
        LIMIT $2
    """, query_embedding, top_k)
    
    await conn.close()
    
    return [
        {
            "chunk_id": row["id"],
            "text": row["content"],
            "source": row["title"],
            "metadata": row["metadata"],
            "similarity": float(row["similarity"])
        }
        for row in rows
    ]
```

**Die Scoring-Logik:**

```python
# agents/vera_verify/scoring.py

import anthropic
from .prompt import VERA_SYSTEM_PROMPT
from .rag_query import find_relevant_chunks
import json

client = anthropic.Anthropic()

async def verify_claim(claim: dict) -> dict:
    """
    Prüft eine einzelne Behauptung gegen die Wissensbasis.
    
    Ablauf:
    1. Relevante Quellenpassagen finden (RAG)
    2. Behauptung + Quellen an Claude schicken
    3. Bewertung zurückbekommen
    """
    # Schritt 1: Relevante Stellen finden
    relevant_chunks = await find_relevant_chunks(claim["claim_text"])
    
    # Schritt 2: Quellen als Kontext aufbereiten
    context = "\n\n".join([
        f"[Quelle: {chunk['source']}]\n{chunk['text']}"
        for chunk in relevant_chunks
    ])
    
    # Schritt 3: An Claude schicken
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        temperature=0,
        system=VERA_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""BEHAUPTUNG:
{claim['claim_text']}

KATEGORIE: {claim['category']}

QUELLENPASSAGEN AUS DER WISSENSBASIS:
{context}

Bewerte diese Behauptung auf Basis der Quellenpassagen."""
            }
        ]
    )
    
    # Ergebnis parsen
    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    result = json.loads(response_text[json_start:json_end])
    
    return result
```

### 8.3 Conrad (CONTRA) — Adversariale Gegenprüfung

Conrad ist der eingebaute Gegenspieler. Er bekommt nur Claims, die Vera mit einem Score über 0.8 bewertet hat.

**Der Prompt:**

```python
# agents/conrad_contra/prompt.py

CONRAD_SYSTEM_PROMPT = """Du bist Conrad, der Gegenprüfer im responzai-Prüfteam.

DEINE AUFGABE:
Versuche die folgende, bereits als "verifiziert" eingestufte Behauptung 
zu widerlegen. Sei hartnäckig, aber fair.

DEINE STRATEGIEN:
1. AUSNAHMENSUCHE: Gibt es Fälle, in denen die Behauptung nicht gilt?
   Gibt es Ausnahmen im Gesetz? Sonderfälle?
2. ZEITLICHE PRÜFUNG: Ist die Information möglicherweise veraltet?
   Gibt es neuere Entwicklungen?
3. ANNAHMENPRÜFUNG: Welche versteckten Voraussetzungen stecken in der
   Behauptung? Sind diese Voraussetzungen immer erfüllt?
4. GEGENBEISPIELE: Gibt es konkrete Fälle oder Quellen, die der
   Behauptung widersprechen?

REGELN:
1. Nutze NUR die bereitgestellten Quellenpassagen und die 
   Originalquelle der Behauptung.
2. Wenn du keinen Widerspruch findest, sag das ehrlich.
   Ein Claim, den du nicht widerlegen kannst, ist ein starker Claim.
3. Unterscheide zwischen echten Widersprüchen und Haarspalterei.
4. Gib konkrete Belege für jede Schwäche, die du findest.

BEWERTUNG:
- survived: Du konntest die Behauptung nicht widerlegen. Sie ist robust.
- weakened: Du hast Einschränkungen gefunden, die erwähnt werden sollten.
- refuted: Du hast einen klaren Widerspruch gefunden.

AUSGABEFORMAT (JSON):
{
  "claim_id": "claim_001",
  "result": "survived | weakened | refuted",
  "strategies_applied": [
    {
      "strategy": "AUSNAHMENSUCHE",
      "finding": "Was gefunden wurde",
      "evidence": "Beleg aus den Quellen",
      "severity": "critical | major | minor | none"
    }
  ],
  "overall_assessment": "Zusammenfassende Bewertung",
  "suggested_refinement": "Wie die Behauptung präzisiert werden könnte"
}
"""
```

**Die Widerlegungsstrategien:**

```python
# agents/conrad_contra/strategies.py

import anthropic
from agents.vera_verify.rag_query import find_relevant_chunks

client = anthropic.Anthropic()

async def inverse_rag_search(claim_text: str) -> list:
    """
    Conrads eigene Suche in der Wissensbasis.
    
    Warum eine eigene Suche?
    Vera sucht nach Belegen FÜR die Behauptung.
    Conrad sucht nach Belegen GEGEN die Behauptung.
    Dafür formuliert er die Suchanfrage um.
    
    Beispiel:
    Behauptung: "Art. 4 gilt für alle Unternehmen"
    Conrads Suche: "Ausnahmen Art. 4" und "nicht anwendbar Art. 4"
    """
    # Gegensuche formulieren
    counter_queries = [
        f"Ausnahmen von: {claim_text}",
        f"Einschränkungen: {claim_text}",
        f"Nicht anwendbar: {claim_text}",
        f"Änderung oder Aufhebung: {claim_text}"
    ]
    
    all_chunks = []
    for query in counter_queries:
        chunks = await find_relevant_chunks(query, top_k=3)
        all_chunks.extend(chunks)
    
    # Duplikate entfernen und nach Relevanz sortieren
    seen_ids = set()
    unique_chunks = []
    for chunk in sorted(all_chunks, key=lambda x: x["similarity"], reverse=True):
        if chunk["chunk_id"] not in seen_ids:
            seen_ids.add(chunk["chunk_id"])
            unique_chunks.append(chunk)
    
    return unique_chunks[:5]
```

**Die Bewertungslogik:**

```python
# agents/conrad_contra/evaluation.py

from .prompt import CONRAD_SYSTEM_PROMPT
from .strategies import inverse_rag_search
import anthropic
import json

client = anthropic.Anthropic()

async def challenge_claim(claim: dict, vera_result: dict) -> dict:
    """
    Conrads Hauptfunktion: Versuche, den Claim zu widerlegen.
    
    Conrad bekommt:
    - Den Claim selbst
    - Veras Ergebnis (Score, Quellenpassagen)
    - Eigene Gegenrecherche-Ergebnisse
    """
    # Eigene Gegenrecherche durchführen
    counter_evidence = await inverse_rag_search(claim["claim_text"])
    
    # Kontext aufbereiten
    vera_context = "\n\n".join([
        f"[Veras Quelle: {p['source']}]\n{p['text']}"
        for p in vera_result.get("supporting_passages", [])
    ])
    
    counter_context = "\n\n".join([
        f"[Gegenrecherche: {chunk['source']}]\n{chunk['text']}"
        for chunk in counter_evidence
    ])
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        temperature=0,
        system=CONRAD_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"""BEHAUPTUNG (von Vera als verifiziert eingestuft, Score: {vera_result['score']}):
{claim['claim_text']}

VERAS QUELLENBELEGE:
{vera_context}

ERGEBNISSE DEINER GEGENRECHERCHE:
{counter_context}

Versuche diese Behauptung zu widerlegen. Wende alle vier Strategien an."""
            }
        ]
    )
    
    response_text = message.content[0].text
    json_start = response_text.find("{")
    json_end = response_text.rfind("}") + 1
    result = json.loads(response_text[json_start:json_end])
    
    return result
```

### 8.4 Sven (SYNC) — Konsistenzprüfung

Sven vergleicht alle Claims miteinander und über alle Kanäle hinweg.

**Der Prompt:**

```python
# agents/sven_sync/prompt.py

SVEN_SYSTEM_PROMPT = """Du bist Sven, der Konsistenzprüfer im responzai-Prüfteam.

DEINE AUFGABE:
Vergleiche die folgenden Behauptungen und finde Widersprüche,
Doppelungen und Inkonsistenzen.

PRÜFEBENEN:
1. INTERNE KONSISTENZ: Widersprechen sich Behauptungen auf 
   derselben Seite?
2. KANALÜBERGREIFENDE KONSISTENZ: Sagt die Website etwas 
   anderes als der Newsletter?
3. SEMANTISCHE DUPLIKATE: Wird dasselbe in leicht 
   unterschiedlichen Worten behauptet?
4. IMPLIZITE WIDERSPRÜCHE: Folgen aus zwei Behauptungen 
   zusammen ein Widerspruch?

SCHWEREGRADE:
- critical: Direkter inhaltlicher Widerspruch.
- major: Unterschiedliche Zahlen, Daten oder Einschränkungen.
- minor: Unterschiedliche Formulierungen desselben Sachverhalts.

AUSGABEFORMAT (JSON):
{
  "contradictions": [
    {
      "claim_a_id": "claim_001",
      "claim_b_id": "claim_015",
      "type": "KANALÜBERGREIFEND",
      "severity": "major",
      "description": "Was sich widerspricht",
      "source_a": "Website: /produkte",
      "source_b": "Newsletter Ausgabe 23",
      "suggested_resolution": "Vorschlag zur Auflösung"
    }
  ],
  "duplicates": [
    {
      "claims": ["claim_003", "claim_012"],
      "similarity": 0.92,
      "note": "Gleiche Aussage, unterschiedliche Formulierung"
    }
  ],
  "consistency_score": 0.85
}
"""
```

**Die Konsistenzprüfung:**

```python
# agents/sven_sync/consistency.py

import asyncpg
import numpy as np
from processing.embedding import create_embeddings

async def find_similar_claims(claims: list, threshold: float = 0.85) -> list:
    """
    Findet Behauptungen, die sich ähnlich sind.
    
    Warum?
    Ähnliche Behauptungen könnten sich widersprechen.
    Wenn auf der Website steht "ab Februar 2025" und im 
    Newsletter "ab März 2025", dann ist das ein Problem.
    
    threshold=0.85 bedeutet: Wir suchen nach Behauptungen,
    die zu mindestens 85% ähnlich sind.
    """
    # Embeddings für alle Claims erzeugen
    claim_texts = [c["claim_text"] for c in claims]
    embeddings = create_embeddings(claim_texts)
    
    # Ähnlichkeiten berechnen
    pairs = []
    for i in range(len(claims)):
        for j in range(i + 1, len(claims)):
            # Kosinus-Ähnlichkeit berechnen
            similarity = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            
            if similarity >= threshold:
                pairs.append({
                    "claim_a": claims[i],
                    "claim_b": claims[j],
                    "similarity": float(similarity)
                })
    
    return pairs
```

### 8.5 Pia (PULSE) — Aktualitätsprüfung

Pia erkennt Zeitbezüge und prüft die Aktualität der Quellen.

**Der Prompt:**

```python
# agents/pia_pulse/prompt.py

PIA_SYSTEM_PROMPT = """Du bist Pia, die Aktualitätsprüferin im responzai-Prüfteam.

DEINE AUFGABE:
Prüfe jede Behauptung auf Zeitbezüge und Aktualität.

WAS DU PRÜFST:
1. Enthält die Behauptung explizite Zeitangaben? 
   (Daten, Fristen, "aktuell", "seit", "ab")
2. Wann wurde die zugrundeliegende Quelle zuletzt aktualisiert?
3. Gibt es neuere Versionen der referenzierten Dokumente?
4. Sind genannte Fristen abgelaufen oder stehen sie bevor?

BEWERTUNG:
- fresh: Quelle ist aktuell, keine Änderungen bekannt.
- stale: Quelle ist älter als 3 Monate, aber inhaltlich noch gültig.
- outdated: Quelle wurde aktualisiert oder durch neuere ersetzt.
- expiring: Eine genannte Frist steht in den nächsten 30 Tagen bevor.

AUSGABEFORMAT (JSON):
{
  "claim_id": "claim_001",
  "time_references": ["Februar 2025", "Artikel 113"],
  "freshness": "stale",
  "source_last_updated": "2024-07-12",
  "latest_version_available": "2025-01-15",
  "days_since_update": 242,
  "upcoming_deadlines": [],
  "update_suggestion": "Formulierung anpassen: 'seit Februar 2025 in Kraft' statt 'ab Februar 2025'"
}
"""
```

**Die Monitoring-Logik:**

```python
# agents/pia_pulse/monitors.py

import feedparser
from datetime import datetime

# EUR-Lex RSS-Feed für den AI Act
EURLEX_FEED = "https://eur-lex.europa.eu/rss/search-result.xml?qid=..."

def check_eurlex_updates() -> list:
    """
    Prüft den EUR-Lex RSS-Feed auf neue Veröffentlichungen.
    
    Warum RSS?
    EUR-Lex bietet RSS-Feeds an, die automatisch aktualisiert
    werden, wenn neue Dokumente veröffentlicht werden.
    So muss Pia nicht die ganze Website durchsuchen.
    """
    feed = feedparser.parse(EURLEX_FEED)
    
    updates = []
    for entry in feed.entries:
        published = datetime(*entry.published_parsed[:6])
        updates.append({
            "title": entry.title,
            "url": entry.link,
            "published": published.isoformat(),
            "summary": entry.summary
        })
    
    return updates


def check_freshness(claim_date: str, source_date: str) -> dict:
    """
    Vergleicht das Datum einer Behauptung mit dem Datum der Quelle.
    
    Einfache Logik:
    - Quelle jünger als 30 Tage → fresh
    - Quelle 30 bis 90 Tage alt → stale
    - Quelle älter als 90 Tage → outdated
    """
    source_dt = datetime.fromisoformat(source_date)
    days_old = (datetime.now() - source_dt).days
    
    if days_old <= 30:
        return {"freshness": "fresh", "days_old": days_old}
    elif days_old <= 90:
        return {"freshness": "stale", "days_old": days_old}
    else:
        return {"freshness": "outdated", "days_old": days_old}
```

---

## 9. Verbesserungsteam umsetzen

### 9.1 Lena (LEGAL) — Rechtliche Aktualisierung

Lena ist der sensibelste Agent, weil sie Texte generiert, die inhaltlich korrekt sein müssen. Deshalb hat sie die strengsten Sicherheitsmechanismen.

**Der Prompt (mit Anti-Halluzinations-Regeln):**

```python
# agents/lena_legal/prompt.py

LENA_SYSTEM_PROMPT = """Du bist Lena, die juristische Textredakteurin 
im responzai-Verbesserungsteam.

STRIKTE REGELN (NICHT VERHANDELBAR):

1. Du darfst NUR Informationen verwenden, die in den mitgelieferten 
   source_passages enthalten sind.

2. Jeder Satz, den du schreibst, MUSS mit einer Quellenreferenz enden:
   [Quelle: EU AI Act, Art. 4]

3. Wenn die source_passages nicht ausreichen, um eine Aussage zu belegen, 
   schreibe KEINE Aussage. Stattdessen markiere eine Lücke:
   [LÜCKE: Keine Quelle verfügbar für ...]

4. Du darfst Formulierungen vereinfachen, aber KEINE inhaltlichen 
   Ergänzungen machen, die nicht in den Quellen stehen.

5. Verwende NIEMALS Wissen, das nicht in den source_passages vorkommt.

6. Generiere NUR die Änderung (Diff), nicht den kompletten Text.
   Zeige: Was steht da? Was soll da stehen? Warum?

DEIN OUTPUT-FORMAT (JSON):
{
  "claim_id": "claim_001",
  "change_type": "update | correction | addition | removal",
  "current_text": "Der bestehende Text",
  "suggested_text": "Der vorgeschlagene neue Text [Quelle: ...]",
  "sources_used": [
    {
      "hash": "abc123",
      "source": "EU AI Act, Art. 4",
      "passage": "Die verwendete Stelle"
    }
  ],
  "coverage": 0.98,
  "gaps": [],
  "reasoning": "Warum diese Änderung nötig ist"
}
"""
```

**Die Quellen-Binding-Prüfung:**

```python
# agents/lena_legal/verification_loop.py

import hashlib

def verify_source_binding(lena_output: dict, provided_sources: list) -> dict:
    """
    Prüft, ob Lena sich wirklich nur auf die mitgelieferten Quellen bezieht.
    
    Warum ist das wichtig?
    Lena könnte "halluzinieren", also Informationen erfinden, die 
    plausibel klingen, aber nicht in den Quellen stehen. Diese Prüfung
    stellt sicher, dass jede Quellenreferenz in Lenas Output tatsächlich
    auf eine echte Quelle zurückgeht.
    
    Wie funktioniert das?
    Jede Quelle bekommt einen digitalen Fingerabdruck (Hash).
    Wir prüfen, ob alle Fingerabdrücke, die Lena nennt, auch
    in den bereitgestellten Quellen vorkommen.
    """
    # Hashes der bereitgestellten Quellen berechnen
    source_hashes = set()
    for source in provided_sources:
        hash_value = hashlib.sha256(source["text"].encode()).hexdigest()[:12]
        source_hashes.add(hash_value)
    
    # Hashes in Lenas Output prüfen
    used_hashes = set()
    for ref in lena_output.get("sources_used", []):
        used_hashes.add(ref["hash"])
    
    # Gibt es Quellen, die Lena nennt, die wir nicht kennen?
    unknown_sources = used_hashes - source_hashes
    
    if unknown_sources:
        return {
            "status": "REJECTED",
            "reason": f"Lena referenziert unbekannte Quellen: {unknown_sources}",
            "action": "Lenas Vorschlag wird verworfen. Bitte manuell prüfen."
        }
    
    # Quellenabdeckung prüfen
    if lena_output.get("coverage", 0) < 0.95:
        return {
            "status": "REVIEW",
            "reason": f"Quellenabdeckung nur {lena_output['coverage']*100:.0f}%",
            "action": "Lenas Vorschlag braucht menschliche Prüfung."
        }
    
    return {
        "status": "ACCEPTED",
        "reason": "Alle Quellen verifiziert, Abdeckung ausreichend."
    }


async def run_verification_loop(lena_output: dict, claim: dict):
    """
    Die Rückprüfungsschleife: Lenas Vorschlag geht nochmal durch 
    Vera und Conrad.
    
    Ablauf:
    1. Lena generiert einen Textvorschlag.
    2. Quellen-Binding wird geprüft (Funktion oben).
    3. Vera prüft den neuen Text gegen die Wissensbasis.
    4. Conrad versucht, den neuen Text zu widerlegen.
    5. Nur wenn alles besteht, wird der Vorschlag akzeptiert.
    """
    from agents.vera_verify.scoring import verify_claim
    from agents.conrad_contra.evaluation import challenge_claim
    
    # Schritt 1: Quellen-Binding prüfen
    binding_check = verify_source_binding(lena_output, claim["source_passages"])
    if binding_check["status"] == "REJECTED":
        return binding_check
    
    # Schritt 2: Neuen Claim aus Lenas Vorschlag erstellen
    new_claim = {
        "claim_text": lena_output["suggested_text"],
        "category": claim["category"],
        "source_url": claim["source_url"]
    }
    
    # Schritt 3: Vera prüft den neuen Text
    vera_result = await verify_claim(new_claim)
    if vera_result["score"] < 0.9:
        return {
            "status": "REJECTED",
            "reason": f"Vera gibt dem neuen Text nur Score {vera_result['score']}",
            "vera_feedback": vera_result
        }
    
    # Schritt 4: Conrad prüft den neuen Text
    conrad_result = await challenge_claim(new_claim, vera_result)
    if conrad_result["result"] == "refuted":
        return {
            "status": "REJECTED",
            "reason": "Conrad hat den neuen Text widerlegt",
            "conrad_feedback": conrad_result
        }
    
    return {
        "status": "ACCEPTED",
        "lena_output": lena_output,
        "vera_score": vera_result["score"],
        "conrad_result": conrad_result["result"]
    }
```

### 9.2 David (DRAFT) — Textoptimierung

David verbessert Texte sprachlich, basierend auf dem responzai-Stilguide.

**Der Prompt:**

```python
# agents/david_draft/prompt.py

DAVID_SYSTEM_PROMPT = """Du bist David, der Textoptimierer im 
responzai-Verbesserungsteam.

DEIN STILGUIDE (responzai-Standard):

1. VERSTÄNDLICHKEIT: Wenn ein Zehnjähriger den Satz nicht versteht, 
   schreibe ihn um.
2. KÜRZE: Kurze Sätze. Maximal 15 Wörter pro Satz als Richtwert.
3. WÖRTER: Alltägliche Wörter statt Fachsprache. Wenn Fachsprache 
   nötig ist, erkläre sie sofort im nächsten Satz.
4. FORM: Aktiv statt passiv. "Prüfen Sie..." statt "Es ist zu prüfen..."
5. HANDLUNG: Konkrete Handlungsanweisungen statt vager Empfehlungen.
   "Tragen Sie hier den Namen ein" statt "Der Name sollte angegeben werden"
6. VERBOTEN: Keine Gedankenstriche. Keine abgenutzten Metaphern.
   Keine pseudokreativen Sprachbilder. Kein "Hand aufs Herz".
   Kein "Technikgewitter". Kein "Cloudnebel".
7. SATZANFANG: Lieber ein Satz mehr als ein unverständlicher Satz.

DEINE AUFGABE:
Optimiere den folgenden Text nach diesen Regeln. Zeige für jede 
Änderung: Was steht da? Was soll da stehen? Warum?

AUSGABEFORMAT (JSON):
{
  "changes": [
    {
      "current_text": "Die Implementierung der in Art. 9 Abs. 2 
                       normierten Verpflichtung ist zeitnah 
                       sicherzustellen.",
      "suggested_text": "Starten Sie die Risikobewertung bis zum 
                         [Datum]. Artikel 9 Absatz 2 schreibt das vor.",
      "reason": "Nominalstil aufgelöst. Passive Konstruktion durch 
                 direkte Handlungsanweisung ersetzt. Frist konkretisiert.",
      "category": "readability"
    }
  ],
  "readability_score_before": 35,
  "readability_score_after": 72,
  "summary": "5 Änderungen: 3x Nominalstil aufgelöst, 
              1x Schachtelsatz vereinfacht, 1x Fachbegriff erklärt"
}
"""
```

### 9.3 Uma (UX) — Bedienungsfreundlichkeit

Uma prüft Dokumente aus Nutzerperspektive.

**Der Prompt:**

```python
# agents/uma_ux/prompt.py

UMA_SYSTEM_PROMPT = """Du bist Uma, die UX-Expertin im 
responzai-Verbesserungsteam.

DEINE PERSPEKTIVE:
Du bist NICHT die Person, die das Dokument geschrieben hat.
Du bist die Person, die es zum ersten Mal in den Händen hält 
und damit arbeiten muss.

DEINE PRÜFKRITERIEN:

1. ORIENTIERUNG: Weiß ich nach 10 Sekunden, was dieses 
   Dokument ist und was ich damit tun soll?
2. REIHENFOLGE: Ist die Reihenfolge logisch? Kommt zuerst, 
   was ich zuerst brauche?
3. AUSFÜLLHILFEN: Steht bei jedem Feld, was ich eintragen soll? 
   Gibt es ein Beispiel?
4. GRUPPIERUNG: Sind lange Listen sinnvoll in Blöcke aufgeteilt?
5. ZUSTÄNDIGKEIT: Ist klar, wer welchen Abschnitt ausfüllt?
6. VOLLSTÄNDIGKEIT: Fehlt etwas, das ein Anwender braucht?
7. ÜBERFORDERUNG: Gibt es Stellen, die unnötig kompliziert sind?

BEWERTUNGSSKALA PRO KRITERIUM:
- gut: Keine Änderung nötig.
- verbesserungswürdig: Funktioniert, könnte aber besser sein.
- problematisch: Anwender werden hier Schwierigkeiten haben.
- kritisch: Anwender werden hier scheitern oder Fehler machen.

AUSGABEFORMAT (JSON):
{
  "overall_usability": "verbesserungswürdig",
  "issues": [
    {
      "section": "Anhang C: Checkliste",
      "criterion": "GRUPPIERUNG",
      "severity": "problematisch",
      "issue": "23 Punkte ohne Gruppierung. Anwender verliert 
               den Überblick.",
      "suggestion": "Aufteilen in drei Blöcke: Vorbereitung (1 bis 8), 
                     Durchführung (9 bis 17), Nachbereitung (18 bis 23). 
                     Verantwortliche Rolle pro Block ergänzen.",
      "effort": "niedrig"
    }
  ],
  "quick_wins": ["Die einfachsten Verbesserungen mit größter Wirkung"],
  "priority_order": ["In dieser Reihenfolge umsetzen"]
}
"""
```

---

## 10. Pipeline-Orchestrierung mit LangGraph

### 10.1 Was ist LangGraph?

LangGraph ist ein Framework, das die Reihenfolge und Logik der Agenten steuert. Stell es dir wie ein Gleissystem vor: Es bestimmt, welcher Agent wann dran ist und was passiert, wenn ein Agent "Halt" sagt.

### 10.2 Die Pipeline als Graph

```python
# pipeline/orchestrator.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import json

# Der "State" ist der Zustand, der durch die Pipeline fließt.
# Jeder Agent liest daraus und schreibt hinein.

class PipelineState(TypedDict):
    # Eingabe
    source_url: str
    source_text: str
    
    # Simon (SCOUT)
    claims: List[dict]
    
    # Vera (VERIFY)
    verified_claims: List[dict]
    unverified_claims: List[dict]
    
    # Conrad (CONTRA)
    survived_claims: List[dict]
    weakened_claims: List[dict]
    refuted_claims: List[dict]
    
    # Sven (SYNC)
    contradictions: List[dict]
    consistency_score: float
    
    # Pia (PULSE)
    freshness_results: List[dict]
    
    # Lena (LEGAL)
    legal_updates: List[dict]
    
    # David (DRAFT)
    text_improvements: List[dict]
    
    # Uma (UX)
    ux_issues: List[dict]
    
    # Berichte
    verification_report: Optional[dict]
    improvement_report: Optional[dict]


# Die einzelnen Schritte der Pipeline

async def simon_step(state: PipelineState) -> PipelineState:
    """Simon extrahiert Claims aus dem Text."""
    from agents.simon_scout.parser import extract_claims
    from agents.simon_scout.crawler import crawl_page
    
    # Wenn eine URL gegeben ist, zuerst crawlen
    if state["source_url"] and not state["source_text"]:
        page = crawl_page(state["source_url"])
        state["source_text"] = page["text"]
    
    # Claims extrahieren
    result = await extract_claims(state["source_text"], state["source_url"])
    state["claims"] = result["claims"]
    
    print(f"Simon: {len(state['claims'])} Claims gefunden.")
    return state


async def vera_step(state: PipelineState) -> PipelineState:
    """Vera prüft jeden Claim gegen die Wissensbasis."""
    from agents.vera_verify.scoring import verify_claim
    
    verified = []
    unverified = []
    
    for claim in state["claims"]:
        result = await verify_claim(claim)
        claim["vera_result"] = result
        
        if result["score"] >= 0.8:
            verified.append(claim)
        else:
            unverified.append(claim)
    
    state["verified_claims"] = verified
    state["unverified_claims"] = unverified
    
    print(f"Vera: {len(verified)} verifiziert, {len(unverified)} unsicher.")
    return state


async def conrad_step(state: PipelineState) -> PipelineState:
    """Conrad versucht, die verifizierten Claims zu widerlegen."""
    from agents.conrad_contra.evaluation import challenge_claim
    
    survived = []
    weakened = []
    refuted = []
    
    for claim in state["verified_claims"]:
        result = await challenge_claim(claim, claim["vera_result"])
        claim["conrad_result"] = result
        
        if result["result"] == "survived":
            survived.append(claim)
        elif result["result"] == "weakened":
            weakened.append(claim)
        else:
            refuted.append(claim)
    
    state["survived_claims"] = survived
    state["weakened_claims"] = weakened
    state["refuted_claims"] = refuted
    
    print(f"Conrad: {len(survived)} überlebt, {len(weakened)} geschwächt, {len(refuted)} widerlegt.")
    return state


async def sven_step(state: PipelineState) -> PipelineState:
    """Sven prüft die Konsistenz aller Claims."""
    from agents.sven_sync.consistency import find_similar_claims
    
    # Alle Claims, die noch im Rennen sind
    all_active = state["survived_claims"] + state["weakened_claims"]
    
    similar_pairs = await find_similar_claims(all_active)
    
    # TODO: Für jedes ähnliche Paar prüfen, ob sie sich widersprechen
    # (Hier kommt Svens Claude-Aufruf)
    
    state["contradictions"] = []  # Wird befüllt
    state["consistency_score"] = 0.0  # Wird berechnet
    
    print(f"Sven: {len(similar_pairs)} ähnliche Paare gefunden.")
    return state


async def pia_step(state: PipelineState) -> PipelineState:
    """Pia prüft die Aktualität aller Claims."""
    from agents.pia_pulse.monitors import check_eurlex_updates, check_freshness
    
    freshness_results = []
    
    for claim in state["survived_claims"] + state["weakened_claims"]:
        # Zeitbezüge im Claim finden und Aktualität prüfen
        # (Vereinfachte Version)
        result = {
            "claim_id": claim["id"],
            "freshness": "fresh",  # Wird durch Pias Claude-Aufruf bestimmt
        }
        freshness_results.append(result)
    
    state["freshness_results"] = freshness_results
    
    print(f"Pia: {len(freshness_results)} Claims auf Aktualität geprüft.")
    return state


async def lena_step(state: PipelineState) -> PipelineState:
    """Lena generiert rechtliche Aktualisierungen."""
    from agents.lena_legal.verification_loop import run_verification_loop
    
    legal_updates = []
    
    # Lena arbeitet nur an Claims, die Probleme haben
    problematic = state["weakened_claims"] + state["refuted_claims"]
    problematic += [c for c in state["freshness_results"] 
                    if c.get("freshness") in ["stale", "outdated"]]
    
    for claim in problematic:
        # Lena generiert Vorschlag + Rückprüfung
        result = await run_verification_loop(claim.get("lena_output", {}), claim)
        legal_updates.append(result)
    
    state["legal_updates"] = legal_updates
    
    print(f"Lena: {len(legal_updates)} rechtliche Updates vorgeschlagen.")
    return state


async def david_step(state: PipelineState) -> PipelineState:
    """David optimiert die Texte sprachlich."""
    # David arbeitet an allen Texten, nicht nur an problematischen
    state["text_improvements"] = []  # Wird befüllt
    
    print("David: Textoptimierung abgeschlossen.")
    return state


async def uma_step(state: PipelineState) -> PipelineState:
    """Uma prüft die Bedienungsfreundlichkeit."""
    state["ux_issues"] = []  # Wird befüllt
    
    print("Uma: UX-Prüfung abgeschlossen.")
    return state


async def generate_reports(state: PipelineState) -> PipelineState:
    """Erstellt die finalen Berichte."""
    from pipeline.reporting import create_verification_report, create_improvement_report
    
    state["verification_report"] = create_verification_report(state)
    state["improvement_report"] = create_improvement_report(state)
    
    print("Berichte erstellt.")
    return state


# Den Graphen zusammenbauen

def build_pipeline():
    """
    Baut die LangGraph-Pipeline zusammen.
    
    Die Pipeline hat zwei Phasen:
    Phase 1 (Prüfung): Simon → Vera → Conrad → Sven → Pia
    Phase 2 (Verbesserung): Lena → David → Uma → Berichte
    """
    workflow = StateGraph(PipelineState)
    
    # Knoten hinzufügen (jeder Agent ist ein Knoten)
    workflow.add_node("simon", simon_step)
    workflow.add_node("vera", vera_step)
    workflow.add_node("conrad", conrad_step)
    workflow.add_node("sven", sven_step)
    workflow.add_node("pia", pia_step)
    workflow.add_node("lena", lena_step)
    workflow.add_node("david", david_step)
    workflow.add_node("uma", uma_step)
    workflow.add_node("reports", generate_reports)
    
    # Kanten hinzufügen (die Reihenfolge)
    workflow.set_entry_point("simon")
    workflow.add_edge("simon", "vera")
    workflow.add_edge("vera", "conrad")
    workflow.add_edge("conrad", "sven")
    workflow.add_edge("sven", "pia")
    workflow.add_edge("pia", "lena")
    workflow.add_edge("lena", "david")
    workflow.add_edge("david", "uma")
    workflow.add_edge("uma", "reports")
    workflow.add_edge("reports", END)
    
    return workflow.compile()
```

### 10.3 Die Pipeline starten

```python
# pipeline/config.py

# Schwellenwerte für die Pipeline
VERIFICATION_THRESHOLD = 0.8   # Mindest-Score für Vera
ADVERSARIAL_PASS = ["survived", "weakened"]  # Conrad: welche Ergebnisse ok sind
CONSISTENCY_THRESHOLD = 0.7    # Mindest-Score für Sven
FRESHNESS_MAX_DAYS = 90        # Pia: ab wann eine Quelle "stale" ist
LEGAL_COVERAGE_MIN = 0.95      # Lena: Mindest-Quellenabdeckung

# Modell-Konfiguration
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_TEMPERATURE = 0            # Keine Kreativität bei Prüfungen
EMBEDDING_MODEL = "voyage-3"
```

---

## 11. Automatisierung mit n8n

### 11.1 Was ist n8n?

n8n ist ein Automatisierungswerkzeug. Es verbindet verschiedene Dienste miteinander und führt Abläufe automatisch aus. Stell dir n8n wie einen unsichtbaren Assistenten vor, der jeden Montag um 6 Uhr morgens den Verifier startet, den Bericht per E-Mail verschickt und bei Problemen sofort Alarm schlägt.

### 11.2 n8n einrichten

n8n läuft bereits als Docker-Container (siehe Kapitel 4.7). Du erreichst es über den Browser:

```
http://DEINE-IP:5678
```

Beim ersten Mal richtest du ein Konto ein. Danach siehst du die n8n-Oberfläche.

### 11.3 Workflow 1: Wöchentlicher Prüflauf

**Was dieser Workflow tut:**
Jeden Montagmorgen um 6:00 Uhr wird die Website responzai.eu automatisch geprüft. Das Ergebnis kommt als E-Mail.

**Node-Konfiguration (Copy-Paste-fertig):**

**Node 1: Cron (Zeitplan)**
```json
{
  "name": "Wöchentlicher Trigger",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "triggerTimes": {
      "item": [
        {
          "mode": "everyWeek",
          "hour": 6,
          "minute": 0,
          "weekday": 1
        }
      ]
    }
  }
}
```

Was das tut: Startet den Workflow jeden Montag (weekday: 1) um 6:00 Uhr.

**Node 2: HTTP Request (Prüfung anstoßen)**
```json
{
  "name": "Verifier API aufrufen",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://verifier:8000/verify",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "url",
          "value": "https://responzai.eu"
        },
        {
          "name": "mode",
          "value": "full"
        }
      ]
    },
    "options": {
      "timeout": 300000
    }
  }
}
```

Was das tut: Sendet einen Auftrag an den Verifier, die gesamte Website zu prüfen. Der Timeout von 300.000 Millisekunden (5 Minuten) gibt dem System genug Zeit.

**Node 3: IF (Probleme gefunden?)**
```json
{
  "name": "Probleme gefunden?",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "number": [
        {
          "value1": "={{$json.issues_found}}",
          "operation": "larger",
          "value2": 0
        }
      ]
    }
  }
}
```

Was das tut: Prüft, ob der Verifier Probleme gefunden hat. Wenn ja, geht es zum Alarm-Pfad. Wenn nein, zum normalen Report.

**Node 4a: E-Mail (Normaler Report)**
```json
{
  "name": "Report per E-Mail",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "verifier@responzai.eu",
    "toEmail": "DEINE-EMAIL",
    "subject": "responzai Prüfbericht KW {{$now.format('WW')}}",
    "text": "Prüfbericht für responzai.eu\n\nGeprüfte Claims: {{$json.total_claims}}\nVerifiziert: {{$json.verified_claims}}\nProbleme: {{$json.issues_found}}\n\nDetails im Dashboard: https://DEINE-DOMAIN/reports"
  }
}
```

**Node 4b: E-Mail (Alarm bei Problemen)**
```json
{
  "name": "Alarm bei Problemen",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "verifier@responzai.eu",
    "toEmail": "DEINE-EMAIL",
    "subject": "⚠ responzai: {{$json.issues_found}} Probleme gefunden",
    "text": "ACHTUNG: Der wöchentliche Prüflauf hat {{$json.issues_found}} Probleme gefunden.\n\nKritische Befunde:\n{{$json.critical_issues}}\n\nBitte prüfe die Ergebnisse: https://DEINE-DOMAIN/reports"
  }
}
```

### 11.4 Workflow 2: EUR-Lex Monitoring (für Pia)

**Was dieser Workflow tut:**
Täglich um 7:00 Uhr prüft Pia, ob es neue Veröffentlichungen zum AI Act gibt.

**Node 1: Cron (Täglich)**
```json
{
  "name": "Täglicher Check",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "triggerTimes": {
      "item": [
        {
          "mode": "everyDay",
          "hour": 7,
          "minute": 0
        }
      ]
    }
  }
}
```

**Node 2: RSS Feed lesen**
```json
{
  "name": "EUR-Lex Feed",
  "type": "n8n-nodes-base.rssFeedRead",
  "parameters": {
    "url": "https://eur-lex.europa.eu/rss/search-result.xml?qid=AI_ACT_FEED_ID"
  }
}
```

**Node 3: IF (Neue Einträge?)**
```json
{
  "name": "Neue Einträge?",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "dateTime": [
        {
          "value1": "={{$json.pubDate}}",
          "operation": "after",
          "value2": "={{$now.minus({days: 1}).toISO()}}"
        }
      ]
    }
  }
}
```

Was das tut: Prüft, ob der Eintrag von heute ist (innerhalb der letzten 24 Stunden). Nur neue Einträge gehen weiter.

**Node 4: HTTP Request (Wissensbasis aktualisieren)**
```json
{
  "name": "Wissensbasis aktualisieren",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://verifier:8000/knowledge/update",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "source_url",
          "value": "={{$json.link}}"
        },
        {
          "name": "source_type",
          "value": "primary"
        }
      ]
    }
  }
}
```

**Node 5: E-Mail (Benachrichtigung)**
```json
{
  "name": "Update-Benachrichtigung",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "pia@responzai.eu",
    "toEmail": "DEINE-EMAIL",
    "subject": "Pia: Neue EUR-Lex Veröffentlichung",
    "text": "Pia hat eine neue Veröffentlichung gefunden:\n\n{{$json.title}}\n{{$json.link}}\n\nDie Wissensbasis wird automatisch aktualisiert. Ein neuer Prüflauf wird empfohlen."
  }
}
```

### 11.5 Workflow 3: Newsletter-Prüfung

**Was dieser Workflow tut:**
Wenn ein neuer Newsletter veröffentlicht wird, wird er automatisch geprüft und in die Wissensbasis aufgenommen.

**Node 1: Webhook (Trigger)**
```json
{
  "name": "Neuer Newsletter",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "path": "newsletter-published",
    "httpMethod": "POST"
  }
}
```

Was das tut: Wartet auf einen Aufruf von außen. Wenn du den Newsletter veröffentlichst, kann dein System diesen Webhook aufrufen: `POST http://DEINE-IP:5678/webhook/newsletter-published`

**Node 2: HTTP Request (In Wissensbasis aufnehmen)**
```json
{
  "name": "In Wissensbasis aufnehmen",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://verifier:8000/knowledge/ingest",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "content",
          "value": "={{$json.body.newsletter_text}}"
        },
        {
          "name": "source_type",
          "value": "own"
        },
        {
          "name": "source_name",
          "value": "Newsletter {{$json.body.edition}}"
        }
      ]
    }
  }
}
```

**Node 3: HTTP Request (Prüflauf anstoßen)**
```json
{
  "name": "Newsletter prüfen",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://verifier:8000/verify",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "text",
          "value": "={{$json.body.newsletter_text}}"
        },
        {
          "name": "mode",
          "value": "full"
        }
      ]
    }
  }
}
```

**Node 4: E-Mail (Ergebnis)**
```json
{
  "name": "Prüfergebnis senden",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "verifier@responzai.eu",
    "toEmail": "DEINE-EMAIL",
    "subject": "Newsletter-Prüfung: {{$json.total_claims}} Claims, {{$json.issues_found}} Probleme",
    "text": "Der neue Newsletter wurde geprüft.\n\nErgebnis:\n- Claims: {{$json.total_claims}}\n- Verifiziert: {{$json.verified_claims}}\n- Probleme: {{$json.issues_found}}\n\nDetails: https://DEINE-DOMAIN/reports"
  }
}
```

### 11.6 Workflow 4: GUIDES-Verbesserung

**Was dieser Workflow tut:**
Einmal im Monat prüft das Verbesserungsteam (Lena, David, Uma) alle GUIDES-Vorlagen und erstellt einen Änderungsbericht.

**Node 1: Cron (Monatlich)**
```json
{
  "name": "Monatlicher GUIDES-Check",
  "type": "n8n-nodes-base.cron",
  "parameters": {
    "triggerTimes": {
      "item": [
        {
          "mode": "everyMonth",
          "hour": 8,
          "minute": 0,
          "dayOfMonth": 1
        }
      ]
    }
  }
}
```

**Node 2: HTTP Request (Verbesserungspipeline)**
```json
{
  "name": "GUIDES verbessern",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "http://verifier:8000/improve",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "target",
          "value": "guides"
        },
        {
          "name": "agents",
          "value": "lena,david,uma"
        }
      ]
    },
    "options": {
      "timeout": 600000
    }
  }
}
```

**Node 3: E-Mail (Änderungsbericht)**
```json
{
  "name": "Änderungsbericht senden",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "verifier@responzai.eu",
    "toEmail": "DEINE-EMAIL",
    "subject": "GUIDES Monatsbericht: {{$json.changes_required}} Änderungen vorgeschlagen",
    "text": "Das Verbesserungsteam hat die GUIDES geprüft.\n\nLena (Recht): {{$json.legal_updates}} Updates\nDavid (Text): {{$json.text_improvements}} Verbesserungen\nUma (UX): {{$json.ux_issues}} Vorschläge\n\nBitte prüfe und gib die Änderungen frei:\nhttps://DEINE-DOMAIN/reports/improvement"
  }
}
```

---

## 12. Integration mit responzai.eu

### 12.1 API-Endpunkte

Die API verbindet die Website mit dem Verifier.

```python
# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="responzai Verifier API",
    description="Multi-Agent Verification System für responzai",
    version="1.0.0"
)

# CORS erlauben (damit die Website auf die API zugreifen kann)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://responzai.eu"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

```python
# api/routes/verify.py

from fastapi import APIRouter
from pipeline.orchestrator import build_pipeline

router = APIRouter()

@router.post("/verify")
async def verify_content(url: str = None, text: str = None, mode: str = "full"):
    """
    Startet einen Prüflauf.
    
    Parameter:
    - url: Eine URL, die geprüft werden soll
    - text: Alternativ ein Text direkt
    - mode: "full" (alle Agenten) oder "quick" (nur Simon + Vera)
    
    Rückgabe:
    Der vollständige Prüfbericht als JSON.
    """
    pipeline = build_pipeline()
    
    initial_state = {
        "source_url": url or "",
        "source_text": text or "",
        "claims": [],
        "verified_claims": [],
        "unverified_claims": [],
        "survived_claims": [],
        "weakened_claims": [],
        "refuted_claims": [],
        "contradictions": [],
        "consistency_score": 0.0,
        "freshness_results": [],
        "legal_updates": [],
        "text_improvements": [],
        "ux_issues": [],
        "verification_report": None,
        "improvement_report": None
    }
    
    result = await pipeline.ainvoke(initial_state)
    
    return {
        "total_claims": len(result["claims"]),
        "verified_claims": len(result["verified_claims"]),
        "issues_found": len(result["refuted_claims"]) + len(result["weakened_claims"]),
        "critical_issues": [c for c in result["refuted_claims"]],
        "report": result["verification_report"]
    }
```

### 12.2 Verification Badge für die Website

Eine kleine React-Komponente, die den letzten Prüfstatus anzeigt:

```jsx
// src/components/VerificationBadge.jsx

import React, { useState, useEffect } from 'react';

export default function VerificationBadge() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://api.responzai.eu/reports/latest')
      .then(res => res.json())
      .then(data => {
        setStatus(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return null;
  if (!status) return null;

  const isHealthy = status.issues_found === 0;

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      padding: '6px 12px',
      borderRadius: '20px',
      fontSize: '13px',
      backgroundColor: isHealthy ? '#e8f5e9' : '#fff3e0',
      color: isHealthy ? '#2e7d32' : '#e65100'
    }}>
      <span style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        backgroundColor: isHealthy ? '#4caf50' : '#ff9800'
      }} />
      <span>
        Letzte Prüfung: {new Date(status.created_at).toLocaleDateString('de-DE')}
        {' · '}
        {status.total_claims} Claims geprüft
        {status.issues_found > 0 && ` · ${status.issues_found} in Bearbeitung`}
      </span>
    </div>
  );
}
```

### 12.3 Die Prüfseite: Dokumente hochladen und prüfen

Die Prüfseite ist der zentrale Ort, an dem Nutzer Dokumente prüfen lassen. Sie bietet drei Wege: URL eingeben, Text einfügen oder Datei hochladen. Die Seite zeigt den Fortschritt in Echtzeit und das Ergebnis als übersichtliches Dashboard.

**Die Seitenstruktur:**

```
┌──────────────────────────────────────────────────────┐
│  responzai Verifier                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Was möchten Sie prüfen?                             │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  🔗 URL  │  │  📝 Text │  │  📄 Datei│           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                      │
│  ┌────────────────────────────────────────────┐      │
│  │                                            │      │
│  │     Datei hierher ziehen                   │      │
│  │     oder klicken zum Auswählen             │      │
│  │                                            │      │
│  │     PDF, Word, Excel, PowerPoint,          │      │
│  │     Bilder, E-Mails und mehr               │      │
│  │     (max. 50 MB)                           │      │
│  │                                            │      │
│  └────────────────────────────────────────────┘      │
│                                                      │
│  Modus: ○ Schnellprüfung  ● Vollständige Prüfung    │
│                                                      │
│  [ Prüfung starten ]                                 │
│                                                      │
├──────────────────────────────────────────────────────┤
│  FORTSCHRITT (erscheint nach Start)                  │
│                                                      │
│  ✅ Simon: 23 Behauptungen gefunden                  │
│  ✅ Vera: 19 verifiziert, 4 unsicher                 │
│  🔄 Conrad: Gegenprüfung läuft...                   │
│  ⏳ Sven: Wartet...                                  │
│  ⏳ Pia: Wartet...                                   │
│                                                      │
│  ████████████░░░░░░░░  40%                           │
├──────────────────────────────────────────────────────┤
│  ERGEBNIS (erscheint wenn fertig)                    │
│                                                      │
│  23 Behauptungen · 17 bestätigt · 4 geschwächt ·    │
│  2 widerlegt · Gesamtscore: 0.78                     │
│                                                      │
│  [ Vollständigen Bericht anzeigen ]                  │
│  [ Bericht als PDF herunterladen ]                   │
└──────────────────────────────────────────────────────┘
```

### 12.4 Die Prüfseite (React-Komponente)

```jsx
// src/pages/verify.jsx

import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import VerificationDashboard from '../components/VerificationDashboard';

export default function VerifyPage() {
  const [mode, setMode] = useState('full');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(null);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
      <h1>responzai Verifier</h1>
      <p>Prüfen Sie Ihre Texte auf Richtigkeit, Aktualität und Konsistenz.</p>

      {!result && (
        <>
          <DocumentUpload
            mode={mode}
            onModeChange={setMode}
            onResult={setResult}
            onProgress={setProgress}
            onLoadingChange={setLoading}
          />
          {loading && progress && (
            <ProgressDisplay progress={progress} />
          )}
        </>
      )}

      {result && (
        <VerificationDashboard
          result={result}
          onReset={() => { setResult(null); setProgress(null); }}
        />
      )}
    </div>
  );
}

function ProgressDisplay({ progress }) {
  const agents = [
    { key: 'simon', name: 'Simon', label: 'Behauptungen finden' },
    { key: 'vera', name: 'Vera', label: 'Faktenprüfung' },
    { key: 'conrad', name: 'Conrad', label: 'Gegenprüfung' },
    { key: 'sven', name: 'Sven', label: 'Konsistenzprüfung' },
    { key: 'pia', name: 'Pia', label: 'Aktualitätsprüfung' },
  ];

  return (
    <div style={{
      marginTop: '24px',
      padding: '20px',
      border: '1px solid #e0e0e0',
      borderRadius: '8px'
    }}>
      <h3>Prüfung läuft...</h3>
      {agents.map(agent => {
        const status = progress[agent.key];
        const icon = status === 'done' ? '✅'
                   : status === 'running' ? '🔄'
                   : '⏳';
        return (
          <div key={agent.key} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 0',
            opacity: status === 'waiting' ? 0.5 : 1
          }}>
            <span>{icon}</span>
            <strong>{agent.name}:</strong>
            <span>{agent.label}</span>
            {status === 'done' && progress[`${agent.key}_summary`] && (
              <span style={{ color: '#666', marginLeft: '8px' }}>
                {progress[`${agent.key}_summary`]}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

### 12.5 Die Upload-Komponente (Drag and Drop)

```jsx
// src/components/DocumentUpload.jsx

import React, { useState, useRef, useCallback } from 'react';

const API_BASE = 'https://api.responzai.eu';

const ALLOWED_FORMATS = {
  'application/pdf': 'PDF',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'text/plain': 'Text',
  'text/html': 'HTML',
  'text/markdown': 'Markdown',
  'text/csv': 'CSV',
  'image/png': 'PNG',
  'image/jpeg': 'JPEG',
  'message/rfc822': 'E-Mail',
};

const MAX_SIZE = 50 * 1024 * 1024; // 50 MB

export default function DocumentUpload({
  mode, onModeChange, onResult, onProgress, onLoadingChange
}) {
  const [inputType, setInputType] = useState('file');  // 'url', 'text', 'file'
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Drag and Drop Handler
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (f) => {
    setError(null);

    if (f.size > MAX_SIZE) {
      setError(`Datei zu groß: ${(f.size / 1024 / 1024).toFixed(1)} MB. Maximum: 50 MB.`);
      return;
    }

    setFile(f);
    setInputType('file');
  };

  const handleSubmit = async () => {
    setError(null);
    onLoadingChange(true);

    try {
      let response;

      if (inputType === 'file' && file) {
        // Datei hochladen
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', mode);

        response = await fetch(`${API_BASE}/verify/document`, {
          method: 'POST',
          body: formData,
        });

      } else if (inputType === 'url' && url) {
        // URL prüfen
        response = await fetch(`${API_BASE}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, mode }),
        });

      } else if (inputType === 'text' && text) {
        // Text direkt prüfen
        response = await fetch(`${API_BASE}/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text, mode }),
        });
      }

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Prüfung fehlgeschlagen');
      }

      const result = await response.json();
      onResult(result);

    } catch (err) {
      setError(err.message);
    } finally {
      onLoadingChange(false);
    }
  };

  const canSubmit = (inputType === 'file' && file)
                 || (inputType === 'url' && url.trim())
                 || (inputType === 'text' && text.trim());

  return (
    <div>
      {/* Tab-Auswahl: URL, Text, Datei */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '16px'
      }}>
        {[
          { key: 'url', label: 'URL' },
          { key: 'text', label: 'Text' },
          { key: 'file', label: 'Datei hochladen' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setInputType(tab.key)}
            style={{
              padding: '10px 20px',
              border: '2px solid',
              borderColor: inputType === tab.key ? '#1a73e8' : '#e0e0e0',
              borderRadius: '8px',
              background: inputType === tab.key ? '#e8f0fe' : '#fff',
              cursor: 'pointer',
              fontWeight: inputType === tab.key ? 'bold' : 'normal',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* URL-Eingabe */}
      {inputType === 'url' && (
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://responzai.eu/..."
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '8px',
          }}
        />
      )}

      {/* Text-Eingabe */}
      {inputType === 'text' && (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Text hier einfügen..."
          rows={8}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            border: '1px solid #ccc',
            borderRadius: '8px',
            resize: 'vertical',
          }}
        />
      )}

      {/* Datei-Upload (Drag and Drop) */}
      {inputType === 'file' && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragOver ? '#1a73e8' : '#ccc'}`,
            borderRadius: '12px',
            padding: '40px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: dragOver ? '#e8f0fe' : '#fafafa',
            transition: 'all 0.2s',
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
            accept=".pdf,.docx,.xlsx,.pptx,.odt,.ods,.odp,.html,.htm,.md,.txt,.csv,.eml,.msg,.png,.jpg,.jpeg,.tiff,.tif"
          />

          {file ? (
            <div>
              <p style={{ fontSize: '18px', fontWeight: 'bold' }}>
                {file.name}
              </p>
              <p style={{ color: '#666' }}>
                {(file.size / 1024 / 1024).toFixed(1)} MB
              </p>
              <p style={{ color: '#1a73e8', fontSize: '14px' }}>
                Andere Datei wählen
              </p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: '18px', marginBottom: '8px' }}>
                Datei hierher ziehen oder klicken
              </p>
              <p style={{ color: '#666', fontSize: '14px' }}>
                PDF, Word, Excel, PowerPoint, Bilder, E-Mails und mehr
              </p>
              <p style={{ color: '#999', fontSize: '13px' }}>
                Maximal 50 MB
              </p>
            </div>
          )}
        </div>
      )}

      {/* Modus-Auswahl */}
      <div style={{ marginTop: '16px', display: 'flex', gap: '16px' }}>
        <label style={{ cursor: 'pointer' }}>
          <input
            type="radio"
            value="quick"
            checked={mode === 'quick'}
            onChange={() => onModeChange('quick')}
          />
          {' '}Schnellprüfung (Simon + Vera)
        </label>
        <label style={{ cursor: 'pointer' }}>
          <input
            type="radio"
            value="full"
            checked={mode === 'full'}
            onChange={() => onModeChange('full')}
          />
          {' '}Vollständige Prüfung (alle 8 Agenten)
        </label>
      </div>

      {/* Fehlermeldung */}
      {error && (
        <div style={{
          marginTop: '12px',
          padding: '12px',
          backgroundColor: '#fdecea',
          color: '#b71c1c',
          borderRadius: '8px',
        }}>
          {error}
        </div>
      )}

      {/* Absenden */}
      <button
        onClick={handleSubmit}
        disabled={!canSubmit}
        style={{
          marginTop: '16px',
          padding: '14px 32px',
          fontSize: '16px',
          fontWeight: 'bold',
          color: '#fff',
          backgroundColor: canSubmit ? '#1a73e8' : '#ccc',
          border: 'none',
          borderRadius: '8px',
          cursor: canSubmit ? 'pointer' : 'not-allowed',
          width: '100%',
        }}
      >
        Prüfung starten
      </button>
    </div>
  );
}
```

### 12.6 Das Ergebnis-Dashboard

```jsx
// src/components/VerificationDashboard.jsx

import React, { useState } from 'react';
import ReportViewer from './ReportViewer';

export default function VerificationDashboard({ result, onReset }) {
  const [showReport, setShowReport] = useState(false);

  // Gesamtbewertung bestimmen
  const getOverallStatus = () => {
    if (result.issues_found === 0) return { label: 'Alles in Ordnung', color: '#4caf50' };
    if (result.issues_found <= 2) return { label: 'Kleine Auffälligkeiten', color: '#ff9800' };
    return { label: 'Handlungsbedarf', color: '#f44336' };
  };

  const status = getOverallStatus();

  return (
    <div>
      {/* Kopfzeile mit Gesamtergebnis */}
      <div style={{
        padding: '24px',
        borderRadius: '12px',
        backgroundColor: `${status.color}15`,
        border: `2px solid ${status.color}`,
        marginBottom: '24px',
        textAlign: 'center',
      }}>
        <h2 style={{ color: status.color, marginBottom: '8px' }}>
          {status.label}
        </h2>
        {result.filename && (
          <p style={{ color: '#666' }}>Geprüfte Datei: {result.filename}</p>
        )}
      </div>

      {/* Kennzahlen */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        marginBottom: '24px',
      }}>
        <StatCard
          label="Behauptungen"
          value={result.total_claims}
          color="#1a73e8"
        />
        <StatCard
          label="Bestätigt"
          value={result.verified_claims}
          color="#4caf50"
        />
        <StatCard
          label="Probleme"
          value={result.issues_found}
          color={result.issues_found > 0 ? '#f44336' : '#4caf50'}
        />
        <StatCard
          label="Seiten"
          value={result.pages || '-'}
          color="#666"
        />
      </div>

      {/* Dokumentinfo (bei Datei-Uploads) */}
      {result.metadata && (
        <div style={{
          padding: '16px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          marginBottom: '24px',
          fontSize: '14px',
        }}>
          <strong>Dokumentdetails:</strong>
          <div style={{ marginTop: '8px', display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
            {result.format && <span>Format: {result.format}</span>}
            {result.text_length && <span>Textlänge: {result.text_length.toLocaleString()} Zeichen</span>}
            {result.metadata.author && <span>Autor: {result.metadata.author}</span>}
            {result.metadata.modified && <span>Geändert: {new Date(result.metadata.modified).toLocaleDateString('de-DE')}</span>}
          </div>
        </div>
      )}

      {/* Aktionsbuttons */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={() => setShowReport(true)}
          style={{
            padding: '12px 24px',
            backgroundColor: '#1a73e8',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Vollständigen Bericht anzeigen
        </button>
        <button
          onClick={onReset}
          style={{
            padding: '12px 24px',
            backgroundColor: '#fff',
            color: '#333',
            border: '1px solid #ccc',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Neue Prüfung
        </button>
      </div>

      {/* Detailbericht */}
      {showReport && result.report && (
        <ReportViewer
          report={result.report}
          onClose={() => setShowReport(false)}
        />
      )}
    </div>
  );
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      padding: '16px',
      borderRadius: '8px',
      border: '1px solid #e0e0e0',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: '28px', fontWeight: 'bold', color }}>{value}</div>
      <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>{label}</div>
    </div>
  );
}
```

### 12.7 Der Berichts-Viewer

```jsx
// src/components/ReportViewer.jsx

import React from 'react';

export default function ReportViewer({ report, onClose }) {
  if (!report) return null;

  return (
    <div style={{
      marginTop: '24px',
      padding: '24px',
      border: '1px solid #e0e0e0',
      borderRadius: '12px',
      backgroundColor: '#fff',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
      }}>
        <h3>Prüfbericht</h3>
        <button
          onClick={onClose}
          style={{
            padding: '6px 12px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer',
            background: '#fff',
          }}
        >
          Schließen
        </button>
      </div>

      {/* Problematische Claims auflisten */}
      {report.issues && report.issues.map((issue, i) => (
        <div key={i} style={{
          padding: '16px',
          marginBottom: '12px',
          borderRadius: '8px',
          border: '1px solid',
          borderColor: issue.severity === 'critical' ? '#f44336'
                     : issue.severity === 'major' ? '#ff9800'
                     : '#ffc107',
          backgroundColor: issue.severity === 'critical' ? '#fdecea'
                         : issue.severity === 'major' ? '#fff3e0'
                         : '#fffde7',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '8px'
          }}>
            <strong>{issue.claim_text}</strong>
            <span style={{
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: 'bold',
              color: '#fff',
              backgroundColor: issue.severity === 'critical' ? '#f44336'
                             : issue.severity === 'major' ? '#ff9800'
                             : '#ffc107',
            }}>
              {issue.severity}
            </span>
          </div>

          {/* Welcher Agent hat das Problem gefunden? */}
          <p style={{ fontSize: '14px', color: '#666' }}>
            Gefunden von: <strong>{issue.found_by}</strong>
          </p>
          <p style={{ fontSize: '14px' }}>{issue.description}</p>

          {/* Verbesserungsvorschlag */}
          {issue.suggestion && (
            <div style={{
              marginTop: '8px',
              padding: '10px',
              backgroundColor: '#e8f5e9',
              borderRadius: '4px',
              fontSize: '14px',
            }}>
              <strong>Vorschlag:</strong> {issue.suggestion}
            </div>
          )}
        </div>
      ))}

      {/* Wenn keine Probleme */}
      {(!report.issues || report.issues.length === 0) && (
        <p style={{ color: '#4caf50', textAlign: 'center', padding: '20px' }}>
          Keine Probleme gefunden. Alle Behauptungen wurden bestätigt.
        </p>
      )}
    </div>
  );
}
```

### 12.8 Fortschrittsanzeige mit Server-Sent Events

Die Prüfung dauert bei großen Dokumenten mehrere Minuten. Der Nutzer soll sehen, welcher Agent gerade arbeitet. Dafür verwenden wir Server-Sent Events (SSE). Das ist eine einfache Technik: Der Server schickt Nachrichten an den Browser, ohne dass der Browser ständig nachfragen muss.

**API-Endpunkt für Fortschritt:**

```python
# api/routes/upload.py (Ergänzung)

from fastapi.responses import StreamingResponse
import asyncio
import json

@router.post("/verify/document/stream")
async def verify_document_stream(
    file: UploadFile = File(...),
    mode: str = "full"
):
    """
    Wie /verify/document, aber mit Fortschrittsanzeige.
    Der Server schickt Updates als Server-Sent Events.

    Warum SSE statt WebSockets?
    SSE ist einfacher. Es funktioniert über eine normale
    HTTP-Verbindung. Der Browser empfängt, der Server sendet.
    Für unseren Fall (nur der Server sendet Updates) ist
    das perfekt. WebSockets wären hier unnötige Komplexität.
    """
    content = await file.read()
    stored = await save_upload(content, file.filename)
    document = await ingest_document(
        stored["stored_path"], file.filename, file.content_type
    )

    async def event_stream():
        # Fortschritt für jeden Agenten senden
        agents = ['simon', 'vera', 'conrad', 'sven', 'pia',
                  'lena', 'david', 'uma']

        for i, agent in enumerate(agents):
            # Status: Dieser Agent arbeitet jetzt
            yield f"data: {json.dumps({
                'agent': agent,
                'status': 'running',
                'progress': int((i / len(agents)) * 100)
            })}\n\n"

            # Hier würde der jeweilige Agent-Schritt laufen
            # (vereinfacht dargestellt)
            await asyncio.sleep(0.1)  # Platzhalter

            # Status: Agent ist fertig
            yield f"data: {json.dumps({
                'agent': agent,
                'status': 'done',
                'progress': int(((i + 1) / len(agents)) * 100),
                'summary': f'{agent} fertig'
            })}\n\n"

        # Endergebnis senden
        yield f"data: {json.dumps({
            'status': 'complete',
            'progress': 100,
            'result': {}  # Hier kommt das vollständige Ergebnis
        })}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
```

**Browser-seitig (in DocumentUpload.jsx):**

```javascript
// Fortschritts-Variante des Submit-Handlers
const handleSubmitWithProgress = async () => {
  if (inputType !== 'file' || !file) return;

  setError(null);
  onLoadingChange(true);

  const formData = new FormData();
  formData.append('file', file);
  formData.append('mode', mode);

  try {
    const response = await fetch(
      `${API_BASE}/verify/document/stream`,
      { method: 'POST', body: formData }
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));

          if (data.status === 'complete') {
            onResult(data.result);
          } else {
            // Fortschritt aktualisieren
            onProgress(prev => ({
              ...prev,
              [data.agent]: data.status,
              [`${data.agent}_summary`]: data.summary,
              percent: data.progress,
            }));
          }
        }
      }
    }
  } catch (err) {
    setError(err.message);
  } finally {
    onLoadingChange(false);
  }
};
```

---

## 13. Skills für die Agenten

### 13.1 Was sind Skills in diesem Kontext?

Skills sind wiederverwendbare Anweisungsdokumente, die die Prompt-Logik und Qualitätskriterien eines Agenten standardisieren. Jeder Skill ist eine Markdown-Datei, die genau beschreibt, was der Agent tun soll, wie das Ergebnis aussehen muss und was auf keinen Fall passieren darf.

Skills werden im Ordner `skills/` des responzai-verifier Repositories gespeichert.

### 13.2 Skill: Claim-Extraktion (für Simon)

```markdown
# Skill: Claim-Extraktion

## Wann diesen Skill verwenden
Immer wenn ein Text in prüfbare Behauptungen zerlegt werden soll.
Simon (SCOUT) verwendet diesen Skill bei jedem Prüflauf.

## Eingabe
Ein beliebiger Text und die URL, von der er stammt.

## Regeln
1. Jede Behauptung muss als eigenständiger Satz formuliert sein.
2. Jede Behauptung muss mit Ja oder Nein beantwortbar sein.
3. Zusammengesetzte Aussagen werden in einzelne Behauptungen zerlegt.
4. Meinungen und Wertungen werden nicht als Claims extrahiert.
5. Jeder Claim bekommt eine Kategorie: LEGAL_CLAIM, PRODUCT_CLAIM, 
   MARKET_CLAIM oder TARGET_GROUP.

## Qualitätskriterien
- Vollständigkeit: Keine prüfbare Behauptung übersehen.
- Atomarität: Jeder Claim enthält genau eine Behauptung.
- Prüfbarkeit: Jeder Claim kann gegen eine Quelle geprüft werden.

## Ausgabeformat
JSON-Objekt mit claims-Array (siehe agents/simon_scout/prompt.py).

## Häufige Fehler
- Zu große Claims (mehrere Behauptungen in einem Satz).
- Meinungen als Claims extrahieren ("responzai ist der beste Anbieter").
- Implizite Annahmen nicht als separate Claims erfassen.
```

### 13.3 Skill: Adversarial Check (für Conrad)

```markdown
# Skill: Adversariale Gegenprüfung

## Wann diesen Skill verwenden
Immer wenn ein von Vera verifizierter Claim gegengeprüft werden soll.
Conrad (CONTRA) verwendet diesen Skill für jeden verifizierten Claim.

## Eingabe
Ein Claim mit Veras Ergebnis (Score, Quellenpassagen) und 
Ergebnissen der inversen RAG-Suche.

## Die vier Strategien (immer alle anwenden)
1. AUSNAHMENSUCHE: Suche nach Fällen, in denen der Claim nicht gilt.
2. ZEITLICHE PRÜFUNG: Suche nach neueren Quellen.
3. ANNAHMENPRÜFUNG: Identifiziere versteckte Voraussetzungen.
4. GEGENBEISPIELE: Suche nach konkreten Widersprüchen.

## Regeln
1. Nur auf Basis der bereitgestellten Quellen argumentieren.
2. Haarspalterei ist kein Widerspruch. Echte Schwächen finden.
3. "survived" ist ein gutes Ergebnis. Nicht künstlich schwächen.
4. Jede Schwäche braucht einen konkreten Beleg.

## Qualitätskriterien
- Ein "refuted" Ergebnis muss einen eindeutigen Beleg haben.
- Ein "weakened" Ergebnis muss zeigen, was fehlt oder ungenau ist.
- Kein Ergebnis darf auf Conrads eigenem "Wissen" basieren.

## Ausgabeformat
JSON-Objekt mit result, strategies_applied und suggested_refinement
(siehe agents/conrad_contra/prompt.py).
```

### 13.4 Skill: Quellengebundene Textgenerierung (für Lena)

```markdown
# Skill: Quellengebundene Textgenerierung

## Wann diesen Skill verwenden
Immer wenn ein rechtlicher Text aktualisiert oder korrigiert werden soll.
Lena (LEGAL) verwendet diesen Skill für jede Textänderung.

## SICHERHEITSREGELN (NICHT VERHANDELBAR)
1. NUR Informationen aus den mitgelieferten source_passages verwenden.
2. Jeder Satz MUSS eine Quellenreferenz haben.
3. Bei fehlender Quelle: LÜCKE markieren, NICHTS erfinden.
4. Temperature MUSS 0 sein.
5. Nur Diff generieren, nie den kompletten Text neu schreiben.

## Rückprüfungsschleife
Jeder Vorschlag von Lena durchläuft:
1. Quellen-Binding-Check (Hash-Validierung)
2. Vera prüft den neuen Text (Score muss > 0.9 sein)
3. Conrad prüft den neuen Text (darf nicht "refuted" sein)

## Wenn die Rückprüfung fehlschlägt
Der Vorschlag wird verworfen. Lena generiert KEINEN zweiten Versuch
automatisch. Stattdessen wird das Problem dem Menschen gemeldet.

## Ausgabeformat
JSON-Objekt mit current_text, suggested_text, sources_used, 
coverage und gaps (siehe agents/lena_legal/prompt.py).
```

### 13.5 Skill: Report-Generierung

```markdown
# Skill: Report-Generierung

## Wann diesen Skill verwenden
Am Ende jeder Pipeline, um den finalen Bericht zu erstellen.

## Zwei Berichtstypen

### Prüfbericht (Verification Report)
Fasst die Ergebnisse von Simon, Vera, Conrad, Sven und Pia zusammen.
Enthält:
- Gesamtübersicht (Anzahl Claims, Scores, Probleme)
- Details pro problematischem Claim
- Empfohlene Maßnahmen

### Änderungsbericht (Improvement Report)
Fasst die Vorschläge von Lena, David und Uma zusammen.
Enthält:
- Gesamtübersicht (Anzahl Änderungen, Schweregrade)
- Änderungsvorschläge pro Dokument/Abschnitt
- Priorisierung der Änderungen

## Stilregeln für Berichte
- Klar und verständlich (siehe Stilguide, Kapitel 14)
- Jeder Befund hat: Was ist das Problem? Wo genau? Wie beheben?
- Schweregrade: critical / major / minor
- Agenten werden mit Namen genannt: "Vera hat Score 0.45 vergeben"
```

---

## 14. Stilguide für David (DRAFT)

### 14.1 Grundprinzip

Jeder Text von responzai folgt einer einfachen Regel: Wenn ein Zehnjähriger den Satz nicht versteht, muss er umgeschrieben werden. Das bedeutet nicht, dass die Inhalte kindisch sind. Die Inhalte sind für Erwachsene. Aber die Sprache ist einfach.

### 14.2 Die Regeln

**Satzlänge:** Maximal 15 Wörter pro Satz als Richtwert. Nicht als starre Grenze, sondern als Orientierung. Wenn ein Satz 18 Wörter hat und trotzdem klar ist, ist das in Ordnung. Wenn er 12 Wörter hat und unklar ist, muss er trotzdem umgeschrieben werden.

**Wörter:** Alltägliche Wörter statt Fachsprache. Wenn ein Fachbegriff unvermeidbar ist (z.B. "Konformitätsbewertung"), wird er sofort im nächsten Satz erklärt.

**Satzform:** Aktiv statt passiv. "Prüfen Sie das Risiko" statt "Das Risiko ist zu prüfen". "Füllen Sie das Feld aus" statt "Das Feld sollte ausgefüllt werden".

**Handlungsanweisungen:** Konkret statt vage. "Tragen Sie den Namen der verantwortlichen Person ein" statt "Die zuständige Person ist zu benennen".

**Verboten:**
- Gedankenstriche (immer durch Punkte oder Kommas ersetzen)
- "Hand aufs Herz"
- "Technikgewitter", "Cloudnebel", "Datenflut" und ähnliche Sprachbilder
- "Im Endeffekt", "Schlussendlich", "Letzten Endes"
- "Nicht zu unterschätzen", "Es sei darauf hingewiesen"
- Nominalstil ("Die Durchführung der Implementierung" → "Setzen Sie um")

**Erwünscht:**
- Kurze Sätze
- Klare Anweisungen
- Beispiele
- Erklärungen bei Fachbegriffen
- Lieber ein Satz mehr als ein unverständlicher Satz

### 14.3 Vorher/Nachher-Beispiele

**Vorher:** "Die Implementierung der in Art. 9 Abs. 2 lit. a der Verordnung normierten Verpflichtung zur Durchführung einer Risikobewertung ist durch die jeweils zuständige Organisationseinheit zeitnah sicherzustellen."

**Nachher:** "Starten Sie die Risikobewertung bis zum [Datum]. Artikel 9 Absatz 2 der Verordnung schreibt das vor. Zuständig ist [Abteilung eintragen]."

**Vorher:** "Es wird empfohlen, eine regelmäßige Überprüfung der eingesetzten KI-Systeme hinsichtlich ihrer Konformität mit den regulatorischen Anforderungen des EU AI Act vorzunehmen."

**Nachher:** "Prüfen Sie Ihre KI-Systeme regelmäßig. Der EU AI Act verlangt das. Planen Sie die Prüfung alle [Zeitraum eintragen] Monate ein."

---

## 15. Anhang: Konfigurationsdateien und Referenzen

### 15.1 .env.example (Vorlage für Umgebungsvariablen)

```bash
# responzai Verifier - Umgebungsvariablen
# Kopiere diese Datei als .env und fülle die Werte aus.

# Anthropic API (für Claude)
ANTHROPIC_API_KEY=sk-ant-api...

# Voyage API (für Embeddings)
VOYAGE_API_KEY=pa-...

# PostgreSQL Datenbank
POSTGRES_USER=responzai
POSTGRES_PASSWORD=SICHERES_PASSWORT
POSTGRES_DB=verifier
DATABASE_URL=postgresql://responzai:SICHERES_PASSWORT@postgres:5432/verifier

# n8n Automatisierung
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=SICHERES_PASSWORT

# E-Mail (für Benachrichtigungen)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=verifier@responzai.eu
SMTP_PASSWORD=EMAIL_PASSWORT

# Allgemein
ENVIRONMENT=production
LOG_LEVEL=info
```

### 15.2 requirements.txt

```
# Python-Abhängigkeiten für den responzai Verifier

# Web-Framework
fastapi==0.109.0
uvicorn==0.27.0

# KI und NLP
anthropic==0.18.0
langchain==0.1.0
langgraph==0.0.26
voyageai==0.2.0

# Datenbank
asyncpg==0.29.0
sqlalchemy==2.0.25
pgvector==0.2.4

# Web-Crawling
requests==2.31.0
beautifulsoup4==4.12.3
scrapy==2.11.0

# RSS und Monitoring
feedparser==6.0.11

# Hilfsbibliotheken
numpy==1.26.3
python-dotenv==1.0.0
pydantic==2.5.0
```

### 15.3 Dockerfile

```dockerfile
# Basis-Image: Python 3.11 (schlank)
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten zuerst kopieren (für Cache-Optimierung)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Port freigeben
EXPOSE 8000

# Anwendung starten
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 15.4 Scoring-System (Gesamtübersicht)

Jeder Claim bekommt am Ende einen strukturierten Score:

```json
{
  "claim_id": "claim_001",
  "claim_text": "Der EU AI Act verpflichtet zur KI-Kompetenz",
  "source_url": "https://responzai.eu/...",
  "category": "LEGAL_CLAIM",
  
  "simon": {
    "extracted": true,
    "verifiability": "high",
    "category": "LEGAL_CLAIM"
  },
  
  "vera": {
    "score": 0.85,
    "status": "verified",
    "sources": ["EU AI Act, Art. 4"]
  },
  
  "conrad": {
    "result": "weakened",
    "finding": "Gilt nur für Anbieter und Betreiber, nicht für alle Unternehmen",
    "suggested_refinement": "Präzisieren: Anbieter und Betreiber von KI-Systemen"
  },
  
  "sven": {
    "consistency_score": 0.7,
    "contradictions": [{
      "with_claim": "claim_015",
      "source": "Newsletter Ausgabe 23",
      "severity": "minor"
    }]
  },
  
  "pia": {
    "freshness": "fresh",
    "days_since_source_update": 45
  },
  
  "lena": {
    "suggestion": "Ersetzen durch: 'Anbieter und Betreiber von KI-Systemen müssen KI-Kompetenz sicherstellen (Art. 4 VO (EU) 2024/1689).'",
    "coverage": 0.98,
    "verification_passed": true
  },
  
  "david": {
    "suggestion": "Vereinfachen: 'Wer KI-Systeme anbietet oder nutzt, muss dafür sorgen, dass die Mitarbeiter sich mit KI auskennen. So steht es in Artikel 4 des EU AI Act.'",
    "readability_improvement": "+37 Punkte"
  },
  
  "uma": {
    "issue": "Keine Erklärung, was KI-Kompetenz konkret bedeutet",
    "suggestion": "Beispiel ergänzen: 'KI-Kompetenz bedeutet: Ihre Mitarbeiter wissen, was KI kann, wo Risiken liegen und wie sie KI verantwortungsvoll einsetzen.'"
  },
  
  "overall_confidence": 0.62,
  "action_required": true
}
```

---

## Zusammenfassung: Der Fahrplan

```
Woche  1 bis  2: Server aufsetzen, Docker einrichten, Repos anlegen
Woche  3 bis  4: Wissensbasis befüllen (EU AI Act, eigene Inhalte)
Woche  5 bis  6: Simon (SCOUT) bauen und testen
Woche  7 bis  8: Vera (VERIFY) bauen, erster Prüflauf
Woche  9 bis 10: Conrad (CONTRA) bauen und kalibrieren
Woche 11 bis 12: Sven (SYNC) und Pia (PULSE), erster vollständiger Report
Woche 13 bis 14: n8n-Workflows einrichten, Automatisierung
Woche 15 bis 16: Lena (LEGAL), David (DRAFT), Uma (UX)
Woche 17 bis 18: Testen, justieren, erster öffentlicher Content
```

**Kosten bis zum MVP:** Unter 100 Euro (plus deine Arbeitszeit).
**Laufende Kosten:** Ca. 21 Euro pro Monat.

---

*Dieses Dokument wurde erstellt als Arbeitsanweisung für die Umsetzung des responzai Multi-Agent Verification & Improvement Systems. Es ist gleichzeitig Referenz und schrittweise Anleitung. Bei Fragen zu einzelnen Schritten: Frag nach. Das System ist komplex, aber jeder einzelne Schritt ist machbar.*
