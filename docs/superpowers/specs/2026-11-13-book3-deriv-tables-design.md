# Design: Dritter Übungstyp — Ableitungstabellen für Buch 3 (Verbformen)

Datum: 2026-11-13
Status: Phase 1 von 4 (Datenstruktur + Step-Builder + ein Proof-Lektion). Rendering, Bewertung/Verkettung
und Themen-Auswahl folgen in späteren, eigenen Aufgaben.

## Warum Typ 2 (TABLES/buildTableSteps/makeTable) nicht passt

Typ 2 bildet eine Personen-Konjugationstabelle ab: eine ZEILE ist eine Person/Genus/Numerus-Kombination
(`{group, gender, num, pronoun, form}`), die feste Buchreihenfolge kommt aus `buildTableSteps()` selbst
(3. Pers. → 2. Pers. → 1. Pers.), unabhängig von der Eingabedaten-Reihenfolge.

Buch 3 druckt ab Lektion 16 (Verbformen II–X plus Quadriliteral) keine solchen Tabellen mehr. Stattdessen:
eine ZEILE ist ein WURZELVERB derselben Verbform, eine SPALTE ist eine grammatische Stammform (immer
الماضي und المضارع, je nach Lektion zusätzlich الأمر und/oder المصدر und/oder اسم الفاعل/اسم المفعول —
3 bis 5 Spalten, Anzahl und Reihenfolge wechseln von Lektion zu Lektion). Nur die erste Wurzel (manchmal
die erste je Unterkategorie) ist vollständig ausgearbeitet vorgegeben, der Rest ist zum Selbst-Ableiten
leer — und manchmal ist eine einzelne schwere Zelle einer unregelmäßigen Wurzel trotzdem als Hinweis
vorgegeben, auch wenn der Rest ihrer Zeile leer bleibt.

Das ist eine andere Achsenzuordnung (Zeile=Wurzel statt Zeile=Person) und eine andere
Given/Blank-Granularität (pro Zelle, nicht block-weise pro Person). Das in `{group,gender,num,pronoun,
form}` zu zwingen wäre ein Hack — z. B. müsste "Spalte" künstlich auf "group" abgebildet werden, obwohl
`buildTableSteps()` group/gender/num fest mit der Personen-Reihenfolge verdrahtet. Deshalb eine zweite,
parallele Engine: `DERIV_TABLES` / `buildDerivTableSteps()` / `makeDerivTable()`, die dieselben bewährten
Interaktionsmechaniken wiederverwendet (zwei Phasen, zwei Versuche pro Zelle, Chat-Bubble-Persistenz,
Verkettung mehrerer Tabellen pro Lektion), aber eine eigene Datenstruktur und einen eigenen Step-Builder
hat, statt TABLES/buildTableSteps/makeTable zu überladen.

## Neue Datenstruktur: DERIV_TABLES

```
DERIV_TABLES[topicId] = Array<DerivTabelle>

DerivTabelle = {
  de: string,              // deutsche Überschrift, über der Tabelle angezeigt
  columns: string[],       // 3-5 Spaltenbeschriftungen, GEDRUCKTE Reihenfolge aus dem Buch
  rows: [
    { root: string, values: (string|null)[], given: boolean[] },
    ...
  ]
}
```

`values[i]`/`given[i]` sind parallele Arrays, ein Eintrag pro Spalte (gleiche Länge wie `columns`).
`given[i] === true` → `values[i]` ist die gedruckte Antwort, wird dem Nutzer immer als Referenz gezeigt,
ist aber kein Abfrage-Schritt. `given[i] === false` → `values[i]` ist `null` in den Rohdaten, der Nutzer
muss die Form selbst eingeben; die richtige Form steckt stattdessen im vom Step-Builder erzeugten Step
(`form`), nicht in `values[i]` (das bleibt `null`, bis in einer späteren Aufgabe die Antwort eingetragen
wird — siehe Scoring-Aufgabe).

Mehrere `DerivTabelle`-Einträge je `topicId` werden, genau wie Typ 2 bei Lektion 27/28, nacheinander
verkettet (eine Lektion kann mehrere Tabellen zeigen: Hauptmodell, dann Masdar-Drill, dann اسم الفاعل usw.).

## given pro Zelle, nicht pro Zeile

Bewusste Entscheidung, weil das Buch es so macht: in Entry B (مصدر باب فعّل) sind z. B. هَنَّأَ، سَمَّى، حَيَّى
irreguläre Wurzeln, deren Masdar als Hinweis vorgegeben ist, während رَبَّى — ebenfalls irregulär — absichtlich
NICHT vorgegeben wird (der Student soll sie selbst ableiten). Eine Row-Level-Flagge (ganze Zeile entweder
komplett gegeben oder komplett leer) könnte das nicht abbilden. Deshalb ist `given` ein Array parallel zu
`values`, nicht ein einzelnes Bool auf der Zeile.

## Step-Builder: `buildDerivTableSteps(entry)`

Analog zu `buildTableSteps()`, aber mit einer wichtigen Abweichung: **keine feste Universal-Reihenfolge.**
Bei Typ 2 bestimmt eine hartkodierte Order-Tabelle (3.m→3.f→2.m→2.f→1.) die Abfragereihenfolge, unabhängig
von der Eingabe-Reihenfolge der Zellen. Bei Typ 3 GIBT es keine universelle Reihenfolge über Wurzeln
hinweg — die gedruckte Reihenfolge im Buch (Zeile für Zeile von oben, Spalte für Spalte von links nach
rechts innerhalb jeder Zeile, exakt wie in `entry.columns`) IST die Reihenfolge. Die Funktion iteriert also
einfach `entry.rows` in Array-Reihenfolge und darin `entry.columns` in Array-Reihenfolge, statt wie
`buildTableSteps()` gegen eine feste Bucket-Liste zu matchen.

Jede Zelle mit `given[colIdx] === false` wird zu einem Step:
`{rowIdx, colIdx, root: row.root, column: entry.columns[colIdx], form: row.values[colIdx]}`.
Zellen mit `given[colIdx] === true` werden komplett ausgelassen (keine Lücken, keine Platzhalter-Steps) —
sie sind reine, immer sichtbare Referenzanzeige, keine Abfrage.

## `makeDerivTable(topicId, tableIndex)` und der Sonderfall "null Lückenzellen" (Entry A)

Analog zu `makeTable()`: Lookup in `DERIV_TABLES[topicId][tableIndex]`, baut die Steps, gibt ein
Message-Objekt mit `role:'derivTable'` und denselben Lifecycle-Feldern wie Typ 2 zurück
(`phase:1, order, pos:0, attempt:0, answers:{}, done`), zusätzlich `columns`/`rows`/`steps`/`de`, damit der
Renderer (nächste Aufgabe) nichts aus `DERIV_TABLES` nachschlagen muss.

**Zwei verschiedene Fälle von "keine Steps", bewusst unterschiedlich behandelt:**

1. **Fehlende/defekte Lektionsdaten** (kein Eintrag, `rows` fehlt oder ist leer) → `makeDerivTable` gibt
   `null` zurück, genau wie `makeTable`s `if (!entry || !Array.isArray(entry.cells) || !entry.cells.length)
   return null;`. Das ist der Defensiv-Fall für echten Dateneingabe-Fehler — Lektion wird übersprungen statt
   eine tote, unbeantwortbare Bubble zu erzeugen.
2. **Eintrag ist vollständig und gültig, aber absichtlich 100 % `given`** (Buch-3-Lektion 16, Entry A —
   das fertig ausgearbeitete فَعَّلَ-Hauptmodell, das der Student nur LESEN soll, bevor die folgenden Drill-
   Tabellen ihn selbst ableiten lassen) → **kein `null`.** `buildDerivTableSteps()` liefert hier zurecht ein
   leeres Array (keine Zelle hat `given:false`), aber die Tabelle selbst ist kein Fehler — sie ist der
   erste von sechs verketteten Einträgen dieser Lektion und muss dem Nutzer gezeigt werden, sonst
   verschwindet wortlos das einzige vollständig vorgerechnete Referenzbeispiel der Lektion.

   **Entscheidung:** `makeDerivTable` setzt in diesem Fall ein zusätzliches Feld `studyOnly:true` und
   `done:true` direkt bei der Erzeugung (nichts abzufragen, also von Anfang an "fertig" im Sinne von
   Scoring), lässt aber `columns`/`rows`/`de` wie gewohnt gefüllt — der Renderer einer späteren Aufgabe
   kann darüber entscheiden, die Karte als reine Lesekarte mit einem Weiter-Button darzustellen, statt sie
   durch den Zwei-Versuche-Scoring-Flow zu schicken. Diese Verkettungs-/Darstellungslogik selbst ist nicht
   Teil dieser Aufgabe (Phase 1); `studyOnly` ist der Marker, den die spätere Rendering-Aufgabe braucht, um
   den Unterschied zu einer normalen Drill-Tabelle überhaupt erkennen zu können.

   **Verworfene Alternative:** `null` zurückgeben und die Lektion wie Fall 1 überspringen. Verworfen, weil
   das denselben Code-Pfad für "Dateneingabe-Fehler" und "absichtlich reine Referenztabelle" benutzen würde
   — beide sehen für `makeDerivTable` identisch aus (`steps.length === 0`), aber nur der erste Fall soll
   die Lektion stillschweigend überspringen. Mit `studyOnly` als explizitem State bleibt der echte
   Fehlerfall (Fall 1) weiterhin `null` und sichtbar von einem rows-freien Dateneintrag unterscheidbar; ein
   künftiger Tippfehler, der eine eigentlich gedachte Drill-Tabelle versehentlich komplett `given:true`
   setzt, fällt dadurch als auffällig unbeantwortbare "Studienkarte" auf, statt lautlos aus der Kette zu
   verschwinden — der sicherere Fehlschlag-Modus.

## Proof-Lektion: `b3-l16` (باب فَعَّلَ / Form II)

Sechs verkettete `DerivTabelle`-Einträge (A–F): Hauptmodell (0 Lückenzellen, `studyOnly`), Masdar-Drill (9
Zeilen, 6 Lückenzellen), اسم الفاعل (6 Zeilen × 1 Lückenspalte), اسم المفعول (Zeile 1 Modell, Zeilen 2–8 nur
الماضي vorgegeben), زwei مصدر-Drills (فَعْل und فِعَال, je nur مصدر-Spalte leer). Transkription 1:1 aus der
vom Auftraggeber bereits mit dem Originalbuch abgeglichenen Vorlage, inkl. aller Diakritika.

## Nicht Teil dieser Aufgabe

Rendering der Tabelle als Chat-Bubble, Zwei-Versuche-Scoring (`submitDerivTableCell` o. ä.), Phase-1→2-
Übergang (Shuffle-Wiederholung), Verkettung mehrerer Einträge im laufenden Chat, Themen-Auswahl-Wiring. Alle
vier folgen in späteren Aufgaben, analog zur Typ-2-Reihenfolge (siehe
`docs/superpowers/plans/2026-11-11-book2-konjugationstabellen.md`).
