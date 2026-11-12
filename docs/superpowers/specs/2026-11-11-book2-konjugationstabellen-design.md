# Design: Zweiter Übungstyp für Buch 2 — Konjugationstabellen

Datum: 2026-11-11
Status: Entwurf, wartet auf Ridouanes Freigabe

## Kontext und Warum

Die Madina-Arabisch-App (`arabisch-app/madina-arabisch.html`, eine einzige HTML/JS-Datei ohne Framework) hat bisher einen einzigen Übungstyp im Sparmodus ("Typ 1"): eine Frage (`EX[lessonId]`) mit einer richtigen Antwort und zwei falschen Antworten samt Erklärung, dargestellt als Multiple-Choice-Chat-Bubble im Tutor-Tab (`makeQuiz()` / `answerQuiz()`). Dieses Format passt gut zu Buch 1, das Bild-Rate- und Dialog-Übungen hat.

Buch 2 (gerade vollständig gelesen, 31 Lektionen, Übersicht in `[[Madina Buch 2 - Lektionsübersicht]]` im Vault) hat **keine Bilder** und besteht zu großen Teilen aus Konjugationstabellen (Verb × Person/Genus/Numerus) mit oft 10–20 Übungsseiten pro Lektion statt einzelner Frage-Antwort-Paare. Typ 1 bildet solche Tabellen nicht ab. Ridouane möchte für Buch 2 einen zweiten Übungstyp, der dem Original so nah wie möglich kommt.

**Entscheidung (Ridouane, 2026-11-11):** Typ 1 bleibt unverändert für Vokabel- und reine Grammatikfragen bestehen. Der neue Typ 2 wird ausschließlich für Konjugationstabellen genutzt — überall dort in Buch 2, wo das Buch selbst eine Tabelle zeigt.

## Ziele

- Ein Übungstyp, der eine echte Konjugationstabelle (Person × Genus × Numerus) zum selbstständigen Ausfüllen zeigt, statt einer einzelnen Multiple-Choice-Frage.
- Die Reihenfolge der Pronomen folgt der **klassischen arabischen Lehrbuch-Reihenfolge**, nicht der im Deutschen üblichen ("ich, du, er..."):
  1. 3. Person maskulin (الغائب، مذكر)
  2. 3. Person feminin (الغائب، مؤنث)
  3. 2. Person / direkte Anrede, maskulin dann feminin (المخاطب)
  4. 1. Person (المتكلم)
  Diese Reihenfolge gilt **identisch** für Vergangenheit (ماضي), Präsens (مضارع) und Imperativ (أمر) — keine abweichende Reihenfolge je Zeitform.
- Die Tabelle deckt Singular, Dual und Plural ab, sobald die jeweilige Lektion das einführt (Dual kommt in Buch 2 strukturell erst in Lektion 30 hinzu, siehe Lektionsübersicht; frühere Tabellen haben nur Singular/Plural).
- **Zwei Phasen** pro Tabellen-Übung:
  1. **Schrittweises Ausfüllen**: Die Zellen werden in genau der oben genannten Reihenfolge nacheinander abgefragt (zuerst alle maskulinen Formen, dann alle femininen, dann die Anrede, zuletzt die 1. Person). Jede Zelle einzeln per Texteingabe, sofortiges Feedback pro Zelle. Bei falscher Eingabe gibt es **einen zweiten Versuch**; ist auch der zweite falsch, wird die korrekte Schreibweise gezeigt und es geht zur nächsten Zelle weiter (Ridouane, 2026-11-11).
  2. **Wiederholung in zufälliger Reihenfolge**: Nachdem die Tabelle einmal komplett ausgefüllt ist, werden dieselben Zellen noch einmal abgefragt, aber in gemischter/zufälliger Reihenfolge — damit der Nutzer die Form wirklich kennt und nicht nur ihre Position in der Tabelle.
- Eingabe-Prüfung **ignoriert Diakritika (Taschkīl)**: Der Nutzer tippt die Grundschreibung, z. B. `ذهب` statt `ذَهَبَ`. Die Buchstaben müssen stimmen, Vokalzeichen werden beim Vergleich entfernt/ignoriert.
- **Eigene Eingabehilfe (Ridouane, 2026-11-11):** Die App bekommt für Typ 2 eine eigene arabische Eingabehilfe (Buchstaben-Tasten innerhalb der App), statt sich allein auf die arabische Tastatur des Geräts zu verlassen — Begründung: bei Typ 2 wird ständig, viele Male pro Tabelle, ein einzelnes arabisches Wort von Grund auf eingetippt, das ist etwas anderes als das bisherige gelegentliche Eintippen eines ganzen Satzes. Genaues Layout/Umfang der Eingabehilfe bleibt dem Builder überlassen (Standard-arabische Tastenanordnung ist ein sinnvoller Ausgangspunkt).

## Nicht-Ziele

- Typ 1 wird nicht ersetzt oder umgebaut — er bleibt unverändert für alle Vokabel- und reinen Grammatikfragen in Buch 2, und für Buch 1/3.
- Keine Unterstützung für die drei Mudari'-Modi (مرفوع / منصوب / مجزوم) als eigene Tabellenspalten in dieser ersten Version. Diese drei unterscheiden sich bei gesunden Verben ausschließlich durch Diakritika (z. B. يَذْهَبُ / يَذْهَبَ / يَذْهَبْ sind ohne Taschkīl alle `يذهب`) und wären bei einer Prüfung ohne Taschkīl nicht sauber unterscheidbar. Buch 2 behandelt das in eigenen Lektionen (18, 21) — falls das später gebraucht wird, braucht es eine eigene Lösung (z. B. doch mit Taschkīl prüfen) und ist hier bewusst ausgeklammert.
- Keine Änderung am Claude-Modus (Online-Tutor) — der zweite Übungstyp ist nur für den Sparmodus (offline, vorbereitete Daten), genau wie Typ 1.

## Anti-Ziele (das wäre ein Fehlschlag, auch wenn es technisch läuft)

- Eine Tabelle, die dem Nutzer alle Formen auf einmal zum Auswendiglernen zeigt, statt sie Schritt für Schritt abzufragen — das wäre näher an einem Spickzettel als an einer Übung.
- Eine Zufalls-Phase, die de facto nie zufällig genug ist (z. B. immer von vorne nach hinten durchgeht) und damit ihren eigentlichen Zweck — echtes Wissen statt Positions-Gedächtnis zu prüfen — verfehlt.

## Bestehende Architektur (Kontext für den Builder)

Datei: `arabisch-app/madina-arabisch.html`. Relevante Teile:

- `TOPICS`: Array, ein Eintrag pro Lektion (`id`, `book`, `ar`, `de`, `gram`, `ex`, `words`). Buch 2 hat aktuell nur 6 aus dem Gedächtnis geschriebene Platzhalter-Themen (`b2-mudari`, `b2-zaman`, `b2-salah`, `b2-alwan`, `b2-amr`, `b2-kana`) — die werden, wie bei Buch 1, durch die 31 echten Lektionen ersetzt (eigene, zeitlich vorgelagerte Aufgabe, nicht Teil dieses Designs).
- `EX`: Objekt, Lektions-ID → Array von Übungsfragen (`{q, qde, ok:[ar,de], bad:[[ar,erklärung],...]}`), Typ-1-Format. Gerendert über `makeQuiz()` / `answerQuiz()` als Multiple-Choice-Chat-Bubble im Tutor-Tab (`CHAT.tutor.msgs`, Rolle `role:'quiz'`).
- `STEPS` / `SCENES` / `ENDS`: dasselbe Grundprinzip für die Rollenspiel-Szenen, von diesem Design nicht betroffen.
- Fünf Tabs: Bücher (liest `TOPICS.gram` / `.ex` / `.words`, reine Leseansicht), Tutor (Chat mit `EX`-Quiz), Rollenspiel, Karteikarten (`words` → Leitner-System in `S.srs`), Übersetzer.

Für Typ 2 gibt es noch **keine** Datenstruktur und **keine** Rendering-Logik — beides ist neu zu bauen.

## Einbindung in die bestehende App (entschieden)

Die App ist durchgängig als Chat-Oberfläche gebaut; auch die bestehenden Quiz-Fragen sind Chat-Bubbles (`role:'quiz'`) im Tutor-Tab. Typ 2 wird eine neue Chat-Rolle (`role:'table'`) im selben Tutor-Tab. Das hält die App bei einer einzigen Bedienlogik, statt einen sechsten Tab oder Modus einzuführen.

**Darstellung als persistente, sich füllende Tabelle, nicht als Strom einzelner Bubbles (mein Entscheid, folgt direkt aus Ziel + Anti-Ziel oben):** Die Tabelle wird als eine Bubble gerendert, die über die ganze Phase 1 hinweg sichtbar bleibt und sich Zelle für Zelle füllt — bereits beantwortete Zellen zeigen die korrekte Form und bleiben stehen, die aktuelle Zelle hat das Eingabefeld, restliche Zellen sind leer/ausgegraut. Ein Strom einzelner, verschwindender Fragen-Bubbles (wie bei Typ 1) würde sich nicht wie eine Tabelle anfühlen und den ganzen Sinn des neuen Übungstyps unterlaufen.

**Session-Verhalten (mein Entscheid, folgt bestehenden App-Konventionen):** Tabellen-Sessions laufen **nicht** im zufälligen Cross-Lektion-Pool von `tutorQuiz()` mit — eine mehrstufige Session lässt sich nicht einfach zwischen einzelnen Zufallsfragen anderer Lektionen einschieben. Eine Tabelle wird gezielt gestartet, wenn der Nutzer das entsprechende Buch-2-Thema ausgewählt hat. Der Fortschritt (welche Phase, welche Zelle, bei Phase 2 die bereits gewürfelte Zufallsreihenfolge) wird lokal gespeichert wie der übrige App-Zustand (`CHAT.tutor.msgs`, `S.mistakes`, `S.srs`) — der Nutzer macht beim nächsten Öffnen exakt da weiter, wo er aufgehört hat, nichts geht verloren.

## Entschieden: Lektionen mit mehreren Verb-Mustern (v. a. Lektion 27 und 28)

Dort zeigt das Buch mehrere vollständige Paradigmen (z. B. Lektion 27: قال/يقول, باع/يبيع, نام/ينام als drei verschiedene Hohlverb-Muster) — aber jeweils nur **ein** Verb vollständig ausgearbeitet, für die anderen gibt das Buch nur die Anweisung "mach das Gleiche für diese Verben" (Ex. 4: "اسنِدِ (قام) و(زار) و(كان) إلى الضمائر كما في التمرين السابق"), ohne eigene abgedruckte Tabelle. **Entscheidung (Ridouane, 2026-11-11): daraus wird eine Kette von mehreren eigenständigen Tabellen-Sessions, eine pro Verb, nacheinander** — nicht eine einzige Tabelle mit mehreren Verb-Spalten. Das entspricht dem Buch selbst und vermeidet einen Sonderfall nur für diese paar Lektionen.

## Status

Alle offenen Entscheidungsfragen sind mit Ridouane geklärt (2026-11-11). Bereit für die Planungsphase.

## Was dem Builder offen bleibt

- Exakte Datenstruktur für die neuen Tabellen-Daten (Name, Feldnamen) — orientiert sich am Stil von `EX` (ein Objekt pro Lektions-ID).
- Visuelle Gestaltung der Tabelle (CSS), innerhalb des bestehenden Chat-Bubble-Stils.
- Reihenfolge Singular/Dual/Plural *innerhalb* einer Person/Genus-Zeile — Vorschlag: Singular vor Dual vor Plural, wie im Buch selbst dargestellt (z. B. Lektion 13: Spalten "Mufrad" dann "Jam'" nebeneinander). Unkritisch, da Ridouane nur die Reihenfolge der Personen/Genus-*Gruppen* festgelegt hat, nicht die der Numeri innerhalb einer Gruppe.
- Wie "Dual nur wo im Buch vorhanden" technisch abgebildet wird — z. B. keine Dual-Zelle für die 1. Person (im Arabischen gibt es dort keinen eigenen Dual, die Pluralform wird mitbenutzt, siehe Buch Lektion 30), und eine gemeinsame Dual-Zelle für die Anrede, da die Dual-Form dort für maskulin/feminin identisch ist (ebenfalls Lektion 30).
- Exakter Vergleichsalgorithmus für "ohne Diakritika" (z. B. Unicode-Bereich der arabischen Vokalzeichen beim Vergleich aus beiden Seiten entfernen, dann exakter String-Vergleich).
- Welche der 31 echten Buch-2-Lektionen Typ 2 bekommen (grobe Sichtung ergab mindestens die Lektionen 8, 11–16, 18, 20, 26–30) — endgültige Zuordnung macht der Builder beim Einpflegen der echten Lektionsinhalte in `TOPICS`/`EX`.

## Konkretes Beispiel (zur Illustration, nicht normativ)

Lektion mit dem Verb ذَهَبَ (gehen) in der Vergangenheit, nur Singular + Plural (kein Dual in dieser frühen Lektion). Schritt-Reihenfolge der Phase 1:

هو ذهب → هم ذهبوا → هي ذهبت → هن ذهبن → أنت ذهبت → أنتم ذهبتم → أنتِ ذهبتِ → أنتن ذهبتن → أنا ذهبت → نحن ذهبنا

(Hier als "erst männlicher Singular+Plural komplett, dann weiblicher Singular+Plural komplett" angenommen — passend zur oben offen gelassenen Numerus-Reihenfolge innerhalb einer Gruppe.)
