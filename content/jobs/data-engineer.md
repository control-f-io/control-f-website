kennung:    CF-2026-DE-01
bereich:    Plattform
area:       Platform
titel:      {Data Engineer} (m/w/d)
title:      Data Engineer (m/f/d)
anriss:     Sie bauen die Strecken, auf denen Anlagendaten ankommen: Anbindung, Modellierung, Qualitätssicherung. Ohne dieses Fundament ist jede Auswertung darüber geraten.
excerpt:    You build the routes along which plant data arrives: connection, modelling, quality assurance. Without that foundation, every analysis on top of it is guesswork.
standort:   Konstanz, hybrid
location:   Konstanz, hybrid
anstellung: Festanstellung
employment: Permanent employment
umfang:     Voll- oder Teilzeit
hours:      Full or part time
start:      ab sofort
starts:     immediately
adresse:    Am Seerhein 6, 78467 Konstanz. Zwei Tage die Woche vor Ort, der Rest frei eingeteilt.
address:    Am Seerhein 6, 78467 Konstanz. Two days a week on site, the rest as you arrange it.
verguetung: 58.000–72.000 € brutto im Jahr, je nach Erfahrung. Kein Verhandeln um die Zahl, sondern um die Einordnung.
salary:     €58,000–72,000 gross a year, depending on experience. No haggling over the number, only over where you sit in the range.
gehalt_von: 58000
gehalt_bis: 72000
art:        FULL_TIME, PART_TIME
seit:       2026-07-06
frist:      2026-09-30

Die Daten, mit denen wir arbeiten, liegen fast immer schon vor — nur eben in einer Steuerung von 2004, in einem OPC-UA-Server, den seit der Abnahme niemand angefasst hat, und in einer CSV-Ablage auf einem Netzlaufwerk. Sie bauen die Strecke dazwischen: Anbindung, Modellierung, Qualitätssicherung, bis eine Zahl, die im Betrieb gilt, auch in der Plattform gilt.

Das ist keine Arbeit an einem Referenzdatensatz. Wenn wir eine Anlage aufnehmen, fahren Sie mit — weil die Frage, was ein Signal bedeutet, in der Halle beantwortet wird und nicht im Datenblatt. Was Sie danach bauen, betreiben Sie auch: Es gibt hier kein Team, das Ihre Pipelines übernimmt, wenn sie einmal laufen.

Sie kommen in eine Plattform, die es gibt, und in Strecken, die laufen. In den ersten Wochen übernehmen Sie eine bestehende Anbindung, danach die nächste Anlage von der ersten Messung an.

## Was Sie tun

- Anlagen anbinden: OPC UA, Modbus, MQTT, und den Rest, der als Datei kommt. Pro Anbindung eine Entscheidung darüber, was von der Anlage überhaupt gelesen werden muss.

- Datenmodelle bauen, die eine Anlage beschreiben und nicht eine Tabelle: Signale, Aggregate, Zustände — versioniert, damit eine Auswertung von letztem Jahr auch nächstes Jahr dasselbe bedeutet.

- Qualität messbar machen. Ein fehlender Messwert, ein eingefrorener Sensor und ein umgestellter Skalierungsfaktor sehen in der Datenbank gleich aus und sind drei verschiedene Vorfälle.

- Die Strecken betreiben: Orchestrierung, Alarmierung, Nachlauf nach einem Ausfall. Was nachts abbricht, muss morgens ohne Handarbeit vollständig sein.

- Mit den Kolleginnen und Kollegen aus der Analytik am selben Modell arbeiten — sie sind die ersten, die merken, wenn eine Definition sich verschoben hat.

## Was notwendig ist

- Drei Jahre oder mehr an Datenstrecken im Betrieb, nicht nur im Projekt.

- Python auf einem Niveau, auf dem Sie Code von anderen aufräumen; SQL auf einem Niveau, auf dem Sie einen Abfrageplan lesen.

- Erfahrung mit Zeitreihen und mit dem, was sie schwierig macht: Zeitzonen, Abtastraten, Nachträge, Lücken.

- Deutsch für die Halle, Englisch für die Dokumentation.

## Was hilft und keine Bedingung ist

- Industrieerfahrung — SPS, Leitsystem, Feldbus. Wer sie nicht hat, bekommt sie bei der ersten Anlage.

- Kubernetes, Terraform, alles rund um den Betrieb der Plattform selbst.

- Ein Studium. Wir haben im Team beides und die Arbeit unterscheidet sich nicht danach.

--- en ---

The data we work with is almost always there already — only in a controller from 2004, in an OPC UA server nobody has touched since commissioning, and in a CSV folder on a network drive. You build the route in between: connection, modelling, quality assurance, until a number that holds in operation also holds in the platform.

This is not work on a reference data set. When we take on a plant, you come along — because the question of what a signal means is answered in the hall and not in the data sheet. And what you build afterwards, you also operate: there is no team here that takes your pipelines off you once they run.

You come into a platform that exists and routes that are running. In the first weeks you take over an existing connection, then the next plant from the first measurement on.

## What you do

- Connecting plant: OPC UA, Modbus, MQTT, and the rest that arrives as a file. One decision per connection about what actually has to be read from the machine.

- Building data models that describe a plant and not a table: signals, aggregates, states — versioned, so that an analysis from last year still means the same thing next year.

- Making quality measurable. A missing reading, a frozen sensor and a changed scaling factor look the same in the database and are three different incidents.

- Operating the routes: orchestration, alerting, catch-up after an outage. What breaks at night has to be complete in the morning without anyone touching it.

- Working on the same model as the colleagues in analytics — they are the first to notice when a definition has shifted.

## What is required

- Three years or more of data routes in operation, not only in projects.

- Python at a level where you tidy up other people's code; SQL at a level where you read a query plan.

- Experience with time series and with what makes them difficult: time zones, sampling rates, late arrivals, gaps.

- German for the hall, English for the documentation.

## What helps and is not a condition

- Industrial experience — PLC, control system, fieldbus. Anyone without it picks it up on the first plant.

- Kubernetes, Terraform, everything around running the platform itself.

- A degree. We have both in the team and the work does not differ by it.
