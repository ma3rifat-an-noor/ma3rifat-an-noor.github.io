# Eigener Claude-Schlüssel (BYOK) — Kurz-Design

**Warum:** Ridouane will, dass andere Nutzer den Live-Tutor/Rollenspiel/Übersetzer nutzen können, ohne dass er für jeden bezahlt. Statt des aufwendigeren Supabase-Server-Wegs (siehe `[[Madina App - Claude-Integration (Design)]]` im Vault, jetzt `on-hold` als Notfall-Option) zuerst der einfachere Test: wer keinen eigenen Zugang hat, bleibt beim bestehenden Gratis-Sparmodus; wer einen eigenen Anthropic-Schlüssel hat, trägt ihn ein und spricht direkt aus dem eigenen Browser mit Claude, auf eigene Kosten. Ridouane (18.11.2026): „Wir lassen den Supabase-Server-Plan nicht komplett fallen, wir halten den als Notfall-Option offen und prüfen den Bau des bestehenden Gratis-Modus plus eine Einstellung für den eigenen KI-Schlüssel. Wenn das gut funktioniert, dann lassen wir den Supabase-Server-Plan komplett fallen."

**Ziele:**
- Ein neues Einstellungsfeld (eigener Claude-Schlüssel), nur lokal im Browser gespeichert, nie an Ridouane übertragen.
- Leeres Feld = heutiges Verhalten unverändert (Claude-Modus zeigt weiterhin die bestehende „braucht Claude"-Fehlermeldung).
- Ausgefülltes Feld = Tutor, Rollenspiel-Feedback und Übersetzer sprechen direkt mit `api.anthropic.com`, ohne jeden Server dazwischen.
- Der bestehende Schalter „Genauere Korrektur" bleibt unverändert und steuert weiterhin Haiku (schnell) vs. Sonnet (genauer) — jetzt eben mit dem eigenen statt einem fremden Schlüssel.

**Nicht-Ziele:**
- Kein Gemini/Groq/ChatGPT/Ollama in dieser Runde — nur Claude. Architektur so halten, dass ein weiterer Anbieter später eine kleine Ergänzung ist, aber nicht vorab bauen (YAGNI).
- Keine Änderung am bestehenden Sparmodus oder an den zwölf offline funktionierenden Rollenspiel-Szenen.
- Kein Backend, keine Accounts, kein Kontingent, keine Bezahlung — das ist genau der Punkt dieses einfacheren Wegs.

**Ansatz (es gibt hier nur einen sinnvollen Weg):** `getSample()` (`arabisch-app/madina-arabisch.html:3127`) liefert heute entweder das claude.ai-Sandbox-Objekt (funktioniert nur dort) oder `null`. Es bekommt einen dritten Fall: ist kein Sandbox-Claude da, aber `S.settings.byokKey` gesetzt, liefert es ein selbst gebautes Objekt mit derselben `.json(input, opts)`-Schnittstelle, das den eigentlichen `fetch()` gegen die Anthropic-API macht. Dadurch müssen die drei Aufrufstellen (Tutor/Rollenspiel-Zeile 3485, Rollenspiel-Feedback Zeile 3950, Übersetzer Zeile 4120) **nicht geändert werden** — sie rufen weiterhin nur `sample.json(...)` auf, egal welche Quelle dahintersteckt.

**Was dem Bauenden (mir, in derselben Sitzung) überlassen bleibt:** exakte Fehlertext-Formulierung für einen ungültigen Schlüssel, exakte CSS-Maße für das neue Eingabefeld.
