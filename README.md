# WAXCAT KI Projekt – KI-Assistent für Materialbestellungen & Use-Case-Skizze

Dieses Projekt enthält meine vollständigen Lösungen für die beiden praxisnahen Testaufgaben im Rahmen meiner Bewerbung bei **WAXCAT**:
* **Aufgabe 1:** Ein modularer, lauffähiger Python-Prototyp zur automatisierten Verarbeitung, Validierung und Aggregation von Materialbestellungen aus mehreren WAXCAT-Studios (`src/` & `tests/`).
* **Aufgabe 2:** Eine strukturierte Konzeptskizze (1 Seite) für die automatisierte Auswertung und Triage von Kundenfeedback über alle Standorte hinweg.

---

# Aufgabe 1 – KI-Assistent für Materialbestellungen

## 1. Systemarchitektur (KI vs. Deterministische Logik)

Um höchste Zuverlässigkeit im operativen Studio-Alltag zu gewährleisten, trennt der Prototyp strikt zwischen **probabilistischer Sprachverarbeitung (LLM)** und **deterministischer Geschäftslogik (Python)**. Sprachmodelle eignen sich ideal zum Verstehen und Strukturieren unordentlicher Freitexte, während reiner Python-Code bei Arithmetik und strengen Filterregeln 100 % verlässlich arbeitet.

### A. KI-Schicht (`src/extractor.py`) – Semantisches Parsing & Normalisierung
* **Modell & Provider:** `qwen/qwen3.8-27b` über die **Groq API** (`groq` Python SDK) im deterministischen JSON-Modus (`response_format={"type": "json_object"}`), validiert durch Pydantic (`OrderExtractionResult`).
* **Aufgaben der KI:**
  1. **Entitätserkennung:** Extrahiert Studio-Standort, Artikelname, Menge und Einheit aus natürlichen Nachrichten.
  2. **Erkennung unvollständiger Angaben:** Erkennt, wenn Menge oder Einheit fehlen (z. B. *„und noch Kochsalzlösung“* in Eimsbüttel). Durch explizite Prompt-Regeln wird das Modell angewiesen, keine Mengen zu erraten (`quantity=null`), sondern `is_complete=False` zu setzen.
  3. **Kontextbezogene Rückfrage:** Formuliert für unvollständige Positionen automatisch eine höfliche, direkt versendbare Rückfrage an das jeweilige Studio (inklusive Hinweis auf die gängige Einheit *Flasche*, sofern aus anderen Bestellungen bekannt).

### B. Deterministische Schicht (`src/processor.py`) – Validierung & Aggregation
* **Aufgaben des Python-Codes:**
  1. **Strikte Filterung:** Prüft programmatisch (`if item.is_complete and item.quantity is not None and item.unit is not None`), ob alle Pflichtfelder vorhanden sind.
  2. **Exakte Aggregation:** Gruppiert valide Positionen nach `(Artikelname, Einheit)` und summiert die Mengen exakt auf. Unvollständige Positionen (wie die Kochsalzlösung aus Eimsbüttel) werden strikt aus der Gesamtsumme ausgeschlossen und in eine separate Klärungsliste verschoben.
  3. **API-/ERP-Ready Output:** Liefert sowohl eine übersichtliche Konsolentabelle für das Operations-Team als auch ein sauberes JSON-Objekt für die Weiterverarbeitung (z. B. via Webhook, Slack oder ERP-System).

---

## 2. Qualitätssicherung & Verifikation der Ergebnisse

Damit im Alltag keine fehlerhaften Bestellungen ausgelöst werden, greifen vier Prüfmechanismen:

1. **Schema-Validierung (`src/models.py`):** Pydantic (`model_validate_json`) erzwingt strikte Datentypen für die KI-Antwort (`int` für Mengen, `Optional` für fehlende Werte). Ungültige Strukturen werden sofort abgefangen.
2. **Deterministische Inferenz (`temperature=0.0`):** Minimiert Abweichungen bei wiederholten Durchläufen.
3. **Automatisierte Unit-Tests (`tests/test_processor.py`):** Prüfen mit `pytest` isoliert von der API, ob:
   * *Nitrilhandschuhe M* korrekt über Studios hinweg addiert werden ($3 + 2 = 5\text{ Packungen}$),
   * *Kochsalzlösung* aus Eimsbüttel strikt aus der Gesamtsumme herausgehalten wird ($2\text{ Flaschen}$ aus Wandsbek),
   * und die offene Rückfrage korrekt dem Studio Eimsbüttel zugeordnet wird.
4. **Human-in-the-Loop:** Unklare Positionen werden nie automatisch bestellt, sondern als fertiger Nachrichtenentwurf zur Freigabe bereitgestellt.

---

## Waxcat KI-basierte Bestellextraktions- & Verarbeitungspipeline

Eine KI-basierte Pipeline zur Extraktion und Aggregation von Bestellungen, entwickelt mit Python, Pydantic und Groq. Sie wandelt unstrukturierte Kundenbestellnachrichten in validierte, strukturierte Datenmodelle um und fasst Bestellpositionen zusammen.

## 3. Projektstruktur

```text
Waxcat_KI_Projekt/
├── src/
│   ├── __init__.py
│   ├── extractor.py               # LLM-basierte Bestellextraktionslogik (Es benutzt "qwen/qwen3.8-27b" GS (LLM) über die Groq API.)
│   ├── main.py                    # Einstiegspunkt der Anwendung
│   ├── models.py                  # Pydantic-Datenschemata
│   ├── processor.py               # Logik zur Bestellaggregation und -verarbeitung
│   └── sample_order_messages.py   # Beispielhafte Eingabenachrichten
├── tests/
│   └── test_processor.py          # Unit-Tests für die Bestellverarbeitung
├── .env                           # Umgebungsvariablen (API-Schlüssel)
├── .gitignore                     # Von Git ignorierte Dateien und Ordner
├── pyproject.toml                 # Paket- & Pytest-Konfiguration
├── README.md                      # Projektdokumentation & Installationsanleitung
└── requirements.txt               # Projektabhängigkeiten
```

## 4. Einrichtung & Installation

1. **In das Hauptverzeichnis des Projekts wechseln:**
   ```bash
   cd Waxcat_KI_Projekt
   ```

2. **Virtuelle Umgebung aktivieren:**

   * **macOS / Linux:**
     ```bash
     source waxcat_env/bin/activate
     ```
   * **Windows (PowerShell):**
     ```powershell
     .\waxcat_env\Scripts\Activate
     ```

3. **Projekt und Entwicklungsabhängigkeiten im Editiermodus (editable mode) installieren:**
   ```bash
   pip install -e ".[dev]"
   ```
   *(Alternativ über `pip install -r requirements.txt && pip install -e .` installieren)*

4. **Umgebungsvariablen konfigurieren:**
   Stelle sicher, dass die Datei `.env` im Hauptverzeichnis deinen Groq-API-Schlüssel enthält:
   ```env
   GROQ_API_KEY=dein_api_schluessel_hier
   ```

## 5. Projekt ausführen

Führe die Anwendung **aus dem Projekt-Hauptverzeichnis (`Waxcat_KI_Projekt/`)** aus:

```bash
python src/main.py
```

## Tests ausführen

Führe die Test-Suite **aus dem Projekt-Hauptverzeichnis (`Waxcat_KI_Projekt/`)** mit `pytest` aus:

```bash
python -m pytest
```

Um eine bestimmte Testdatei mit ausführlicher Ausgabe zu starten:

```bash
python -m pytest -v tests/test_processor.py
```

## 6. Virtuelle Umgebung deaktivieren

Wenn du mit der Arbeit fertig bist, kannst du die virtuelle Umgebung wieder verlassen:

* **macOS / Linux:**
  ```bash
  deactivate
  ```
* **Windows (CMD & PowerShell):**
  ```powershell
  deactivate
  ```

Das Ergebnis von der Aufgabe 1: 

Extracting structured order items via the Groq API (qwen/qwen3.8-27b Large Language Model (LLM))...
Extracted Order Data: {
  "items": [
    {
      "studio": "Innenstadt",
      "item_name": "Nitrilhandschuhe M",
      "quantity": 3,
      "unit": "Packung",
      "is_complete": true,
      "clarification_question": null
    },
    {
      "studio": "Innenstadt",
      "item_name": "Tape",
      "quantity": 2,
      "unit": "Rolle",
      "is_complete": true,
      "clarification_question": null
    },
    {
      "studio": "Eimsbüttel",
      "item_name": "Nitrilhandschuhe M",
      "quantity": 2,
      "unit": "Packung",
      "is_complete": true,
      "clarification_question": null
    },
    {
      "studio": "Eimsbüttel",
      "item_name": "Kochsalzlösung",
      "quantity": null,
      "unit": null,
      "is_complete": false,
      "clarification_question": "Hallo Eimsbüttel, wie viele Flaschen Kochsalzlösung benötigt ihr bitte?"
    },
    {
      "studio": "Wandsbek",
      "item_name": "Tape",
      "quantity": 1,
      "unit": "Rolle",
      "is_complete": true,
      "clarification_question": null
    },
    {
      "studio": "Wandsbek",
      "item_name": "Kochsalzlösung",
      "quantity": 2,
      "unit": "Flasche",
      "is_complete": true,
      "clarification_question": null
    }
  ]
}
Aggregating valid orders and filtering incomplete items...

============================================================
STRUKTURIERTE BESTELLÜBERSICHT (GESAMTSUMME)
============================================================
Artikel                   | Einheit    | Menge  | Studios
------------------------------------------------------------
Nitrilhandschuhe M        | Packung    | 5      | Innenstadt (3 Packung), Eimsbüttel (2 Packung)
Tape                      | Rolle      | 3      | Innenstadt (2 Rolle), Wandsbek (1 Rolle)
Kochsalzlösung            | Flasche    | 2      | Wandsbek (2 Flasche)


============================================================
OFFENE RÜCKFRAGEN (NICHT IN GESAMTSUMME ENTHALTEN)
============================================================
Studio:  Eimsbüttel
Artikel: Kochsalzlösung (Unvollständige Angabe)
Entwurf: "Hallo Eimsbüttel, wie viele Flaschen Kochsalzlösung benötigt ihr bitte?"
------------------------------------------------------------


Meine Interpretation des Berichts:

Die ausgegebene Bestellübersicht führt die Einzelanfragen der Studios erfolgreich zusammen, indem die benötigten Mengen für Nitrilhandschuhe M (drei Packungen aus Innenstadt und zwei aus Eimsbüttel zu insgesamt fünf Packungen) sowie Tape (zwei Rollen aus Innenstadt und eine aus Wandsbek zu insgesamt drei Rollen) korrekt zu Gesamtsummen gebündelt wurden. Bei der Kochsalzlösung flossen bislang ausschließlich die zwei Flaschen aus Wandsbek in die Gesamtsumme ein, während die Anfrage aus Eimsbüttel aufgrund der fehlenden Mengenangabe herausgefiltert und für die finale Klärung als offene Rückfrage samt passendem Nachrichtenentwurf festgehalten wurde.


JSON-Ausgabe:
{
  "valid_aggregated_orders": [
    {
      "item_name": "Nitrilhandschuhe M",
      "unit": "Packung",
      "total_quantity": 5,
      "studios": [
        "Innenstadt (3 Packung)",
        "Eimsbüttel (2 Packung)"
      ]
    },
    {
      "item_name": "Tape",
      "unit": "Rolle",
      "total_quantity": 3,
      "studios": [
        "Innenstadt (2 Rolle)",
        "Wandsbek (1 Rolle)"
      ]
    },
    {
      "item_name": "Kochsalzlösung",
      "unit": "Flasche",
      "total_quantity": 2,
      "studios": [
        "Wandsbek (2 Flasche)"
      ]
    }
  ],
  "pending_clarifications": [
    {
      "studio": "Eimsbüttel",
      "item_name": "Kochsalzlösung",
      "quantity": null,
      "unit": null,
      "is_complete": false,
      "clarification_question": "Hallo Eimsbüttel, wie viele Flaschen Kochsalzlösung benötigt ihr bitte?"
    }
  ]
}

src: 

**extractor.py:**

In diesem Modul extractor.py definiert system_prompt über die Rolle "system" die festen Arbeitsanweisungen des Modells, seine Domänen-Persona, das verbindliche Ausgabeformat sowie die Regeln für Sonderfälle, während user_content über die Rolle "user" die dynamischen Eingabedaten des jeweiligen Aufrufs – also die formatierte Liste der rohen Studio-Nachrichten – übergibt. Innerhalb des system_prompt legt die Persona als Operations-Assistenz für die WAXCAT-Studios in Hamburg den fachlichen Kontext und die Standardisierung fest (einheitliche Studio-Namen wie 'Innenstadt', 'Eimsbüttel' und 'Wandsbek' sowie saubere Produktnamen wie 'Nitrilhandschuhe M', 'Tape' und 'Kochsalzlösung'), fügt das direkt aus deinem Pydantic-Modell erzeugte OrderExtractionResult-JSON-Schema ein und erzwingt strenge Regeln zur Datenqualität: Fehlende Mengen dürfen nicht erraten werden, unvollständige Angaben (wenn Menge oder Einheit fehlt) müssen mit quantity=null, unit=null und is_complete=false markiert werden, und für unvollständige Einträge wird automatisch eine höfliche, prägnante deutsche Rückfrage an das jeweilige Studio unter Nennung bekannter Standardeinheiten (wie z. B. Flaschen) formuliert. Im Gegensatz dazu bleibt user_content rein datenorientiert ("Process the following studio messages:\n- ..."), sodass stabile Verhaltensregeln sauber von wechselnden Chat-Nachrichten getrennt sind und OrderExtractionResult.model_validate_json(raw_json) das zurückgegebene JSON zuverlässig validieren kann.

Der Parameter temperature=0.0 weist das Modell an, bei jedem Generierungsschritt strikt das Token mit der höchsten Wahrscheinlichkeit auszuwählen, statt zufällig aus einer breiteren Wahrscheinlichkeitsverteilung zu ziehen, wodurch die Extraktion über mehrere Durchläufe hinweg möglichst deterministisch, konsistent und reproduzierbar bleibt. Gerade bei der strukturierten Erfassung von Materialbestellungen – wo erfundene Mengenangaben, schwankende Produktbezeichnungen oder abweichende JSON-Strukturen direkt zu Fehlbestellungen im Lager führen würden, sorgt minimale Zufälligkeit für verlässliche Ergebnisse, auch wenn temperature=0.0 aufgrund von Hardware- und Backend-Effekten keine zu 100 % bitidentische Ausgabe garantiert. Deshalb arbeitet temperature=0.0 hier gezielt mit response_format={"type": "json_object"} und den expliziten Prompt-Regeln zusammen, damit das Modell bei unklaren Nachrichten nicht rät, sondern saubere null-Werte samt Rückfrage liefert.

Auf Modulebene bereiten die Importe und load_dotenv() zu Beginn die Laufzeitumgebung vor, bevor extract_orders_from_messages aufgerufen wird: os liest den GROQ_API_KEY aus den Umgebungsvariablen, json.dumps(..., indent=2) wandelt OrderExtractionResult.model_json_schema() in gut lesbaren Text für den Prompt um, Groq stellt die Verbindung zur Groq-API her, load_dotenv() lädt während der lokalen Entwicklung die Schlüssel-Wert-Paare aus einer .env-Datei in os.environ, und OrderExtractionResult aus src.models liefert sowohl die Schemadefinition als auch die anschließende Pydantic-Validierung. Die Initialisierung von Groq(api_key=os.getenv("GROQ_API_KEY")) innerhalb der Funktion funktioniert für einfache Skripte problemlos; für höhere Lasten im Produktivbetrieb lässt sich der Client jedoch auch einmalig außerhalb der Funktion instanziieren und um Fehlerbehandlung für fehlende API-Keys sowie ungültige JSON- oder Validierungsantworten ergänzen.

**main.py:**

Der Code in der Datei main.py ist das Hauptskript eines Automatisierungssystems, das unstrukturierte Bestellnachrichten aus verschiedenen Studios ausliest, gültige Bestellungen zusammenrechnet und unvollständige Angaben herausfiltert. Zuerst lädt das Programm notwendige Hilfsfunktionen sowie beispielhafte Bestelltexte und sendet diese an ein Sprachmodell (LLM), das auf der ultraschnellen Groq-Infrastruktur läuft. Die KI erkennt in den freien Texten, welches Studio welchen Artikel in welcher Menge bestellt hat, und wandelt diese Informationen in ein festes, maschinenlesbares Datenformat um.

Im nächsten Schritt übernimmt klassischer Python-Code die weitere Verarbeitung der ausgelesenen Rohdaten, ohne dass erneut eine KI benötigt wird. Alle vollständigen Bestellungen werden nach Artikelnamen gruppiert und ihre Gesamtmengen werden mathematisch addiert. Gleichzeitig filtert das System alle unvollständigen Posten heraus, bei denen beispielsweise eine genaue Mengenangabe oder die Verpackungseinheit fehlt, damit die Gesamtsumme nicht verfälscht wird.

Abschließend gibt main.py die aufbereiteten Ergebnisse in zwei übersichtlichen Bereichen in der Konsole aus. Im ersten Teil erscheint eine saubere Tabelle mit der Gesamtsumme aller gültigen Artikel, während im zweiten Teil alle offenen Rückfragen inklusive eines von der KI vorformulierten Frageentwurfs für das jeweilige Studio aufgelistet werden. Ganz am Ende wird der gesamte Bericht zusätzlich im reinen JSON-Format ausgegeben, damit die Daten problemlos an andere Systeme weitergeleitet werden können.

**models.py:**

In models.py werden mithilfe der Bibliothek Pydantic die festen Datenstrukturen (Baupläne) für das gesamte Bestellsystem definiert, damit die KI und der restliche Python-Code sicher und fehlerfrei zusammenarbeiten können. Diese sogenannten Datenmodelle legen nicht nur exakt fest, welche Felder existieren und welchen Datentyp sie haben müssen (wie Text, Ganzzahl oder Wahrheitswert), sondern geben dem Sprachmodell über integrierte Beschreibungen (Field) auch direkte Handlungsanweisungen. So weiß die KI genau, dass sie Produktnamen auf Deutsch standardisieren und Einheiten im Singular (wie „Packung“ oder „Rolle“) ausgeben muss.

Der erste Teil der Datei widmet sich der Erfassung der Rohdaten durch die KI und besteht aus den Klassen ExtractedItem und OrderExtractionResult. Ein einzelner Bestellposten (ExtractedItem) speichert den Studionamen, den Artikelnamen sowie die optionale Menge und Einheit, wobei die letzten beiden Felder leer (None) bleiben dürfen, falls sie in der Nachricht fehlen. Über das Wahrheitsfeld is_complete entscheidet die KI, ob alle nötigen Angaben vorhanden sind – ist dies nicht der Fall, generiert sie im Feld clarification_question sofort eine höfliche deutsche Rückfrage an das jeweilige Studio, während OrderExtractionResult all diese Einzelposten in einer Gesamtliste bündelt.

Im zweiten Teil der Datei werden schließlich die Strukturen für die fertige Auswertung und den Abschlussbericht festgelegt. Die Klasse AggregatedOrderLine definiert eine zusammengefasste Bestellzeile für die spätere Gesamttabelle, bestehend aus Artikelname, Einheit, einer Liste aller bestellenden Studios sowie der berechneten Gesamtmenge (total_quantity), die durch die Regel ge=0 garantiert nicht negativ sein kann. Abschließend führt ProcessedOrderReport diese gültigen, summierten Bestellungen (valid_aggregated_orders) und die Liste der noch offenen Rückfragen (pending_clarifications) in einem einzigen Objekt zusammen, das main.py am Ende als Tabelle und JSON ausgibt.


**processor.py:**

In processor.py findet die eigentliche Geschäftslogik statt, indem die von der KI ausgelesenen Rohdaten mithilfe von klassischem Python-Code sortiert, zusammengerechnet und gefiltert werden. Die Funktion aggregate_orders nimmt das strukturierte KI-Ergebnis (OrderExtractionResult) entgegen und bereitet zunächst ein spezielles Wörterbuch (defaultdict) zum Gruppieren der gültigen Artikel sowie eine leere Liste für unvollständige Bestellungen vor. Danach durchläuft das Programm in einer Schleife jeden einzelnen Bestellposten und prüft streng, ob das Kontrollfeld is_complete wahr ist und sowohl eine Menge als auch eine Verpackungseinheit vorliegen.

Wenn alle Angaben vollständig sind, bildet der Code aus dem bereinigten Artikelnamen und der Einheit einen eindeutigen Schlüssel, um gleiche Produkte zuverlässig zusammenzufassen. Die jeweilige Bestellmenge wird zur bisherigen Gesamtsumme addiert und das bestellende Studio wird zusammen mit seiner individuellen Teilmenge (zum Beispiel im Format „Innenstadt (5 Packung)“) in die Liste der Auftraggeber eingetragen. Fehlt hingegen eine Information oder ist der Posten als unvollständig markiert, wird der Artikel nicht mitgezählt, sondern direkt in die Liste pending_clarifications verschoben, damit er später nachgefragt werden kann.

Im letzten Schritt wandelt die Funktion die gesammelten Gruppen in saubere, nach dem Bauplan aus models.py geprüfte Objekte (AggregatedOrderLine) um. Abschließend verpackt sie sowohl diese fertigen, summierten Bestellzeilen als auch die offenen Rückfragen in das übergeordnete Berichtsobjekt ProcessedOrderReport und gibt dieses an main.py zurück, wo es am Ende als übersichtliche Tabelle und JSON ausgegeben wird.

**sample_order_messages.py:**

In sample_order_messages.py sind realistische, unstrukturierte Beispielnachrichten verschiedener Studios hinterlegt, die als Testdaten für den gesamten Programmablauf dienen. Die Variable SAMPLE_MESSAGES ist eine Python-Liste mit drei Freitext-Bestellungen aus den Hamburger Standorten Innenstadt, Eimsbüttel und Wandsbek, die genau so aus einem echten Chat oder einer E-Mail stammen könnten. Diese Texte dienen als Eingabematerial, um zu testen, wie zuverlässig das Groq-Sprachmodell menschliche Umgangssprache in strukturierte Daten übersetzen kann.

Inhaltlich decken diese drei Nachrichten gezielt verschiedene typische Szenarien des Bestellprozesses ab. Während die Nachrichten aus Innenstadt und Wandsbek ausschließlich vollständige Angaben enthalten (etwa „3 Packungen Nitrilhandschuhe M“ oder „1 Rolle Tape“), kombiniert die Nachricht aus Eimsbüttel eine klare Bestellung („2 Packungen Nitrilhandschuhe M“) mit einem unvollständigen Wunsch („und noch Kochsalzlösung“), bei dem sowohl die Menge als auch die Verpackungseinheit fehlen. Dadurch lässt sich überprüfen, ob die KI vollständige Artikel über verschiedene Studios hinweg korrekt trennt und unklare Posten zuverlässig erkennt.

Im Zusammenspiel mit dem restlichen System sorgt genau diese Mischung für einen kompletten Funktionstest der gesamten Anwendung. Während processor.py später beispielsweise die Nitrilhandschuhe M aus Innenstadt (3 Packungen) und Eimsbüttel (2 Packungen) automatisch zu einer Gesamtmenge von 5 Packungen zusammenrechnet, wird die unvollständige Kochsalzlösung aus Eimsbüttel nicht mit den 2 Flaschen aus Wandsbek vermischt, sondern landet separat bei den offenen Rückfragen inklusive eines vorformulierten Frageentwurfs.

tests: 

**test_processor.py:** 

In test_processor.py befindet sich ein automatisierter Softwaretest (Unit-Test), der die Berechnungs- und Filterlogik aus processor.py ganz ohne echte KI-Anfrage überprüft. Dazu erstellt die Testfunktion test_aggregation_and_exclusion zunächst künstliche Testdaten (mock_extraction), die genau so aussehen, als kämen sie direkt vom Groq-Sprachmodell. Dieses fiktive Ergebnis enthält vier Bestellposten: zweimal vollständige Nitrilhandschuhe M (3 und 2 Packungen), einmal vollständige Kochsalzlösung aus Wandsbek (2 Flaschen) sowie eine unvollständige Bestellung für Kochsalzlösung aus Eimsbüttel, bei der die Menge fehlt (quantity=None, is_complete=False).

Anschließend übergibt der Test diese simulierten Rohdaten an die eigentliche Verarbeitungsfunktion aggregate_orders und prüft mithilfe von assert-Anweisungen (Zusicherungen), ob das zurückgegebene Ergebnis exakt den Erwartungen entspricht. Zuerst kontrolliert der Code, ob die Nitrilhandschuhe M aus Innenstadt und Eimsbüttel korrekt zur Gesamtmenge 5 addiert wurden und beide Studios mit ihren Teilmengen in der Liste stehen. Danach stellt der Test sicher, dass bei der Kochsalzlösung ausschließlich die 2 Flaschen aus Wandsbek gezählt wurden, während der unklare Posten aus Eimsbüttel sauber aus der Gesamtsumme herausgehalten wurde.

Im letzten Abschnitt überprüft die Funktion noch die Liste der offenen Rückfragen (pending_clarifications), um zu garantieren, dass keine unvollständige Bestellung verloren gegangen ist. Hier wird konkret abgefragt, ob sich genau ein Element in dieser Liste befindet und ob dieses tatsächlich dem Studio Eimsbüttel zugeordnet ist. Durch diesen Aufbau lässt sich jederzeit in Sekundenbruchteilen und völlig kostenlos testen, ob Änderungen an der Geschäftslogik fehlerfrei funktionieren.


• .env: In dieser Datei werden sensible Zugangsdaten und geheime Schlüssel (wie z. B. der GROQ_API_KEY) sicher getrennt vom eigentlichen Programmcode gespeichert.

• .gitignore: Diese Konfigurationsdatei legt fest, welche Dateien und Ordner (wie die geheime .env-Datei oder temporäre Cache-Dateien) von der Versionsverwaltung Git ignoriert und nicht hochgeladen werden sollen.

• requirements.txt: Diese Datei listet alle externen Python-Bibliotheken (wie z. B. groq, pydantic, python-dotenv oder pytest) auf, die installiert werden müssen, damit das Projekt fehlerfrei läuft.

------------------------------------------------------------------------------------------------------ 
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