# Übergabe: Madina Arabisch App

Stand: 10. November 2026. Diese Datei ist für eine neue Claude-Sitzung, die an der App weiterarbeitet.

## Was existiert

- **Live-App (Claude-Artefakt):** https://claude.ai/artifact/FUZxoyZJUbUAkTsznw2WXr
  Immer unter dieser URL aktualisieren (`Artifact` mit `url`), nie ein neues Artefakt anlegen. Vor dem ersten Publish die Datei bzw. das Artefakt lesen.
- **Quelltext:** `arabisch-app/madina-arabisch.html` in diesem Repository, Branch `claude/arabic-learning-app-fxgl8e`. Nach jeder Änderung: publishen, committen, pushen.
- Das Artefakt deklariert die Capabilities `sample` (Claude-Aufrufe aus der Seite), `db` und `user` (Fortschritt im Claude-Konto unter `data/users/<id>/progress`). Beim Publish `capabilities` weglassen, dann bleiben sie erhalten.

## Nutzer

- Deutschsprachiger Anfänger, lernt mit den Madina-Büchern (Durūs al-Lugha al-ʿArabiyya, Islamische Universität Medina), Buch 1 bis 3.
- Nutzt die App am Handy (Android) und am Mac. Will Tokens sparen: Sparmodus ist voreingestellt.
- Antworten an den Nutzer auf Deutsch, Du-Form, kurz und ehrlich.

## Aufbau der App (eine HTML-Datei, kein Framework)

Fünf Bereiche mit Tab-Leiste: Bücher (Themenliste mit Grammatik, Beispielen, Wörtern), Tutor, Rollenspiel, Karteikarten, Übersetzer. Einstellungen als Sheet (Buch, Anrede m/f, Vorlesen, Sparmodus usw.).

Datenstrukturen im Script (alle Arabisch-Texte mit vollständigem Taschkīl):

- `TOPICS`: Array der Lernthemen. Felder: `id` (z. B. `b1-hadha`), `book` (1–3), `ar`, `de`, `gram` (kurze Erklärung, Deutsch), `ex` (Beispielsätze `[ar, de]`), `words` (`[ar, umschrift, de, beispiel?, beispiel_de?]`). Aus `words` entstehen automatisch die Karteikarten.
- `EX`: Übungen für den Sparmodus je Thema: `{q, qF?, qde, ok:[ar, de, arF?], bad:[[ar, erklärung], ...]}`. Der Tutor stellt `q`, der Nutzer wählt aus `ok` und `bad`; falsche Wahl zeigt die Korrektur und legt den richtigen Satz in den Fehler-Stapel.
- `SCENES`, `STEPS`, `ENDS`: Rollenspiele (Café, Restaurant, Hotel, Supermarkt, Arzt, Universität) mit festen Dialogen für den Sparmodus.
- Lernkartei: Leitner-System in `S.srs`, Fehler-Stapel in `S.mistakes`, eigene Wörter in `S.custom`. Gespeichert lokal und im Claude-Konto.
- Modus `S.settings.mode`: `offline` (Sparmodus, kostenlos) oder `claude` (freier Tutor, Rollenspiel mit Claude, Übersetzer mit Claude über `sample.json`).

Derzeit 19 Themen (10 für Buch 1, je 4–5 für Buch 2 und 3), 263 Wörter, 57 Übungen. Die Inhalte sind aus dem Gedächtnis geschrieben, nicht aus den Büchern, und ohne Lektionsnummern.

## Nächste Aufgabe

Die App Lektion für Lektion nach den echten Büchern ausrichten. Der Nutzer lädt dafür **Buch 1 als PDF und den englischen Key zu Buch 1** hoch (später Buch 2 und 3 in eigenen Sitzungen).

Vorgehen:
1. Prüfen, ob die PDFs Text enthalten (`pdftotext`) oder Scans sind. Dem Nutzer vor dem Lesen eine Token-Schätzung nennen. Bei Scans nur die Seiten mit Grammatik, Wortschatz und Mustersätzen lesen, Übungsseiten überspringen. PDFs mit `Read` und `pages` (max. 20 pro Aufruf) lesen.
2. `TOPICS` für Buch 1 durch die echten Lektionen ersetzen: eine Lektion = ein Thema, `id` z. B. `b1-l01`, `de` mit Lektionsnummer („Lektion 1 · Das ist …"), vollständiger Wortschatz der Lektion, Grammatik aus dem Key in einfachem Deutsch, Beispielsätze aus dem Buch.
3. `EX` für jede Lektion mit etwa 5 Übungen nach dem Muster der Buchübungen; typische Anfängerfehler als `bad`.
4. Bestehende Themen-IDs für Buch 1 (`b1-hadha` bis `b1-adad`) dürfen wegfallen; der Fehler-Stapel des Nutzers verweist auf Karten-IDs `topicId.umschrift`, verlorene Verweise werden ignoriert, das ist in Ordnung.
5. Nach dem Umbau: Syntax prüfen (`node --check` auf dem Script-Teil), einmal mit Playwright in 390 px Breite ansehen, publishen, committen, pushen.

Zum Testen gab es Skripte im Scratchpad (Playwright-Screenshots); sie müssen neu geschrieben werden, das Scratchpad ist sitzungsgebunden.
