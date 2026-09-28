datum:   2026-09-28
autor:   Pressestelle
minuten: 13
themen:  KI, Datenplattform
bild:    news/offene-ki-modelle-welche-es-gibt-und-wel-db13c04b.png
titel:   Offene KI-Modelle: Welche es gibt und welche davon man wirklich betreiben kann
title:   Open AI models: which ones exist and which ones you can realistically run

**Die üblichen Ranglisten sortieren nach Benchmark. Für jeden, der ein Modell selbst betreiben will, ist das die falsche Sortierung. Nützlicher ist eine andere Frage: Was passt auf welche Hardware?**

Wer sich heute nach offenen Modellen umsieht, findet vor allem Bestenlisten. Die sind nicht falsch, aber sie beantworten eine Frage, die sich in der Praxis selten stellt. Denn zwischen „offene Gewichte verfügbar“ und „wirtschaftlich selbst betreibbar“ liegen bei den größten Modellen Welten. Nützlicher ist deshalb eine andere Sortierung: Was passt auf welche Hardware?

Open Source im klassischen Sinn ist davon allerdings nicht alles. Viele der heute verfügbaren Modelle sind Open-Weight-Modelle: Die Gewichte werden veröffentlicht, oft zusammen mit Inferenzcode und Dokumentation, aber nicht zwingend mit vollständigen Trainingsdaten und Trainingscode. Man kann die Modelle herunterladen, betreiben und je nach Lizenz anpassen. Einige Projekte gehen deutlich weiter. NVIDIA veröffentlicht bei Nemotron 3 Nano neben den Gewichten auch große Teile der Trainingsdaten und Trainingsrezepte. Swiss AI veröffentlicht bei Apertus ebenfalls Trainingsinfrastruktur und Skripte zur Rekonstruktion der Trainingsdaten. Die Lizenzen reichen von Apache 2.0 über MIT-Varianten bis zu eigenen Modelllizenzen.

**Was bedeuten die Zahlen?**

Für die Hardwareplanung sind deshalb drei Größen entscheidend: die Gesamtzahl der Parameter, die Präzision der Gewichte und der Speicherbedarf des KV-Caches. Bei einem MoE-Modell bestimmen die Gesamtparameter grob die Menge der zu speichernden Gewichte, während die aktiven Parameter den Rechenaufwand pro Token beeinflussen. Wie schnell ein Modell tatsächlich läuft, hängt zusätzlich von Speicherbandbreite, Attention-Architektur, Kontextlänge, Batchgröße und der Verbindung zwischen den GPUs ab.

Deshalb ist Mistral Small 4 trotz seines Namens kein kleines Modell. Es aktiviert 6,5 Milliarden Parameter, hat insgesamt aber 119 Milliarden. In geeigneter 4-Bit-Quantisierung kann es in die 60-GB-Klasse kommen; in FP8 sind es rund 119 GB, in BF16 etwa 238 GB. Es ist beim Rechenaufwand vergleichsweise sparsam, beim Speicherbedarf aber ein großes Modell.

## Klasse A: Eine einzelne Grafikkarte im Rechner

Hier betrachten wir eine einzelne GPU mit etwa 24 bis 32 GB VRAM – also eine Klasse, wie sie auch in leistungsfähigen Workstations und Spielerechnern steckt.

Qwen3.8-27B von Alibaba ist ein naheliegendes Arbeitstier: 27 Milliarden Parameter, dicht aufgebaut, und unter Apache 2.0 veröffentlicht. Es ist ein Beispiel dafür, dass nicht jedes aktuelle Modell auf MoE setzt.

Gemma 4 26B A4B steht daneben. Das Modell hat rund 25,2 Milliarden Parameter, davon 3,8 Milliarden aktiv, und nutzt 128 Experten. Die Lizenz ist Apache 2.0. Mit geeigneter Quantisierung lässt sich das Modell auf einer einzelnen 24- bis 32-GB-GPU betreiben.

Nemotron 3 Nano ist der interessante Außenseiter: 31,6 Milliarden Parameter, rund 3,6 Milliarden aktiv. NVIDIA veröffentlicht neben den Gewichten auch große Teile der Trainingsdaten und Rezepte. Das Modell steht allerdings nicht unter Apache 2.0, sondern unter der NVIDIA Open Model License.

**Technisch nachgerechnet: Klasse A**

## Klasse B: Eine Karte aus dem Rechenzentrum

Mit 80 bis 96 Gigabyte VRAM öffnet sich das Feld deutlich. Hier liegen Modelle, die mit geeigneter Quantisierung auf einer einzelnen Datacenter-GPU betrieben werden können.

gpt-oss-120b ist ein prominentes Beispiel. Das Modell hat 117 Milliarden Gesamtparameter und rund 5,1 Milliarden aktive Parameter. Die von OpenAI veröffentlichte MXFP4-Version benötigt ungefähr 60 GB VRAM und kann damit auf einer einzelnen H100 mit 80 GB betrieben werden.

Mistral Small 4 gehört ebenfalls in diese Größenordnung, wenn eine geeignete Quantisierung verwendet wird. Die offizielle Dokumentation nennt 119 Milliarden Gesamtparameter und 6,5 Milliarden aktive Parameter. Eine NVFP4-Version liegt bei ungefähr 60 GB und kann auf einer einzelnen geeigneten Blackwell-GPU betrieben werden; die FP8-Version benötigt dagegen etwa 119 GB.

Nemotron 3 Super liegt mit 120 Milliarden Gesamtparametern und 12 Milliarden aktiven Parametern ebenfalls in dieser Größenordnung. Für die konkrete Hardware hängt viel von der verwendeten Präzision ab: NVIDIA stellt unter anderem NVFP4- und FP8-Varianten bereit. Eine NVFP4-Version kann in entsprechenden Setups auf einer einzelnen 80-GB-GPU betrieben werden, während die offiziellen Deployment-Rezepte für andere Konfigurationen zwei oder mehr GPUs vorsehen.

Llama 4 Scout von Meta hat 109 Milliarden Parameter, davon 17 Milliarden aktiv, und ein Kontextfenster von bis zu 10 Millionen Tokens. Die Lizenz ist keine Apache- oder MIT-Lizenz, sondern die Llama 4 Community License. Sie erlaubt Nutzung, Veränderung und Verbreitung unter bestimmten Bedingungen. Für Produkte oder Services mit mehr als 700 Millionen monatlich aktiven Nutzern gelten zusätzliche Lizenzbedingungen. Wer Llama-Ausgaben zum Training oder zur Verbesserung eines anderen KI-Modells verwendet, muss bei einem weiterveröffentlichten Modell außerdem bestimmte Namens- und Kennzeichnungsvorgaben beachten.

Apertus 1.5 70B aus der Schweiz, entwickelt unter Beteiligung von ETH Zürich und EPFL, spielt eine andere Rolle. Das Modell steht unter Apache 2.0. Swiss AI veröffentlicht außerdem Trainingscode, Evaluationsskripte und Skripte zur Rekonstruktion der Pre-Training-Daten. Damit ist Apertus eines der Projekte, bei denen nicht nur die Gewichte, sondern auch wesentliche Teile des Entstehungsprozesses offengelegt werden.

**Technisch nachgerechnet: Klasse B**

## Klasse C: Ein Server mit mehreren Karten

Ab hier braucht es einen richtigen Aufbau mit mehreren GPUs. Je nach Modell und Quantisierung reichen zwei Karten; bei den größten Modellen werden acht oder mehr Datacenter-GPUs üblich.

Die Spanne reicht von Inkling-Small mit 276 Milliarden Parametern über Llama 4 Maverick mit 400 Milliarden und Nemotron 3 Ultra mit 550 Milliarden bis zu DeepSeek V4.1 Flash mit 552 Milliarden und Mistral Large 3 mit 675 Milliarden. Auch GLM-5.3 liegt mit rund 753 Milliarden Parametern in dieser Größenklasse.

Bei Mistral Large 3 sind 675 Milliarden Gesamtparameter und rund 41 Milliarden aktive Parameter dokumentiert. Eine offizielle NVFP4-Version ist für einen einzelnen Server mit mehreren GPUs ausgelegt; Mistral nennt für NVFP4 eine Deployment-Möglichkeit auf einem Knoten mit H100- oder A100-GPUs, für FP8 auf einem Knoten mit H200 oder B200.

GLM-5.3 hat rund 753 Milliarden Parameter. Der veröffentlichte Checkpoint liegt bei rund 756 GB und wird in FP8 ausgeliefert. Das ist kein Modell für eine einzelne 80-GB-Karte, sondern für eine Multi-GPU-Infrastruktur.

GLM-5.3 verwendet eine eigene Lizenz. Sie ist nicht MIT, enthält aber weitreichende Rechte zum Nutzen, Kopieren, Modifizieren, Verteilen und Betreiben des Modells. Wer das Modell einsetzen will, sollte deshalb die konkrete Lizenz und nicht nur das Etikett „open“ prüfen.

DeepSeek V4.1 Flash hat rund 552 Milliarden Gesamtparameter. Die Architektur ist dabei nicht einfach mit klassischen MoE-Modellen gleichzusetzen: DeepSeek nennt unterschiedliche Aktivierungswerte für Eingabe und Ausgabe. Genau deshalb sollte man bei solchen Modellen nicht allein anhand der Parameterzahl auf die tatsächliche Rechenleistung schließen.

**Technisch nachgerechnet: Klasse C**

## Klasse D: Offen, aber für normale Unternehmen außer Reichweite

An der Spitze stehen Modelle, deren Gewichte verfügbar sind, deren Betrieb aber eine Infrastruktur voraussetzt, die weit über eine normale Unternehmens-GPU hinausgeht.

Kimi K3 von Moonshot AI hat 2,8 Billionen Parameter, davon 104 Milliarden aktiv, und ein Kontextfenster von bis zu einer Million Tokens. DeepSeek V4 Pro liegt bei rund 1,6 Billionen Parametern. Bei solchen Modellen ist Self-Hosting technisch möglich, aber nur mit entsprechend großer Multi-GPU- oder Cluster-Infrastruktur.

Diese Modelle sind also nicht „nicht betreibbar“. Sie sind nur nicht mit der Hardwareklasse betreibbar, die für die meisten Unternehmen wirtschaftlich oder organisatorisch realistisch ist.

**Technisch nachgerechnet: Klasse D**

## Zwei Beobachtungen zum Feld

Die erste betrifft Meta. Das Unternehmen hat offene Gewichte mit Llama stark popularisiert. Bei Llama 4 zeigt sich inzwischen aber ein gemischtes Bild: Scout und Maverick wurden als offene Gewichte veröffentlicht, das ursprünglich angekündigte Behemoth dagegen nicht. Gleichzeitig kommen neue Meta-Modelle auch über Produkt- und API-Angebote auf den Markt, ohne dass daraus automatisch eine Veröffentlichung der Gewichte folgt. Wer heute auf offene Modelle setzt, sollte deshalb nicht nur das aktuelle Modell, sondern auch die Veröffentlichungsstrategie des Anbieters beobachten.

Die zweite betrifft Europa. Mistral ist derzeit einer der sichtbarsten europäischen Anbieter für große Open-Weight-Modelle. Die aktuelle Palette reicht von kleinen Edge-Modellen bis zu Mistral Large 3. Ein großer Teil der offenen Modellpalette steht unter Apache 2.0, Mistral Medium 3.5 beispielsweise aber unter einer modifizierten MIT-Lizenz.

Daneben gibt es Forschungs- und Open-Science-Projekte wie Apertus, Teuken-7B aus dem Projekt OpenGPT-X und EuroLLM. Sie verfolgen teilweise andere Ziele als maximale Benchmarkwerte: Transparenz bei Trainingsdaten, europäische Sprachen, nachvollziehbare Trainingsprozesse und Forschungsfreiheit stehen stärker im Vordergrund. Apertus geht hier besonders weit und veröffentlicht neben den Modellen auch Trainingsinfrastruktur und Daten-Rekonstruktionsskripte.

Und eine praktische Konsequenz: Bindet euch nicht an ein Modell, sondern an eine Schnittstelle. Wer seine Anwendungen gegen einen standardisierten Endpunkt baut und eine Vermittlungsschicht davorsetzt, kann das Modell austauschen, ohne die gesamte Anwendung neu zu bauen. In einem Feld, in dem sich Modelle, Quantisierungen und Hardwareanforderungen laufend verändern, ist diese Entkopplung die eigentliche Absicherung.

--- en ---

**The usual rankings sort models by benchmark scores. For anyone who wants to operate a model themselves, that is the wrong order. A more useful question is: what fits on which hardware?**

Anyone looking at open models today will mostly find leaderboards. They are not wrong, but they answer a question that rarely arises in practice. With the largest models, there is a world of difference between “open weights available” and “economically viable to self-host”. A more useful way to sort them is therefore: what fits on which hardware?

Not all of this is open source in the traditional sense. Many of the models available today are open-weight models: their weights are released, often together with inference code and documentation, but not necessarily with the complete training data and training code. The models can be downloaded, operated and, depending on the licence, adapted. Some projects go considerably further. For Nemotron 3 Nano, NVIDIA publishes not only the weights but also large parts of the training data and training recipes. For Apertus, Swiss AI likewise publishes the training infrastructure and scripts for reconstructing the training data. Licences range from Apache 2.0 and MIT variants to bespoke model licences.

**What do the numbers mean?**

Three quantities are therefore critical for hardware planning: the total number of parameters, the precision of the weights and the memory required by the KV cache. In an MoE model, the total parameter count roughly determines the amount of weight data that has to be stored, while the active parameters influence the compute required per token. Actual model speed also depends on memory bandwidth, the attention architecture, context length, batch size and the connection between the GPUs.

That is why Mistral Small 4 is not a small model despite its name. It activates 6.5 billion parameters but has 119 billion in total. With suitable 4-bit quantisation, it can fall into the 60 GB class; in FP8 it requires around 119 GB, and in BF16 approximately 238 GB. Its compute requirements are comparatively modest, but its memory requirements make it a large model.

## Class A: a single graphics card in a computer

Here we are looking at a single GPU with around 24 to 32 GB of VRAM — the kind of hardware also found in powerful workstations and gaming PCs.

Alibaba's Qwen3.8-27B is an obvious workhorse: 27 billion parameters, a dense architecture and released under Apache 2.0. It is an example of the fact that not every current model uses MoE.

Gemma 4 26B A4B sits alongside it. The model has around 25.2 billion parameters, of which 3.8 billion are active, and uses 128 experts. It is licensed under Apache 2.0. With suitable quantisation, the model can be run on a single GPU with 24 to 32 GB of VRAM.

Nemotron 3 Nano is the interesting outsider: 31.6 billion parameters, with around 3.6 billion active. In addition to the weights, NVIDIA publishes large parts of the training data and recipes. However, the model is not licensed under Apache 2.0 but under the NVIDIA Open Model License.

**The technical calculation: Class A**

## Class B: a single data-centre card

With 80 to 96 gigabytes of VRAM, the field opens up considerably. This class includes models that can be run on a single data-centre GPU with suitable quantisation.

gpt-oss-120b is a prominent example. The model has 117 billion total parameters and around 5.1 billion active parameters. The MXFP4 version published by OpenAI requires approximately 60 GB of VRAM, allowing it to run on a single H100 with 80 GB.

Mistral Small 4 also falls into this category when suitable quantisation is used. The official documentation lists 119 billion total parameters and 6.5 billion active parameters. An NVFP4 version comes in at around 60 GB and can run on a single suitable Blackwell GPU; the FP8 version, by contrast, requires approximately 119 GB.

With 120 billion total parameters and 12 billion active parameters, Nemotron 3 Super also falls within this range. The exact hardware requirements depend heavily on the precision used: NVIDIA provides NVFP4 and FP8 variants, among others. An NVFP4 version can be operated on a single 80 GB GPU in suitable setups, while the official deployment recipes for other configurations call for two or more GPUs.

Meta's Llama 4 Scout has 109 billion parameters, of which 17 billion are active, and a context window of up to 10 million tokens. It is not licensed under Apache or MIT, but under the Llama 4 Community License. The licence permits use, modification and distribution subject to certain conditions. Additional licensing terms apply to products or services with more than 700 million monthly active users. Anyone who uses Llama outputs to train or improve another AI model must also follow certain naming and labelling requirements if the resulting model is redistributed.

Apertus 1.5 70B from Switzerland, developed with the participation of ETH Zurich and EPFL, plays a different role. The model is licensed under Apache 2.0. Swiss AI also publishes training code, evaluation scripts and scripts for reconstructing the pre-training data. Apertus is therefore one of the projects that discloses not only the weights but also significant parts of the model's development process.

**The technical calculation: Class B**

## Class C: a server with multiple cards

From this point on, a proper multi-GPU setup is required. Depending on the model and quantisation, two cards may be sufficient; for the largest models, eight or more data-centre GPUs are common.

The range extends from Inkling-Small with 276 billion parameters to Llama 4 Maverick with 400 billion, Nemotron 3 Ultra with 550 billion, DeepSeek V4.1 Flash with 552 billion and Mistral Large 3 with 675 billion. GLM-5.3, with around 753 billion parameters, also belongs to this class.

Mistral Large 3 is documented as having 675 billion total parameters and around 41 billion active parameters. An official NVFP4 version is designed for a single server with multiple GPUs. Mistral lists deployment on one node with H100 or A100 GPUs for NVFP4, and on one node with H200 or B200 GPUs for FP8.

GLM-5.3 has around 753 billion parameters. The released checkpoint is approximately 756 GB and is provided in FP8. This is not a model for a single 80 GB card, but for multi-GPU infrastructure.

GLM-5.3 uses its own licence. It is not MIT, but it grants extensive rights to use, copy, modify, distribute and operate the model. Anyone planning to deploy it should therefore examine the specific licence rather than relying on the label “open”.

DeepSeek V4.1 Flash has around 552 billion total parameters. Its architecture cannot simply be equated with conventional MoE models: DeepSeek reports different activation figures for input and output. This is precisely why the actual compute requirements of such models should not be inferred from parameter count alone.

**The technical calculation: Class C**

## Class D: open, but beyond the reach of ordinary companies

At the top are models whose weights are available but whose operation requires infrastructure that goes far beyond a normal enterprise GPU.

Moonshot AI's Kimi K3 has 2.8 trillion parameters, of which 104 billion are active, and a context window of up to one million tokens. DeepSeek V4 Pro has around 1.6 trillion parameters. Self-hosting models of this size is technically possible, but only with correspondingly large multi-GPU or cluster infrastructure.

These models are therefore not “impossible to operate”. They simply cannot be run on the class of hardware that is economically or organisationally realistic for most companies.

**The technical calculation: Class D**

## Two observations about the field

The first concerns Meta. The company did much to popularise open weights with Llama. Llama 4 now presents a mixed picture: Scout and Maverick were released with open weights, while the originally announced Behemoth was not. At the same time, new Meta models also reach the market through products and APIs without this automatically resulting in a release of their weights. Anyone adopting open models today should therefore monitor not only the current model but also the provider's release strategy.

The second concerns Europe. Mistral is currently one of Europe's most visible providers of large open-weight models. Its current portfolio ranges from small edge models to Mistral Large 3. Much of the open model portfolio is licensed under Apache 2.0, although Mistral Medium 3.5, for example, uses a modified MIT licence.

There are also research and open-science projects such as Apertus, Teuken-7B from the OpenGPT-X project and EuroLLM. Some of them pursue objectives other than maximum benchmark scores: transparency about training data, support for European languages, reproducible training processes and freedom of research are given greater priority. Apertus goes particularly far, publishing not only the models but also the training infrastructure and scripts for reconstructing the data.

And one practical consequence: do not tie yourself to a model; tie yourself to an interface. Anyone who builds applications against a standardised endpoint and places an intermediary layer in front of it can swap the model without rebuilding the entire application. In a field where models, quantisation methods and hardware requirements are constantly changing, this decoupling is the real safeguard.

Kategorie / Category: [Blogposts](https://www.control-f.io/blog/categories/blogposts)
