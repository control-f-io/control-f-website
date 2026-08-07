datum:   2025-01-01
autor:   Daniel Tremer
minuten: 2
titel:   Digitale Zwillinge im Energiesektor: Simulation trifft Realität
title:   Digital twins in the energy sector: simulation meets reality

In Ausschreibungen steht „digitaler Zwilling“, gemeint ist aber meistens eines von drei sehr verschiedenen Dingen. Welches, entscheidet über die Architektur — und darüber, ob am Ende jemand dem Ergebnis traut.

## Geometrie, Simulation, Zwilling

Ein Geometriemodell bildet eine Anlage ab. Es wird gerechnet und ist danach fertig. Eine Simulation rechnet ein Verhalten unter Annahmen, die jemand gesetzt hat. Ein Zwilling dagegen hat einen Zustand, der mit der echten Anlage mitläuft — und dieser Zustand veraltet in dem Moment, in dem er geschrieben wird.

Nur das dritte verdient den Namen, und nur das dritte stellt Anforderungen an alles, was darunter liegt. Wer einen Zwilling bestellt und ein Modell meint, kauft eine Visualisierung.

## Das Fundament ist Telemetrie

Bevor irgendetwas simuliert wird, muss die Datenaufnahme stimmen. In den Projekten, die wir seit 2022 begleitet haben, lagen die Probleme fast immer in derselben Schicht: Zeitstempel ohne Zeitzone, Signale ohne Einheit, und Lücken, die als Nullen ankommen.

Der letzte Fehler ist der teuerste, weil eine Null wie eine Messung aussieht. Ein Modell kann Daten interpretieren, aber nicht erfinden — und ein Zwilling, der auf Nullen rechnet, liefert ein Ergebnis mit derselben Selbstsicherheit wie auf echten Werten.

## Die Frage nach dem erlaubten Versatz

Die zweite Frage nach der Datenqualität ist die nach der Latenz. Sie wird selten gestellt und entscheidet trotzdem über die halbe Architektur, weil Kosten und Aktualität hier direkt gegeneinander stehen: Batch für Berichte und Abrechnung, Micro-Batch für Zustandsüberwachung, Streaming für Regelung.

Die meisten Anwendungsfälle, die als „Echtzeit“ ausgeschrieben werden, sind in Wahrheit Micro-Batch. Das ist keine schlechte Nachricht — die Architektur wird um eine Größenordnung einfacher und um etwa denselben Faktor billiger.

## Fazit

Der Zwilling ist der sichtbare Teil, das Datenfundament der teure. Wer die Reihenfolge umdreht, bekommt eine sehr schöne Visualisierung von Daten, denen niemand traut.

--- en ---

Tenders say "digital twin", but they usually mean one of three very different things. Which one decides the architecture — and whether anyone ends up trusting the result.

## Geometry, simulation, twin

A geometry model depicts a plant. It is computed and then it is finished. A simulation computes behaviour under assumptions somebody set. A twin, by contrast, has a state that runs along with the real plant — and that state goes stale the moment it is written.

Only the third deserves the name, and only the third makes demands of everything underneath it. Order a twin and mean a model, and you have bought a visualisation.

## The foundation is telemetry

Before anything is simulated, the data capture has to be right. In the projects we have supported since 2022, the problems were almost always in the same layer: timestamps without a time zone, signals without a unit, and gaps that arrive as zeros.

The last is the most expensive, because a zero looks like a measurement. A model can interpret data but not invent it — and a twin computing on zeros delivers a result with the same confidence as one computing on real values.

## The question of permissible lag

The second question after data quality is latency. It is rarely asked and still decides half the architecture, because cost and currency work directly against each other here: batch for reports and billing, micro-batch for condition monitoring, streaming for control.

Most use cases tendered as "real time" are in fact micro-batch. That is not bad news — the architecture becomes an order of magnitude simpler and about the same factor cheaper.

## In closing

The twin is the visible part, the data foundation the expensive one. Reverse the order and you get a very handsome visualisation of data nobody trusts.
