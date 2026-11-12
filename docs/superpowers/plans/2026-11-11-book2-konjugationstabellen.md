# Buch-2-Konjugationstabellen (Typ 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a second, table-based exercise type ("Typ 2") to the Madina-Arabisch-App's Sparmodus, for drilling full Arabic conjugation paradigms (Vergangenheit/Präsens/Imperativ, inkl. Dual) in the classical pedagogical pronoun order, alongside the existing multiple-choice exercise type ("Typ 1").

**Architecture:** Everything lives in the single existing file `arabisch-app/madina-arabisch.html` (no framework, no build step, no module system — all functions/consts are globals in one inline `<script>`). Typ 2 is a new chat message role (`role:'table'`) rendered inside the existing Tutor-tab chat (`CHAT.tutor.msgs`, via the existing `msgHTML()`/`renderChat()` machinery), mirroring how Typ 1 (`role:'quiz'`) already works. State for an in-progress table lives entirely inside its own message object, so it persists automatically through the app's existing `saveChats()` → `localStorage` mechanism — no new top-level state container is needed.

**Tech Stack:** Vanilla JS (ES2020+, inline `<script>`), plain CSS (existing custom-property design tokens), no build tooling. Tests: Python Playwright, driven from the existing venv at `~/Documents/salim/.pdf-tools-venv/` against a local static server — this is the project's established testing method (see `arabisch-app/UEBERGABE.md`); there is no JS unit-test framework in the repo, and since the app has no module system, pure-logic functions are exercised via `page.evaluate()` calling the global function directly in-browser, not via a separate Node harness.

**Spec:** `docs/superpowers/specs/2026-11-11-book2-konjugationstabellen-design.md` — this plan argues from that spec; executors should read both.

## Global Constraints

- Pronoun order (identisch für Vergangenheit/Präsens/Imperativ): 3. Person maskulin → 3. Person feminin → 2. Person maskulin → 2. Person feminin → 1. Person.
- Innerhalb einer Person/Genus-Gruppe: Singular → Dual → Plural.
- 1. Person hat keinen Dual (im Arabischen nicht vorhanden).
- 2. Person Dual: eine einzige, für maskulin und feminin gemeinsame Zelle (wird nur einmal gefragt, nicht zweimal).
- Phase 1: Zellen in der festen Reihenfolge oben. Phase 2: dieselben Zellen in zufälliger Reihenfolge.
- Pro Zelle: 2 Versuche. Nach dem zweiten falschen Versuch wird die korrekte Schreibweise gezeigt, dann geht es weiter.
- Eingabe-Vergleich ignoriert Diakritika — die App hat dafür bereits `norm()` (Zeile ~946 in `madina-arabisch.html`), das muss wiederverwendet, nicht neu gebaut werden.
- Typ 1 (`EX`, `makeQuiz`, `answerQuiz`) bleibt unverändert.
- Nur Sparmodus (offline) betroffen, keine Änderung am Claude-Modus.
- Lektionen mit mehreren Verb-Paradigmen (27, 28) werden als Kette mehrerer eigenständiger Tabellen-Sessions abgebildet, ein Verb nach dem anderen — keine Tabelle mit mehreren Verb-Spalten.
- Eigene arabische Eingabehilfe (Tasten in der App) für Typ-2-Zellen, da nicht allein auf die Geräte-Tastatur verlassen werden soll.
- Diese Plan-Phase baut das Feature und **eine** reale Beispiel-Lektion (Lektion 8, Verb ذهب) als Fixture/Seed-Daten. Das vollständige Einpflegen aller 31 Buch-2-Lektionen in `TABLES` ist eine eigene, spätere Content-Aufgabe und **nicht** Teil dieses Plans.

## Review Focus

- Eingabe mit abweichender, aber von `norm()` bereits behandelter Schreibweise (z. B. أ statt ا, oder mit Leerzeichen am Ende) muss trotzdem als richtig gewertet werden — Task 3 testet das explizit End-to-End, nicht nur `norm()` selbst (das ist bereits vorhandener, ungetesteter Code, den dieser Plan erstmals über Typ 2 nutzt).
- Leere/nur-Leerzeichen-Eingabe darf keinen Versuch verbrauchen (sonst verliert der Nutzer einen Versuch durch ein verirrtes Antippen des Senden-Knopfs) — Task 3.
- Doppeltes Absenden einer bereits beantworteten Zelle (z. B. Doppel-Tap) darf die Zelle nicht zweimal werten oder zweimal weiterschalten — Task 3, analog zum bestehenden `answered`-Schutz in `answerQuiz()`.
- Eine fehlerhafte/leere `TABLES`-Lektion (z. B. zukünftiger Tippfehler bei der Dateneingabe für eine der 31 Lektionen) darf den Chat nicht zum Absturz bringen, sondern soll die Lektion einfach überspringen — Task 2/Task 7.
- Reload mitten in Phase 2 muss exakt die schon gewürfelte Zufallsreihenfolge wiederherstellen, nicht neu würfeln (sonst könnte der Nutzer durch Neuladen eine unbequeme Reihenfolge umgehen) — Task 7 testet das gezielt für Phase 2, nicht nur Phase 1.

---

## Datenschema (für alle Tasks verbindlich)

**`TABLES`** (neue globale Konstante, Stil wie `EX`): `{ [topicId]: Array<VerbTabelle> }`. Ein Eintrag pro Verb; mehrere Einträge = Kette (Task 6).

```js
// VerbTabelle:
{
  verb: 'ذهب',                 // Anzeige-Label
  tense: 'madi',                // 'madi' | 'mudari' | 'amr' — nur Anzeige, keine Logik hängt daran
  de: 'gehen — Vergangenheit',  // Tabellen-Überschrift, Deutsch
  cells: [                       // unsortiert erlaubt — buildTableSteps() sortiert
    {group:'3', gender:'m', num:'sg', pronoun:'هو', form:'ذهب'},
    {group:'3', gender:'m', num:'pl', pronoun:'هم', form:'ذهبوا'},
    {group:'3', gender:'f', num:'sg', pronoun:'هي', form:'ذهبت'},
    {group:'3', gender:'f', num:'pl', pronoun:'هن', form:'ذهبن'},
    {group:'2', gender:'m', num:'sg', pronoun:'أنت', form:'ذهبت'},
    {group:'2', gender:'m', num:'pl', pronoun:'أنتم', form:'ذهبتم'},
    {group:'2', gender:'f', num:'sg', pronoun:'أنتِ', form:'ذهبتِ'},
    {group:'2', gender:'f', num:'pl', pronoun:'أنتن', form:'ذهبتن'},
    {group:'1', gender:null, num:'sg', pronoun:'أنا', form:'ذهبت'},
    {group:'1', gender:null, num:'pl', pronoun:'نحن', form:'ذهبنا'}
    // Dual-Zellen (falls vorhanden): group:'3' mit num:'du' (separat für m/f),
    // und für group:'2' GENAU EINE Zelle mit gender:null, num:'du' (gemeinsam m/f).
  ]
}
```

**`role:'table'`-Chat-Nachricht** (liegt in `CHAT.tutor.msgs`, persistiert automatisch über das bestehende `saveChats()`):

```js
{
  role: 'table',
  topicId: 'b2-l08', verbIndex: 0,       // Lookup-Schlüssel in TABLES, für Kette (Task 6)
  verb: 'ذهب', tense: 'madi', de: 'gehen — Vergangenheit',  // Kopie der Anzeige-Felder aus der VerbTabelle
  steps: [ /* sortierte Zellen, Ausgabe von buildTableSteps() */ ],
  phase: 1,                               // 1 | 2
  order: [0,1,2,...],                     // Index-Permutation in `steps` für die aktuelle Phase (Phase 1 = Identität, Phase 2 = shuffle())
  pos: 0,                                 // Zeiger in `order` — welche Abfrage aktuell läuft
  attempt: 0,                             // Versuche auf der aktuellen Zelle (0, 1, 2)
  answers: {},                            // stepIndex -> {given, correct, attempts}
  done: false
}
```

---

### Task 1: Zellen-Reihenfolge (`buildTableSteps`) + `TABLES`-Fixture

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (neue Konstanten/Funktion, direkt vor `const EX = {` einfügen, gleicher Abschnitt wie die anderen Datenstrukturen)
- Test: `tests/test_build_table_steps.py` (neu)

**Interfaces:**
- Produces: `function buildTableSteps(cells)` — nimmt ein Array von Zell-Objekten (Schema oben, beliebige Reihenfolge) und gibt sie in der festen Reihenfolge zurück: `[3m-sg, 3m-du, 3m-pl, 3f-sg, 3f-du, 3f-pl, 2m-sg, 2-du(shared), 2m-pl, 2f-sg, 2f-pl, 1-sg, 1-pl]` — Zellen, für die keine passende Eingabe existiert, werden einfach ausgelassen (keine Lücken, keine Platzhalter).
- Produces: `const TABLES = {'b2-l08': [{...}]}` mit der Lektion-8-ذهب-Tabelle aus dem Datenschema oben (ohne Dual, da Dual erst ab Lektion 30 vorkommt).

- [ ] **Step 1: Test-Server + `served_app`-Fixture anlegen**

Prüfen, ob ein einfacher lokaler Server für `arabisch-app/` bereits dokumentiert ist (`UEBERGABE.md` erwähnt einen "lokalen Server mit korrektem UTF-8-Charset-Header"); falls nicht wiederauffindbar, einen minimalen Helfer `tests/serve.py` schreiben (stdlib `http.server`, Working Directory `arabisch-app/`, setzt `Content-Type: text/html; charset=utf-8`). Dazu `tests/conftest.py` mit einer `served_app`-Fixture (Scope `session`): startet den Server auf einem freien Port als Subprozess, liefert die URL zu `madina-arabisch.html`, beendet den Subprozess beim Teardown. Diese Fixture wird von allen folgenden Test-Tasks wiederverwendet.

- [ ] **Step 2: Fehlschlagenden Test schreiben**

```python
# tests/test_build_table_steps.py
def test_order_without_dual(page, served_app):
    page.goto(served_app)
    cells = [
        {"group":"1","gender":None,"num":"pl","pronoun":"نحن","form":"ذهبنا"},
        {"group":"3","gender":"f","num":"sg","pronoun":"هي","form":"ذهبت"},
        {"group":"2","gender":"m","num":"sg","pronoun":"أنت","form":"ذهبت"},
        {"group":"3","gender":"m","num":"sg","pronoun":"هو","form":"ذهب"},
        {"group":"1","gender":None,"num":"sg","pronoun":"أنا","form":"ذهبت"},
        {"group":"2","gender":"f","num":"sg","pronoun":"أنتِ","form":"ذهبتِ"},
    ]
    result = page.evaluate("cells => buildTableSteps(cells)", cells)
    order = [(c["group"], c["gender"], c["num"]) for c in result]
    assert order == [("3","m","sg"), ("3","f","sg"), ("2","m","sg"), ("2","f","sg"), ("1",None,"sg"), ("1",None,"pl")]

def test_order_with_shared_dual(page, served_app):
    page.goto(served_app)
    cells = [
        {"group":"3","gender":"m","num":"sg","pronoun":"هو","form":"ذهب"},
        {"group":"3","gender":"m","num":"du","pronoun":"هما","form":"ذهبا"},
        {"group":"3","gender":"f","num":"du","pronoun":"هما","form":"ذهبتا"},
        {"group":"2","gender":"m","num":"sg","pronoun":"أنت","form":"ذهبت"},
        {"group":"2","gender":None,"num":"du","pronoun":"أنتما","form":"ذهبتما"},
        {"group":"2","gender":"f","num":"sg","pronoun":"أنتِ","form":"ذهبتِ"},
    ]
    result = page.evaluate("cells => buildTableSteps(cells)", cells)
    order = [(c["group"], c["gender"], c["num"]) for c in result]
    assert order == [("3","m","sg"), ("3","m","du"), ("3","f","du"), ("2","m","sg"), ("2",None,"du"), ("2","f","sg")]
```

- [ ] **Step 3: Test laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_build_table_steps.py -v`
Expected: FAIL — `buildTableSteps is not defined` (Funktion existiert noch nicht).

- [ ] **Step 4: `buildTableSteps(cells)` implementieren**

In `madina-arabisch.html`, vor `const EX = {`. Feste Bucket-Reihenfolge als Array von `[group, gender, num]`-Tripeln hartcodieren (siehe Step-2-Tests für die exakte Reihenfolge inkl. der gemeinsamen Dual-Zelle bei `group:'2', gender:null, num:'du'`); für jedes Tripel die erste passende Zelle aus `cells` suchen und, falls vorhanden, ans Ergebnis anhängen.

- [ ] **Step 5: `TABLES`-Konstante mit der Lektion-8-Fixture ergänzen**

Direkt nach `buildTableSteps`, nach dem Datenschema oben (ذهب, Vergangenheit, kein Dual).

- [ ] **Step 6: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_build_table_steps.py -v`
Expected: PASS (beide Tests)

- [ ] **Step 7: Syntax-Check**

Run: `node --check <(sed -n '/<script>/,/<\/script>/p' arabisch-app/madina-arabisch.html | sed '1d;$d')`
Expected: kein Fehler

- [ ] **Step 8: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_build_table_steps.py tests/serve.py tests/conftest.py
git commit -m "feat: add buildTableSteps() and TABLES data structure for Typ-2 conjugation drills"
```

---

### Task 2: `makeTable()` + Rendering der Phase-1-Tabelle

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (neue Funktion `makeTable`, neuer Zweig in `msgHTML()`, neues CSS)
- Test: `tests/test_table_render.py` (neu)

**Interfaces:**
- Consumes: `buildTableSteps(cells)` (Task 1), `TABLES` (Task 1), bestehende `esc()`, `rich()`, `icon()`, `speakBtn()` (bereits vorhanden, siehe Zeilen ~940-952).
- Produces: `function makeTable(topicId, verbIndex)` — liest `TABLES[topicId][verbIndex]`; gibt `null` zurück, wenn der Eintrag fehlt oder `cells` leer/kein Array ist (Review-Focus: fehlerhafte Lektion darf nicht abstürzen); sonst das `role:'table'`-Nachrichtenobjekt aus dem Datenschema oben, mit `phase:1`, `order` = Identität, `pos:0`, `attempt:0`, `answers:{}`, `done:false`.
- Produces: in `msgHTML(m, i, kind)` ein neuer Zweig `if (m.role === 'table')`, der die Tabelle rendert: Kopfzeile mit `m.verb`/`m.de`, dann pro Zelle in `m.steps` eine Zeile mit Pronomen (arabisch) + Antwort-Zelle — bereits beantwortete Zellen (`m.answers[idx]` vorhanden) zeigen die korrekte Form, die aktuelle Zelle (`m.order[m.pos]`) zeigt ein Text-Eingabefeld + Absenden-Button (`data-table-submit`, `data-qi`, `data-kind`), restliche Zellen sind leer/ausgegraut.

- [ ] **Step 1: Fehlschlagenden Test schreiben**

```python
# tests/test_table_render.py
def test_table_starts_with_header_and_first_cell_active(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.topic = 'b2-l08'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-head").inner_text().strip() != ""
    assert page.locator(".msg.table .t-row.active input[type=text]").count() == 1
    assert page.locator(".msg.table .t-row.done").count() == 0

def test_make_table_returns_null_for_missing_topic(page, served_app):
    page.goto(served_app)
    result = page.evaluate("() => makeTable('does-not-exist', 0)")
    assert result is None
```

(`served_app`-Fixture kommt aus `tests/conftest.py`, bereits in Task 1 angelegt.)

- [ ] **Step 2: Test laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_render.py -v`
Expected: FAIL — `makeTable is not defined`

- [ ] **Step 3: `makeTable(topicId, verbIndex)` implementieren**

Direkt nach `buildTableSteps`/`TABLES`.

- [ ] **Step 4: `role:'table'`-Zweig in `msgHTML()` implementieren**

In der bestehenden Funktion `msgHTML(m, i, kind)` (Zeile ~1225), als neuer `if (m.role === 'table')`-Zweig vor der abschließenden `return '';`. HTML-Grundgerüst: `.msg.table` → `.t-head` (Verb + Zeitform) → pro Zelle `.t-row` (Klassen `done`/`active`/leer je Zustand), in der aktiven Zeile `<input type="text" dir="rtl" lang="ar" id="t-input-<i>">` plus `<button data-table-submit data-qi="<i>" data-kind="<kind>">`.

- [ ] **Step 5: CSS für `.msg.table`, `.t-head`, `.t-row` ergänzen**

Bestehende Design-Tokens wiederverwenden (`var(--surface)`, `var(--red)`, `var(--green)` o. ä., wie bei `.btn.bad`/`.opt`); am bestehenden CSS-Block für `.quiz`/`.opts` orientieren.

- [ ] **Step 6: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_render.py -v`
Expected: PASS

- [ ] **Step 7: Syntax-Check** (wie Task 1 Step 7)

- [ ] **Step 8: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_table_render.py
git commit -m "feat: render Typ-2 conjugation table as a persistent chat bubble"
```

---

### Task 3: `submitTableCell()` — Prüfen, Versuche, Weiterschalten

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (neue Funktion, neuer Zweig im globalen Click-Handler, `msgHTML()`-Zweig um Fehler-/Retry-Anzeige erweitern)
- Test: `tests/test_table_submit.py` (neu)

**Interfaces:**
- Consumes: bestehendes `norm()` (Zeile ~946), das `role:'table'`-Schema und `msgHTML()`-Rendering aus Task 2.
- Produces: `function submitTableCell(kind, qi, rawInput)` — Guard: no-op wenn `m` fehlt, `m.role!=='table'` oder `m.done`; no-op (kein Versuchsverbrauch) wenn `norm(rawInput)` leer ist; sonst `m.attempt++`, Vergleich `norm(rawInput) === norm(step.form)`; bei richtig oder beim zweiten Fehlversuch: Eintrag in `m.answers`, `m.pos++`, `m.attempt = 0`, bei Phasenende Übergang (siehe Task 4); bei erstem Fehlversuch: `m.pos`/`m.attempt` so lassen, dass die UI "noch ein Versuch" zeigt, ohne weiterzuschalten. Ruft am Ende `renderChat(kind)` und `saveChats()`.
- Produces: im globalen `document.addEventListener('click', ...)`-Handler (Zeile ~1786) ein neuer Zweig `if (d.tableSubmit !== undefined){ submitTableCell(d.kind, Number(d.qi), $('#t-input-' + d.qi).value); return; }`.

- [ ] **Step 1: Fehlschlagende Tests schreiben**

```python
# tests/test_table_submit.py
def test_correct_answer_advances(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهب")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0

def test_norm_variant_spelling_counts_as_correct(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", " ذهب ")  # abweichend: Leerzeichen
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1

def test_wrong_once_does_not_advance(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "قرأ")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 1

def test_wrong_twice_reveals_and_advances(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "قرأ"); page.click('[data-table-submit][data-qi="0"]')
    page.fill("#t-input-0", "كتب"); page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == False

def test_empty_submit_does_not_consume_attempt(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "   ")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0

def test_double_submit_after_answered_is_noop(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهب"); page.click('[data-table-submit][data-qi="0"]')
    page.evaluate("() => submitTableCell('tutor', 0, 'ذهب')")  # Zelle 0 ist schon fertig, Zelle 1 ist jetzt aktiv
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1  # unverändert, kein zweiter Advance durch den alten Aufruf
```

- [ ] **Step 2: Tests laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_submit.py -v`
Expected: FAIL — `submitTableCell is not defined`

- [ ] **Step 3: `submitTableCell(kind, qi, rawInput)` implementieren**

Logik wie im Interfaces-Block oben beschrieben.

- [ ] **Step 4: Click-Handler-Zweig + Retry-/Reveal-Anzeige in `msgHTML()` ergänzen**

Aktive Zeile zeigt nach einem ersten Fehlversuch (`m.attempt === 1` und aktuelle Zelle noch nicht in `answers`) einen Hinweistext ("Nicht ganz — versuch's noch mal") unter dem Eingabefeld; eine aufgelöste falsche Zelle (`m.answers[idx].correct === false`) zeigt die korrekte Form zusätzlich farblich markiert (vorhandene `.bad`/`.fix`-Klassen als Vorbild nehmen).

- [ ] **Step 5: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_submit.py -v`
Expected: PASS (alle sechs)

- [ ] **Step 6: Syntax-Check** (wie Task 1 Step 7)

- [ ] **Step 7: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_table_submit.py
git commit -m "feat: grade Typ-2 table cells with two-attempt retry-then-reveal rule"
```

---

### Task 4: Phase 1 → Phase 2 (Zufallswiederholung) + Tabellen-Abschluss

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (`submitTableCell()` um Phasenübergang erweitern, `msgHTML()` um Phase-2-Kennzeichnung/Abschluss-Anzeige erweitern)
- Test: `tests/test_table_phases.py` (neu)

**Interfaces:**
- Consumes: `submitTableCell()` (Task 3), bestehendes `shuffle()` (Zeile ~953).
- Produces: Phasenübergang-Logik in `submitTableCell()`: wenn `m.pos === m.order.length` nach einem Advance: bei `m.phase === 1` → `m.phase = 2; m.order = shuffle(m.steps.map((_, idx) => idx)); m.pos = 0;`; bei `m.phase === 2` → `m.done = true`.
- Produces: in `msgHTML()` eine sichtbare Phase-2-Kennzeichnung (z. B. Label "Wiederholung, zufällige Reihenfolge" über der aktiven Zeile, sobald `m.phase === 2`) und eine Abschluss-Darstellung, wenn `m.done` (z. B. ein abschließender Haken/Text statt Eingabefeld).

- [ ] **Step 1: Fehlschlagende Tests schreiben**

```python
# tests/test_table_phases.py
def _answer_all_phase1(page):
    for i in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill(f"#t-input-{pos}", step["form"])
        page.click(f'[data-table-submit][data-qi="{pos}"]')

def test_phase2_starts_with_same_cell_set(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    _answer_all_phase1(page)
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert sorted(order) == list(range(10))

def test_table_marks_done_after_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    _answer_all_phase1(page)
    for _ in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        if page.evaluate("() => CHAT.tutor.msgs[0].done"): break
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill(f"#t-input-{pos}", step["form"])
        page.click(f'[data-table-submit][data-qi="{pos}"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.locator(".msg.table .t-row.active").count() == 0
```

- [ ] **Step 2: Tests laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_phases.py -v`
Expected: FAIL (Phase bleibt 1, kein Übergang)

- [ ] **Step 3: Phasenübergang in `submitTableCell()` implementieren**

- [ ] **Step 4: Phase-2-Label + Abschluss-Darstellung in `msgHTML()` implementieren**

- [ ] **Step 5: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_phases.py -v`
Expected: PASS

- [ ] **Step 6: Syntax-Check** (wie Task 1 Step 7)

- [ ] **Step 7: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_table_phases.py
git commit -m "feat: add shuffled phase-2 review and completion state to Typ-2 tables"
```

---

### Task 5: Eigene arabische Eingabehilfe

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (neue Render-Funktion, neuer Zweig im globalen Click-Handler, in `msgHTML()`-Tabellen-Zweig einbinden)
- Test: `tests/test_table_input_helper.py` (neu)

**Interfaces:**
- Produces: `function arabicKeysHTML(targetInputId)` — gibt HTML für eine Tastenreihe zurück: Standard-arabisches Alphabet (28 Buchstaben, keine Diakritika-Tasten nötig, da Eingabe ohnehin diakritikafrei verglichen wird) plus eine Rücktaste; jede Buchstaben-Taste `data-key-insert="<Buchstabe>" data-key-target="<targetInputId>"`, Rücktaste `data-key-back="<targetInputId>"`.
- Consumes: wird im `role:'table'`-Zweig von `msgHTML()` (Task 2) unter dem aktiven Eingabefeld eingebunden, mit `targetInputId = 't-input-' + aktiverIndex`.
- Produces: im globalen Click-Handler zwei neue Zweige: `if (d.keyInsert !== undefined){ const el = $('#' + d.keyTarget); el.value += d.keyInsert; el.focus(); return; }` und `if (d.keyBack !== undefined){ const el = $('#' + d.keyBack); el.value = el.value.slice(0, -1); el.focus(); return; }`.

- [ ] **Step 1: Fehlschlagenden Test schreiben**

```python
# tests/test_table_input_helper.py
def test_virtual_keys_append_to_input(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.click('[data-key-insert="ذ"][data-key-target="t-input-0"]')
    page.click('[data-key-insert="ه"][data-key-target="t-input-0"]')
    page.click('[data-key-insert="ب"][data-key-target="t-input-0"]')
    assert page.input_value("#t-input-0") == "ذهب"

def test_backspace_key_removes_last_char(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهبx")
    page.click('[data-key-back="t-input-0"]')
    assert page.input_value("#t-input-0") == "ذهب"

def test_submit_via_helper_typed_value_is_graded(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    for ch in "ذهب":
        page.click(f'[data-key-insert="{ch}"][data-key-target="t-input-0"]')
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
```

- [ ] **Step 2: Test laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_input_helper.py -v`
Expected: FAIL

- [ ] **Step 3: `arabicKeysHTML()` implementieren und in den Tabellen-Zweig von `msgHTML()` einbinden**

- [ ] **Step 4: Click-Handler-Zweige `keyInsert`/`keyBack` implementieren**

- [ ] **Step 5: CSS für die Tastenreihe ergänzen** (kompaktes Grid, an `.chip`/`.opt` orientieren)

- [ ] **Step 6: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_input_helper.py -v`
Expected: PASS

- [ ] **Step 7: Syntax-Check** (wie Task 1 Step 7)

- [ ] **Step 8: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_table_input_helper.py
git commit -m "feat: add on-screen Arabic input helper for Typ-2 table cells"
```

---

### Task 6: Verb-Kette für Mehrfach-Paradigmen-Lektionen (z. B. Lektion 27/28)

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (`submitTableCell()`-Abschlusslogik aus Task 4 um Verkettung erweitern)
- Test: `tests/test_table_chain.py` (neu)

**Interfaces:**
- Consumes: `m.done`-Übergang aus Task 4, `makeTable(topicId, verbIndex)` aus Task 2.
- Produces: Erweiterung der Abschlusslogik in `submitTableCell()`: sobald `m.done = true` gesetzt wird, prüfen ob `TABLES[m.topicId][m.verbIndex + 1]` existiert — wenn ja, `ctx.msgs.push(makeTable(m.topicId, m.verbIndex + 1))`; wenn nein, `ctx.msgs.push({role:'note', text:'Tabellen dieser Lektion abgeschlossen.'})`.
- Benötigt eine zweite Test-Fixture in `TABLES` mit zwei Verben (klein gehalten, z. B. je 2 Zellen, nur für diesen Test — siehe Step 1), nicht Teil der echten Lektion 8.

- [ ] **Step 1: Fehlschlagenden Test schreiben**

```python
# tests/test_table_chain.py
def test_second_verb_starts_automatically(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      TABLES['test-chain'] = [
        {verb:'أ', tense:'madi', de:'Test A', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'أ1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'أ2'}]},
        {verb:'ب', tense:'madi', de:'Test B', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'ب1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'ب2'}]}
      ];
      CHAT.tutor.msgs.push(makeTable('test-chain', 0)); renderChat('tutor');
    }""")
    for form in ["أ1", "أ2", "أ1", "أ2"]:  # Phase 1 + Phase 2 von Verb A, je 2 Zellen
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        page.fill(f"#t-input-{pos}", form)
        page.click(f'[data-table-submit][data-qi="{pos}"]')
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[1].verb") == "ب"
    assert page.evaluate("() => CHAT.tutor.msgs[1].verbIndex") == 1

def test_note_shown_after_last_verb_in_chain(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      TABLES['test-chain-single'] = [{verb:'أ', tense:'madi', de:'Test A', cells:[
        {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'أ1'},
        {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'أ2'}]}];
      CHAT.tutor.msgs.push(makeTable('test-chain-single', 0)); renderChat('tutor');
    }""")
    for form in ["أ1", "أ2", "أ1", "أ2"]:
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        page.fill(f"#t-input-{pos}", form)
        page.click(f'[data-table-submit][data-qi="{pos}"]')
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "note"
```

- [ ] **Step 2: Tests laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_chain.py -v`
Expected: FAIL (nur eine Nachricht im Chat)

- [ ] **Step 3: Verkettungslogik implementieren**

- [ ] **Step 4: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_chain.py -v`
Expected: PASS

- [ ] **Step 5: Syntax-Check** (wie Task 1 Step 7)

- [ ] **Step 6: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_table_chain.py
git commit -m "feat: chain multiple verb tables within one lesson (Lektion 27/28 style)"
```

---

### Task 7: Einstieg aus der Themenauswahl + Robustheit + Fortschritt über Reload

**Files:**
- Modify: `arabisch-app/madina-arabisch.html` (`ensureTutorQuiz()` erweitern)
- Test: `tests/test_table_entry_and_resume.py` (neu)

**Interfaces:**
- Consumes: `ensureTutorQuiz()` (bestehend, Zeile ~1360), `makeTable()` (Task 2), `TABLES` (Task 1).
- Produces: `ensureTutorQuiz()` erweitert um eine vorgeschaltete Prüfung — vor der bestehenden Logik: wenn `ctx.topic && Array.isArray(TABLES[ctx.topic]) && TABLES[ctx.topic].length`, UND die letzte Nachricht ist keine unfertige `role:'table'`-Nachricht (`last.role === 'table' && !last.done`), dann `const m = makeTable(ctx.topic, 0); if (m){ ctx.msgs.push(m); saveChats(); return; }`; danach normal weiter mit der bestehenden `role:'quiz'`-Logik (unverändert) für alle anderen Themen. Wenn `makeTable()` `null` liefert (Review Focus: defekte Lektionsdaten), fällt die Funktion ohne Fehler auf die bestehende Typ-1-Logik zurück.

- [ ] **Step 1: Fehlschlagende Tests schreiben**

```python
# tests/test_table_entry_and_resume.py
def test_selecting_topic_with_table_starts_table(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == True

def test_malformed_table_lesson_falls_back_to_quiz(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { TABLES['broken'] = [{verb:'x', cells:[]}]; }")
    page.evaluate("() => { practiceTopic('broken'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == False

def test_reload_resumes_table_mid_phase1(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    page.fill("#t-input-0", "ذهب")
    page.click('[data-table-submit][data-qi="0"]')
    page.reload()
    page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').pos") == 1

def test_reload_resumes_exact_shuffle_in_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    for i in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').pos")
        step = page.evaluate(f"() => {{ const t = CHAT.tutor.msgs.find(m => m.role === 'table'); return t.steps[t.order[{pos}]]; }}")
        page.fill(f"#t-input-{pos}", step["form"])
        page.click(f'[data-table-submit][data-qi="{pos}"]')
    order_before = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').order")
    page.reload()
    page.evaluate("() => show('tutor')")
    order_after = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').order")
    assert order_before == order_after
```

- [ ] **Step 2: Tests laufen lassen, Fehlschlag bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_entry_and_resume.py -v`
Expected: FAIL (erste drei — keine Tabelle startet über `practiceTopic`)

- [ ] **Step 3: `ensureTutorQuiz()` wie im Interfaces-Block beschrieben erweitern**

- [ ] **Step 4: Tests laufen lassen, Erfolg bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/test_table_entry_and_resume.py -v`
Expected: PASS (alle vier)

- [ ] **Step 5: Gesamten Testlauf über alle Tasks bestätigen**

Run: `~/Documents/salim/.pdf-tools-venv/bin/python -m pytest tests/ -v`
Expected: PASS (alle Tests aus Task 1–7)

- [ ] **Step 6: Syntax-Check** (wie Task 1 Step 7)

- [ ] **Step 7: Playwright-Sichtprüfung bei 390 px Breite** (wie im bisherigen Vorgehen laut `UEBERGABE.md`)

Ein Screenshot einer laufenden Tabellen-Session bei 390px Viewport-Breite anfertigen und visuell gegen die bestehenden Typ-1-Quiz-Bubbles prüfen (Lesbarkeit, kein horizontales Scrollen).

- [ ] **Step 8: Commit**

```bash
git add arabisch-app/madina-arabisch.html tests/test_table_entry_and_resume.py
git commit -m "feat: wire Typ-2 tables into topic selection, with resume across reloads"
```

---

## Außerhalb dieses Plans (spätere, eigene Aufgabe)

Das Einpflegen aller 31 echten Buch-2-Lektionen in `TABLES` (Zuordnung welche Lektion welches Verb/welche Zeitform bekommt, vollständige Zellen-Daten aus dem Buch) — siehe Design-Dokument, Abschnitt "Was dem Builder offen bleibt". Dieser Plan liefert das fertige, getestete Feature plus eine reale Beispiel-Lektion (Lektion 8); die Content-Befüllung der restlichen 30 Lektionen ist ein separater, nachfolgender Schritt.
