# Aufgabe 2: Auswertung von Kundenfeedback

## 1. Ausgangslage & Ziel der Vereinfachung
Kundenfeedback geht bei WAXCAT über verschiedene Kanäle ein (z. B. Produktbewertungen, Support-E-Mails, Retourengründe, Social-Media-Kommentare). Die manuelle Sichtung und Kategorisierung dieser unstrukturierten Texte ist zeitintensiv, fehleranfällig und führt oft dazu, dass wiederkehrende Produkt- oder Versandprobleme erst spät erkannt werden.

**Ziel:** Ein hybrid-automatisierter Workflow sammelt Feedback täglich ein, bereinigt es per Skript, klassifiziert Themen sowie Dringlichkeit mithilfe eines KI-Agents und stellt dem Team nur noch verdichtete Handlungsempfehlungen sowie kritische Einzelfälle zur Prüfung bereit.

## 2. Benötigte Datenquellen
Um Feedback nicht isoliert, sondern im geschäftlichen Kontext auszuwerten, werden folgende Daten zusammengeführt:
- **Unstrukturierte Feedback-Daten:** Freitexte aus Shop-Bewertungen, Support-Tickets, Retourenformularen und Umfragen.
- **Metadaten & Bestellkontext:** Zeitstempel, Kanal, Artikelnummer (SKU), Produktkategorie sowie Bestell- und Versandstatus (analog zur Bestellaggregation aus Aufgabe 1).
- **Stammdaten / Taxonomie:** Eine definierte Liste relevanter Kategorien (z. B. *Produktqualität, Passform/Eigenschaften, Versand & Verpackung, Kundenservice, Lob*).

## 3. Aufgabenteilung: Python-Skript vs. KI-Agent vs. Team

### 1. Python-Skript *(Deterministisch)*
* **Verantwortlichkeit & konkrete Schritte:**
  * Täglicher Export neuer Einträge via API/CSV
  * Deduplizierung & Entfernen leerer Einträge
  * Anonymisierung personenbezogener Daten (DSGVO: Namen/E-Mails maskieren)
  * Verknüpfung mit Bestell-/Produkt-IDs & Export als strukturierter Wochenreport
* **Warum diese Aufteilung?**
  * Schnell, kostenlos, 100 % reproduzierbar und datenschutzkonform vor dem LLM-Aufruf.

---

### 2. KI-Agent *(LLM-basiert)*
* **Verantwortlichkeit & konkrete Schritte:**
  * **Klassifizierung:** Zuordnung zu Haupt- und Unterkategorien (Multi-Label)
  * **Sentiment & Dringlichkeit:** Bewertung der Stimmung (-2 bis +2) sowie Erkennung kritischer Fälle (z. B. Defekte, Falschlieferungen)
  * **Extraktion & Zusammenfassung:** Herausfiltern konkreter Produktwünsche und Erstellung eines wöchentlichen Briefings („Top 3 Probleme & Trends“)
* **Warum diese Aufteilung?**
  * Versteht Nuancen, Ironie und unstrukturierte Sprache zuverlässig ohne starre Keyword-Regeln.

---

### 3. WAXCAT-Team *(Human-in-the-Loop)*
* **Verantwortlichkeit & konkrete Schritte:**
  * **Eskalations-Handling:** Direkte Bearbeitung von durch die KI markierten kritischen Tickets
  * **Qualitätssicherung:** Stichprobenartige Prüfung von ca. 5–10 % der KI-Klassifizierungen
  * **Entscheidung:** Ableitung konkreter Maßnahmen (z. B. Anpassung von Produktbeschreibungen oder Lieferanten-Feedback)
* **Warum diese Aufteilung?**
  * Fokus auf Wertschöpfung, Kundenbindung und strategische Entscheidungen statt Routinearbeit.

## 4. Erfolgsmessung (KPIs für Zeitersparnis & Fehlerreduktion)
Um den Mehrwert im Alltag objektiv zu bewerten, werden vor und nach der Einführung folgende Kennzahlen verglichen:

1. **Zeitersparnis (Effizienz):**
   - *Bearbeitungszeit pro Woche:* Reduktion des manuellen Aufwands für Sichtung, Tagging und Reporting (Ziel: **> 75 % Zeitersparnis**, z. B. von 4 Stunden auf unter 45 Minuten pro Woche).
   - *Time-to-Action:* Zeitspanne vom Eingang eines kritischen Kundenproblems bis zur Reaktion des Teams.
2. **Fehlerreduktion & Qualität (Effektivität):**
   - *Klassifizierungsgenauigkeit (Precision/Recall):* Übereinstimmung zwischen KI-Labels und manueller Stichprobenprüfung durch das Team (Ziel: **> 90 % Genauigkeit**).
   - *Übersehene kritische Fälle (False Negatives):* Anteil dringender Reklamationen, die durch den automatischen Dringlichkeits-Filter sofort erkannt werden (Ziel: **0 übersehene Eskalationen**).
   - *Konsistenz:* Einheitliche Kategorisierung unabhängig von Tagesform oder wechselnden Teammitgliedern.