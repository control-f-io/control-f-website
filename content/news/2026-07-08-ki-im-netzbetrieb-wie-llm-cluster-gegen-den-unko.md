datum:   2026-07-08
autor:   Simon Deussen
minuten: 6
themen:  Architektur, Energie
bild:    news/ki-im-netzbetrieb-wie-llm-cluster-gegen-6e6d5535.png
titel:   KI im Netzbetrieb: Wie LLM-Cluster gegen den unkontrollierten Datenabfluss helfen – und was noch kommt
title:   AI in grid operations: how LLM clusters help against uncontrolled data outflow – and what comes next

Seit dem 6. Dezember 2025 gilt das NIS2-Umsetzungsgesetz und soll die Cybersicherheit stärken. Es hebt das Cybersicherheitsniveau in Sektoren an, deren Ausfall die Versorgung gefährden würde, und nimmt dafür erstmals auch die Führungsebene direkt in die Pflicht. Für Verteilnetzbetreiber, Stadtwerke und Energieversorger heißt das konkret: Die Geschäftsleitung haftet nach § 38 BSIG persönlich für Versäumnisse bei der Cybersicherheit, und Verstöße können mit Bußgeldern von bis zu zehn Millionen Euro oder zwei Prozent des weltweiten Jahresumsatzes geahndet werden.

Die Energiewirtschaft gehört zu den Sektoren, in denen „State of the Art“-Sicherheitsmaßnahmen zwingend vorgeschrieben sind. In dieser Lage lohnt ein Blick auf eine Praxis, die in fast jedem Unternehmen längst stattfindet, aber selten in einer Risikoanalyse auftaucht: die informelle Nutzung öffentlich zugänglicher KI-Dienste.

Schauen wir uns dafür ein paar alltägliche Beispiele an. Ein Mitarbeiter kopiert einen Auszug aus einem Netzberechnungsprotokoll in ChatGPT, um sich eine Zusammenfassung schreiben zu lassen. Eine Sachbearbeiterin lässt sich von einem Chatbot eine Kundenmail formulieren und fügt dabei personenbezogene Daten ein. Beides passiert sehr oft „auf dem kurzen Dienstweg“, ohne dass jemand darüber Buch führt, und häufig ohne bösen Willen. Was im vergangenen Jahr noch als pragmatische Selbsthilfe durchging, ist unter NIS2 ein unkontrollierter Datenabfluss an einen nicht bewerteten Dienstleister, und damit ein Haftungsrisiko, für das die Geschäftsführung bei schuldhaften Verstößen persönlich einstehen muss.

Die naheliegende Reaktion, KI-Nutzung schlicht zu untersagen, funktioniert in der Praxis nicht. Wo ein Werkzeug einen echten Nutzen stiftet, wird es verwendet, notfalls über das private Smartphone und damit außerhalb jeder Kontrolle. Die sinnvolle Frage lautet deshalb nicht, ob KI im Unternehmen genutzt werden soll, sondern über welche Architektur diese Nutzung läuft. Genau hier setzen LLM-Cluster und LLM-Gateways an. Wo ist der Unterschied?

## Was heute geht: der lokale LLM-Cluster

Eine sofort verfügbare Problemlösung ist ein lokal betriebenes Sprachmodell. Konkret ist das eine Maschine, die im eigenen Rechenzentrum oder Büro steht und eine Modell-Instanz hostet, die direkt angesprochen wird. Alle Anfragen und alle Daten landen dort und nirgendwo sonst. Für einen Netzbetreiber, dessen sensibelste Anfragen Betriebsdaten aus der Netzsteuerung oder personenbezogene Kundendaten enthalten, löst das den Kern des Problems: Diese Daten verlassen das Haus nicht. Lokale LLMs sind allerdings meist nicht so leistungsfähig, weil sie in der Regel mit viel weniger Daten lernen und ihnen insgesamt weniger Ressourcen zur Verfügung stehen als den kommerziellen Anbietern aus den USA.

Ein großes Sprachmodell (Large Language Model, kurz LLM) ist ein KI-System, das aus großen Textmengen gelernt hat, Sprache zu verarbeiten und zu erzeugen. Es beantwortet Fragen, fasst zusammen oder formuliert Texte, indem es statistisch das jeweils wahrscheinlichste nächste Wort ergänzt.

Lokal betriebene Modelle sind für viele Alltagsaufgaben gut genug, bei komplexen Anfragen sind ihnen die großen, außerhalb Europas oder außerhalb der Firma gehosteten Modelle aber deutlich überlegen. Wer maximale Datenhoheit will, zahlt sie also mit einem Verzicht auf die Spitzenleistung der jeweils stärksten Modelle. Für einen erheblichen Teil der internen KI-Nutzung ist dieser Verzicht vertretbar, und der Gewinn an Kontrolle ist unmittelbar.

## Governance-Gateways: verfügbar, aber nicht das Ende der Geschichte

Zwischen dem rein lokalen Betrieb und der ungeregelten Nutzung externer Dienste hat sich in den vergangenen zwei Jahren eine eigene Produktkategorie etabliert, die sogenannten LLM- oder AI-Gateways. Diese Werkzeuge sind kommerziell verfügbar, teils quelloffen, und sie leisten das, was aus Compliance-Sicht zählt: Sie erkennen und filtern sensible Inhalte wie personenbezogene Daten bereits auf der Gateway-Ebene, bevor eine Anfrage einen externen Anbieter erreicht, sie protokollieren jede Anfrage nachvollziehbar, und sie lassen sich innerhalb der eigenen Netzwerkgrenze betreiben, sodass der regulierte Datenverkehr nicht über einen fremden Cloud-Dienst läuft.

Damit adressieren sie das Problem der „Shadow AI“, also der unkontrollierten KI-Nutzung an IT und Führung vorbei, direkt. Man sollte sie allerdings nicht überschätzen. Diese Gateways sind vom Grundgedanken her darauf gebaut, Anfragen kontrolliert an externe Anbieter weiterzuleiten und dabei zu filtern und zu protokollieren, nicht darauf, maximale Souveränität herzustellen. Und sie sind branchenneutral. Eine Abbildung der spezifischen regulatorischen Logik des Energiesektors, etwa der Anforderungen aus dem IT-Sicherheitskatalog, bringen sie nicht von sich aus mit. Sie sind ein solides Fundament, keine schlüsselfertige Antwort für einen KRITIS-Betreiber.

## Der nächste Schritt: das intelligente, souveräne Gateway

Der eigentlich interessante Ansatz geht einen Schritt weiter und verbindet beides. Technisch gesehen wäre dieses Gateway selbst ein lokales Sprachmodell, das jede Anfrage in Echtzeit prüft und entscheidet, wie sie behandelt wird. Enthält eine Anfrage sensible Informationen, die das Haus nicht verlassen dürfen, wird sie lokal beantwortet. Ist die Anfrage unkritisch, aber komplex, leitet das Gateway sie an ein stärkeres externes Modell weiter. Der Filter entscheidet also anhand von zwei Kriterien zugleich, dem Dateninhalt und der Komplexität, und holt so das Beste aus beiden Welten: Datenhoheit dort, wo sie nötig ist, und Spitzenleistung dort, wo sie unbedenklich ist.

An diesem Punkt ist ehrlicherweise Vorsicht geboten. Die einzelnen Bausteine dafür existieren, und die Forschung zu solchem sensibilitäts- und komplexitätsbasierten Routing zwischen lokalen und externen Modellen ist derzeit sehr aktiv. Ein fertiges, gehärtetes Produkt, das genau diese Logik für die regulatorischen Anforderungen eines deutschen Energieversorgers mitbringt, gibt es aber noch nicht von der Stange. Wer das aufbauen will, betritt heute noch Neuland.

## Was ein LLM-Gateway technisch leistet

Ein LLM-Gateway ist keine zusätzliche Sicherheitsschicht, die man über bestehende Prozesse legt. Es ist die Stelle, an der KI-Anfragen aus dem Unternehmen gebündelt, geprüft und protokolliert werden, bevor sie ein System verlassen. Der Unterschied zwischen einem Firmen-Account bei einem KI-Anbieter und einem echten Gateway liegt in vier Funktionen.

### Datenklassifizierung vor dem Prompt

Bevor eine Anfrage überhaupt weitergeleitet wird, prüft das Gateway, was sie enthält. Betriebsdaten aus der Netzsteuerung, personenbezogene Kundendaten und fachlich unkritische Anfragen werden unterschieden. Diese Klassifizierung entscheidet über alles Weitere und verhindert, dass sensible Inhalte unbemerkt an einen externen Dienst gelangen. Sie ist die technische Entsprechung dessen, was NIS2 an Risikobewertung ohnehin verlangt, angewendet auf jeden einzelnen Vorgang statt einmal jährlich auf dem Papier.

### Modellrouting nach Klassifizierung

Auf Grundlage der Klassifizierung entscheidet das Gateway, welches Modell eine Anfrage beantwortet: das lokale Modell im eigenen Rechenzentrum für alles, was das Haus nicht verlassen darf, ein externes Modell für unkritische, aber anspruchsvolle Aufgaben. Die Entscheidung liegt damit in der Architektur und nicht im Ermessen einzelner Mitarbeitender. Das ist der eigentliche Unterschied zu einer Nutzungsrichtlinie, die zwar existiert, aber im Arbeitsalltag niemanden bindet.

### Zugriffskontrolle und Protokollierung

Jede Anfrage ist einer Person, einer Rolle und einem Zeitpunkt zugeordnet und wird nachvollziehbar protokolliert. Rollenbasierte Berechtigungen begrenzen zusätzlich, wer welche Modelle und welche Datenklassen überhaupt nutzen darf. Für ein Audit oder eine Meldung nach NIS2 ist das der entscheidende Punkt: Erst das Protokoll erlaubt die Aussage, welche Daten wann an welches Modell gegangen sind. Ohne Gateway bleibt an dieser Stelle eine Lücke, die sich im Nachhinein nicht schließen lässt.

### Lieferkettensicherheit

Ein externes Sprachmodell ist ein Dienstleister wie jeder andere und muss entsprechend bewertet werden: Ort der Verarbeitung, Vertragsgrundlage, Umgang mit Eingaben als Trainingsdaten, eingesetzte Subunternehmer. NIS2 verlangt die Sicherheit der Lieferkette ausdrücklich, bei KI-Diensten ist sie bislang aber selten dokumentiert. Das Gateway ist die Stelle, an der eine solche Bewertung technisch wirksam wird, weil ausschließlich freigegebene Anbieter überhaupt erreichbar sind.

Hinzu kommen praktische Hürden, die man nicht kleinreden sollte. Sämtlichen KI-Verkehr durch ein lokales Gateway zu leiten bedeutet zusätzliche Latenz, es verlangt eine durchdachte Netzwerkadministration, und es bleibt ein Schlupfloch: Was, wenn der Mitarbeiter die interne Lösung umgeht und doch das private Handy nutzt? Das zeigt, dass auch das ausgefeilteste Gateway das Problem nicht allein technisch löst. Ohne begleitende organisatorische Regeln, klare Nutzungsrichtlinien und ein Angebot, das gut genug ist, dass niemand das Bedürfnis hat, es zu umgehen, bleibt jede technische Architektur unvollständig.

## LLM-Gateway: keine Parallelwelt zur bestehenden Pflicht

Für Netzbetreiber ist das kein neues, zusätzliches Compliance-Feld, sondern die Fortschreibung einer Anforderung, die längst besteht. Wer ein Strom- oder Gasnetz betreibt, muss bereits ein zertifiziertes Informationssicherheits-Managementsystem nach ISO/IEC 27001 und 27019 vorhalten. Die Rechtsgrundlage dafür hat sich mit dem NIS2-Umsetzungsgesetz geändert: An die Stelle des bisherigen § 11 Abs. 1a und 1b EnWG tritt § 5c EnWG. Die bestehenden IT-Sicherheitskataloge der Bundesnetzagentur von 2015 und 2018 gelten laut Behörde so lange weiter, bis der überarbeitete Katalog nach neuer Rechtslage veröffentlicht ist.

Ein LLM-Gateway ist damit keine Erfindung eines neuen Problems, um eine Lösung dazu zu verkaufen. Es ist die konsequente Anwendung von Prinzipien, die in einem Information Security Management System (ISMS) ohnehin verankert sind, auf einen Kanal, der bislang unter dem Radar lief. Datenklassifizierung, Zugriffskontrolle, Nachweisbarkeit oder Lieferantenbewertung sind keine KI-spezifischen Erfindungen, sondern Kernbestandteile jedes ordentlichen Sicherheitskonzepts. Neu ist nur, dass sie jetzt auch für den Umgang mit Sprachmodellen gelten müssen.

## Fazit: LLM-Nutzung wird zunehmen, Gateways und Cluster helfen

Die Nutzung von KI im Arbeitsalltag wird zunehmen. Die Frage ist nur, ob sie in einer kontrollierten Architektur stattfindet oder in einem Graubereich, der sich im Prüfungsfall nicht erklären lässt. Wer die Architektur jetzt klärt, verschafft sich Handlungsspielraum, statt später unter Zeitdruck und womöglich nach einem Vorfall nachrüsten zu müssen. Der Aufwand, eine solche Struktur aufzubauen, ist überschaubar. Der Aufwand, ihr Fehlen im Nachhinein zu erklären, ist es nicht.

**Über control-f.** Die control-f GmbH ist ein werteorientiertes KI-Unternehmen mit Sitz in Konstanz. Seit 2022 entwickelt die Datenboutique Big-Data-Plattformen für industrielle Telemetriedaten und unterstützt Unternehmen im deutschsprachigen Raum dabei, komplexe Datenlandschaften nutzbar zu machen. Zu den Kunden gehören Konzerne und Mittelständler aus den Bereichen Anlagenbau, Automotive und Energiewirtschaft. Die Geschäftsführer Simon Deussen (Machine Learning Engineer und Gründer) und Daniel Tremer (ehemals Specialist Data Science & AI Projects bei Porsche AG) legen dabei ihren Fokus auf den Aufbau stabiler Datenarchitekturen als Grundlage für Analyse, Softwarelösungen und KI-Anwendungen wie Predictive Maintenance.

Dieser Beitrag gibt einen Überblick und ersetzt keine Rechtsberatung im Einzelfall.

--- en ---

The German NIS2 implementation act has been in force since 6 December 2025 and is intended to strengthen cybersecurity. It raises the level of cybersecurity in sectors whose failure would endanger supply, and for the first time it places direct obligations on management. For distribution grid operators, municipal utilities and energy suppliers this means one thing in concrete terms: under § 38 BSIG, management is personally liable for failures in cybersecurity, and breaches can be sanctioned with fines of up to ten million euros or two per cent of worldwide annual turnover.

The energy industry is one of the sectors in which “state of the art” security measures are mandatory. In that situation, it is worth looking at a practice that has long been taking place in almost every company but rarely appears in a risk assessment: the informal use of publicly available AI services.

Let us look at a few everyday examples. An employee copies an excerpt from a grid calculation report into ChatGPT to have a summary written. A caseworker has a chatbot draft a customer email and pastes personal data into it. Both happen very often as a quick shortcut, without anyone keeping a record, and frequently without any bad intent. What still passed as pragmatic self-help last year is, under NIS2, an uncontrolled outflow of data to an unassessed service provider — and therefore a liability risk for which management must answer personally in the case of culpable breaches.

The obvious response, simply banning the use of AI, does not work in practice. Where a tool provides real benefit, it will be used, if necessary via a private smartphone and therefore outside any control. The sensible question is therefore not whether AI should be used in the company, but which architecture that use runs through. This is exactly where LLM clusters and LLM gateways come in. What is the difference?

## What is possible today: the local LLM cluster

An immediately available solution is a locally operated language model. Concretely, that is a machine standing in your own data centre or office, hosting a model instance that is addressed directly. All requests and all data end up there and nowhere else. For a grid operator whose most sensitive requests contain operational data from grid control or personal customer data, this solves the core of the problem: that data does not leave the building. Local LLMs are usually less capable, however, because they are typically trained on far less data and have fewer resources available overall than the commercial providers from the United States.

A large language model (LLM) is an AI system that has learned from large volumes of text how to process and produce language. It answers questions, summarises or drafts texts by statistically completing the most probable next word.

Locally operated models are good enough for many everyday tasks, but for complex requests the large models hosted outside Europe or outside the company are clearly superior. Anyone who wants maximum data sovereignty pays for it by forgoing the peak performance of the strongest models. For a considerable share of internal AI use that trade-off is acceptable, and the gain in control is immediate.

## Governance gateways: available, but not the end of the story

Between purely local operation and the unregulated use of external services, a product category of its own has established itself over the past two years: so-called LLM or AI gateways. These tools are commercially available, in part open source, and they deliver what counts from a compliance perspective. They detect and filter sensitive content such as personal data at the gateway level, before a request reaches an external provider; they log every request in a traceable way; and they can be operated inside your own network boundary, so that regulated data traffic does not pass through a third-party cloud service.

That addresses the problem of “shadow AI” — uncontrolled AI use bypassing IT and management — head-on. They should not be overestimated, though. By design, these gateways are built to forward requests to external providers in a controlled way, filtering and logging them along the way, not to establish maximum sovereignty. And they are industry-neutral. They do not come with a representation of the specific regulatory logic of the energy sector, such as the requirements of the IT security catalogue. They are a solid foundation, not a turnkey answer for an operator of critical infrastructure.

## The next step: the intelligent, sovereign gateway

The genuinely interesting approach goes one step further and combines both. Technically, this gateway would itself be a local language model that checks every request in real time and decides how it is handled. If a request contains sensitive information that must not leave the building, it is answered locally. If the request is uncritical but complex, the gateway forwards it to a stronger external model. The filter therefore decides on two criteria at once, data content and complexity, and gets the best of both worlds: data sovereignty where it is needed, and peak performance where it is unproblematic.

At this point, honesty calls for caution. The individual building blocks exist, and research into such sensitivity- and complexity-based routing between local and external models is currently very active. A finished, hardened product that brings exactly this logic to the regulatory requirements of a German energy supplier is not yet available off the shelf. Anyone who wants to build it is still entering new territory today.

## What an LLM gateway does technically

An LLM gateway is not an additional security layer laid on top of existing processes. It is the point at which AI requests from across the company are consolidated, checked and logged before they leave a system. The difference between a corporate account with an AI provider and a real gateway lies in four functions.

### Data classification before the prompt

Before a request is forwarded at all, the gateway checks what it contains. Operational data from grid control, personal customer data and technically uncritical requests are distinguished. This classification governs everything that follows and prevents sensitive content from reaching an external service unnoticed. It is the technical equivalent of the risk assessment that NIS2 requires anyway, applied to every single transaction instead of once a year on paper.

### Model routing based on classification

On the basis of the classification, the gateway decides which model answers a request: the local model in your own data centre for anything that must not leave the building, an external model for uncritical but demanding tasks. The decision therefore sits in the architecture rather than in the discretion of individual employees. That is the real difference from a usage policy which exists on paper but binds no one in day-to-day work.

### Access control and logging

Every request is attributed to a person, a role and a point in time, and is logged traceably. Role-based permissions additionally limit who may use which models and which data classes at all. For an audit or a notification under NIS2, this is the decisive point: only the log makes it possible to state which data went to which model and when. Without a gateway, a gap remains here that cannot be closed after the fact.

### Supply chain security

An external language model is a service provider like any other and has to be assessed accordingly: place of processing, contractual basis, treatment of inputs as training data, subcontractors used. NIS2 explicitly requires supply chain security, yet for AI services it is rarely documented so far. The gateway is the place where such an assessment takes technical effect, because only approved providers are reachable at all.

On top of that come practical hurdles that should not be played down. Routing all AI traffic through a local gateway means additional latency, it requires well-considered network administration, and one loophole remains: what if an employee bypasses the internal solution and uses a private phone after all? This shows that even the most sophisticated gateway does not solve the problem by technical means alone. Without accompanying organisational rules, clear usage policies and an offering good enough that no one feels the need to circumvent it, every technical architecture remains incomplete.

## LLM gateway: not a parallel world to existing obligations

For grid operators this is not a new, additional compliance field but the continuation of a requirement that has long existed. Anyone operating an electricity or gas grid must already maintain a certified information security management system in line with ISO/IEC 27001 and 27019. The legal basis for this has changed with the NIS2 implementation act: § 5c EnWG replaces the previous § 11 (1a) and (1b) EnWG. According to the authority, the existing IT security catalogues of the Federal Network Agency from 2015 and 2018 continue to apply until the revised catalogue under the new legal framework is published.

An LLM gateway is therefore not the invention of a new problem in order to sell a solution for it. It is the consistent application of principles already anchored in an information security management system (ISMS) to a channel that has so far flown under the radar. Data classification, access control, auditability and supplier assessment are not AI-specific inventions but core components of any sound security concept. All that is new is that they now have to apply to dealing with language models as well.

## In closing: LLM use will grow, gateways and clusters help

The use of AI in day-to-day work will increase. The only question is whether it takes place within a controlled architecture or in a grey area that cannot be explained in the event of an audit. Those who settle the architecture now gain room for manoeuvre instead of having to retrofit later under time pressure and possibly after an incident. The effort of building such a structure is manageable. The effort of explaining its absence after the fact is not.

**About control-f.** control-f GmbH is a values-driven AI company based in Konstanz. Since 2022, the data boutique has been building big data platforms for industrial telemetry data and helping companies in German-speaking Europe make complex data landscapes usable. Its clients include large corporations and mid-sized companies from plant engineering, automotive and the energy industry. Managing directors Simon Deussen (machine learning engineer and founder) and Daniel Tremer (formerly Specialist Data Science & AI Projects at Porsche AG) focus on building stable data architectures as the foundation for analytics, software solutions and AI applications such as predictive maintenance.

This article provides an overview and does not replace legal advice in individual cases.

Kategorie / Category: [Blogposts](https://www.control-f.io/blog/categories/blogposts)
