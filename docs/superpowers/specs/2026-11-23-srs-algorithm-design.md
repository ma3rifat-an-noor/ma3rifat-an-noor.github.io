# Adaptive Spaced-Repetition-Verbesserung für die Karteikarten-Lernlogik

## Intent / Why

Die Karteikarten-Lernlogik ist aktuell ein klassisches Leitner-System: 5 feste Stufen,
feste Wiederholungsabstände (0/1/3/7/21 Tage je Stufe), binäre Bewertung (gewusst /
nicht gewusst), harte Obergrenze bei 21 Tagen. Das behandelt jede Karte gleich,
unabhängig davon, wie leicht oder schwer sie Ridouane tatsächlich fällt, und
verschwendet auf Dauer Lernzeit bei sicher beherrschten Wörtern, die trotzdem alle
drei Wochen wiederkommen.

Ziel: pro Karte personalisierte Wiederholungsabstände, die mit zunehmender
Sicherheit deutlich über 21 Tage hinauswachsen können — für bessere Lernergebnisse
bei gleichem oder geringerem Zeitaufwand.

## Goals

- Dritte Bewertungsstufe beim Aufdecken einer Karte: nicht gewusst / schwer gewusst
  / leicht gewusst (statt nur gewusst/nicht gewusst).
- Pro Karte ein individueller Ease-Faktor, der sich mit jeder Bewertung anpasst.
- Keine feste Obergrenze mehr bei 21 Tagen — wachsende Intervalle für sicher
  beherrschte Wörter, mit einem weichen Cap (siehe unten), damit die Zahlen nicht
  unbegrenzt weiterlaufen.
- Fehler-Stapel-Konzept und sofortiges Wiedervorlegen falscher Karten innerhalb
  derselben Sitzung bleiben unverändert (bewährtes Verhalten).

## Non-Goals

- Keine Migration des bisherigen Lernfortschritts (`S.srs`) — Ridouane hat
  bestätigt, dass der aktuelle Stand reine Testdaten sind und verworfen werden kann.
- Keine Änderung an der Sitzungs-Zusammenstellung (`startSession`): weiterhin
  Fehler-Stapel + fällige Karten + bis zu 8 neue Karten, Deckel bei 20 Karten pro
  Sitzung.
- Keine Mehrbenutzer-/Synchronisations-Logik für den Algorithmus.

## Anti-Goals

- Kein voller SM-2-Nachbau mit allen Feinheiten (Leech-Erkennung, konfigurierbare
  Parameter, mehrere Kartentypen) — das wäre für eine Einzelnutzer-App mit
  lokalem Speicher unverhältnismäßig komplex.

## Approaches

1. **Nur die 21-Tage-Obergrenze anheben.** Geringster Aufwand, behebt aber weder
   die binäre Bewertung noch die fehlende Personalisierung pro Karte — das
   eigentliche Problem bleibt. Verworfen.
2. **Vollständiges SM-2 (Anki-Original).** Alle Feinheiten (Lapses, Leech-Status,
   konfigurierbare Ease-Grenzen) — zu komplex für den Umfang und Nutzungskontext
   dieser App. Verworfen.
3. **SM-2-„lite" (gewählt).** 3-Stufen-Bewertung, ein einfacher Ease-Faktor pro
   Karte, nächstes Intervall = vorheriges Intervall × Ease (je nach Bewertung
   angepasst), weicher Cap. Bewährtes Prinzip, überschaubare Umsetzung auf der
   bestehenden Datenstruktur (`S.srs[id] = {b, d, w, r, s, ...}`).

Ridouane hat Ansatz 3 in der Besprechung ausdrücklich bestätigt.

## Decided

- Ansatz 3 (SM-2-lite) wird umgesetzt.
- Keine Migration alter Daten nötig.
- Die bestehende `S.srs`-Datenstruktur wird um Felder für Ease-Faktor und
  aktuelles Intervall erweitert (genaue Feldnamen: Sache des Builders).
- Der dritte Bewertungsknopf ("schwer gewusst") ist eine sichtbare UI-Änderung
  auf dem Karteikarten-Bildschirm, die Ridouane täglich sehen wird.

## What's left to the builder

- Genaue Ease-Faktor-Formel und Start-/Grenzwerte (z. B. Start-Ease 2.5, Minimum,
  wie stark „schwer gewusst" vs. „leicht gewusst" den Ease-Faktor bewegen).
- Exakter weicher Cap-Wert für die maximale Intervall-Länge.
- Verhalten bei „nicht gewusst": Rückfall-Logik (z. B. Ease-Reduktion plus
  Intervall-Reset, analog zum heutigen Rückfall auf Stufe 1).
- UI-Anpassung: dritter Knopf auf der Karteikarten-Rückseite, deutsche und
  englische Beschriftung.
- Tests (Playwright) für die neue Bewertungslogik, analog zu den bestehenden
  `tests/test_*` Dateien.
