# Rendering-Tests für role:'derivTable' (Buch 3, Typ-3-Ableitungstabellen). Reines Rendering, mirror von
# tests/test_table_render.py: kein hashchange auf 'tutor' nötig, weil Locator.inner_text()/.count()/
# .get_attribute() keine Sichtbarkeits-Actionability-Checks durchführen (anders als fill()/click() in
# tests/test_table_input_helper.py) - die Nachricht liegt im DOM, auch während #v-tutor per `hidden`
# ausgeblendet ist. Phase 2 verdrahtet bewusst keinen Klick-Handler für data-deriv-submit (kommt erst in
# Phase 3), daher wird hier nur die gerenderte Markup-Struktur geprüft, nie geklickt/befüllt.

import pathlib

QA_SCREENSHOTS = pathlib.Path(__file__).resolve().parent.parent / ".qa-screenshots"

def test_deriv_table_entry_b_renders_header_and_first_active_cell(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1)); renderChat('tutor'); }")
    # Kopfzeile mit der deutschen/gedruckten Überschrift (m.de) ist nicht leer.
    assert page.locator(".msg.derivTable .t-head").inner_text().strip() != ""
    # Genau ein aktives Eingabefeld - Entry B (مصدر باب فعّل) ist eine normale, nicht-studyOnly Drilltabelle.
    # Seit dem Layout-Fix (Abschluss-Review 2026-11-13) lebt das Eingabefeld NICHT mehr in der gequetschten
    # .dt-cell selbst, sondern im eigenständigen, volle-Breite-.dt-answer-Panel direkt nach der .dt-row (die
    # .dt-cell.active ist seitdem nur noch ein schmaler visueller Marker, siehe .dt-active-marker).
    assert page.locator(".msg.derivTable .dt-answer input[type=text]").count() == 1
    assert page.locator(".msg.derivTable .dt-cell.active input[type=text]").count() == 0
    assert page.locator(".msg.derivTable").get_attribute("class") == "msg derivTable"
    # Das aktive Feld muss zur ERSTEN Lückenzelle in gedruckter Reihenfolge gehören (erster Step von
    # buildDerivTableSteps für diesen Eintrag), adressiert über die data-ri/data-ci-Attribute am
    # zugehörigen Senden-Knopf.
    first_step = page.evaluate("() => buildDerivTableSteps(DERIV_TABLES['b3-l16'][1])[0]")
    btn = page.locator(".msg.derivTable [data-deriv-submit]")
    assert btn.count() == 1
    assert int(btn.get_attribute("data-ri")) == first_step["rowIdx"]
    assert int(btn.get_attribute("data-ci")) == first_step["colIdx"]
    # Frisch erzeugt (pos=0): noch keine bewertete Zelle.
    assert page.locator(".msg.derivTable .dt-cell.done").count() == 0


def test_deriv_table_studyonly_entry_a_has_no_inputs_and_is_marked_reference(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.derivTable").count() == 1
    # Entry A (Hauptmodell) ist 100% given -> keine Eingaben, keine Senden-Knöpfe, kein aktiver Zustand,
    # irgendwo in der gerenderten Nachricht.
    assert page.locator(".msg.derivTable input").count() == 0
    assert page.locator(".msg.derivTable [data-deriv-submit]").count() == 0
    assert page.locator(".msg.derivTable .dt-cell.active").count() == 0
    # Visuell/strukturell als Referenzkarte markiert: eigene studyOnly-Klasse am Nachrichten-Container
    # plus Badge-Text.
    assert page.locator(".msg.derivTable.studyOnly").count() == 1
    assert "Referenz" in page.locator(".msg.derivTable .dt-badge").inner_text()


def test_given_cell_in_drill_table_renders_as_reference_text_not_input(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1)); renderChat('tutor'); }")
    # Entry B, Zeile 0 (Wurzel كَبَّرَ): die الماضي-Spalte ist given:true (gedruckte Referenz), nur die
    # المصدر-Spalte ist die Lückenzelle. Die gedruckte كَبَّرَ-Zelle muss als reiner Text erscheinen, nicht
    # als Eingabefeld.
    given_texts = page.locator(".msg.derivTable .dt-cell.given").all_inner_texts()
    assert "كَبَّرَ" in given_texts
    assert page.locator(".msg.derivTable .dt-cell.given input").count() == 0


def test_retry_hint_is_rendered_left_to_right(page, served_app):
    # Regression (Abschluss-Review 2026-11-13): .dt-hint erbte direction:rtl von .dt-cell (anders als
    # .t-hint bei Typ 2, dessen Elternelement .t-cell keine Richtung setzt). Der deutsche Hinweistext
    # "Nicht ganz — versuch's noch mal." wurde dadurch in einem RTL-Absatz gesetzt, und der Schlusspunkt
    # sprang als neutrales Zeichen an den linken Rand der zweiten Zeile (".mal" statt "mal.").
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1));
      renderChat('tutor');
    }""")
    step = page.evaluate("() => { const t = CHAT.tutor.msgs[0]; return t.steps[t.order[t.pos]]; }")
    page.fill(f"#dt-input-0-{step['rowIdx']}-{step['colIdx']}", "غلط")
    page.click(f'[data-deriv-submit][data-mi="0"][data-ri="{step["rowIdx"]}"][data-ci="{step["colIdx"]}"]')
    hint = page.locator(".msg.derivTable .dt-hint")
    assert hint.count() == 1
    assert hint.evaluate("el => getComputedStyle(el).direction") == "ltr"


def test_make_deriv_table_returns_null_message_for_missing_topic(page, served_app):
    # Randfall-Robustheit, analog zu test_table_render.py: eine fehlende Lektion liefert null, nie eine
    # tote/unbeantwortbare derivTable-Nachricht. Berührt Phase 1, nicht diese Rendering-Aufgabe - dient nur
    # als Beleg, dass der Renderer nie mit null gefüttert wird.
    page.goto(served_app)
    result = page.evaluate("() => makeDerivTable('does-not-exist', 0)")
    assert result is None


def test_deriv_table_columns_render_right_to_left_matching_print_order(page, served_app):
    # Regression für den Spalten-Spiegelungs-Bug: m.columns ist in GEDRUCKTER (rechts-nach-links)
    # Reihenfolge angegeben (Spalte 0 = ganz rechts im Buch). Ohne direction:rtl auf dem Flex-Container
    # (.dt-row) landet Spalte 0 optisch ganz LINKS - das Spiegelbild der gedruckten Reihenfolge. Fix:
    # direction:rtl auf .dt-row. Hier wird das anhand echter Bildschirmkoordinaten verifiziert, nicht nur
    # über die Markup-Reihenfolge im DOM (die bleibt unverändert - nur die visuelle Anordnung muss stimmen).
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(served_app)
    # bounding_box() braucht ein tatsächlich sichtbares Element (anders als inner_text()/count() weiter
    # unten in dieser Datei) - deshalb hier zusätzlich location.hash='tutor', damit #v-tutor nicht mehr
    # per `hidden` ausgeblendet ist (siehe tests/test_table_phases.py für dasselbe Muster bei Typ 2).
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1)); renderChat('tutor'); }")
    heads = page.locator(".msg.derivTable .dt-col-head")
    assert heads.count() >= 2
    first_box = heads.first.bounding_box()
    last_box = heads.last.bounding_box()
    assert first_box is not None and last_box is not None
    # Spalte 0 (erster Eintrag in m.columns, z. B. الماضي) muss weiter RECHTS (größeres x) liegen als die
    # letzte Spalte (z. B. المصدر) - genau wie im gedruckten Buch und in korrekter Leserichtung.
    assert first_box["x"] > last_box["x"]


def test_deriv_table_row_has_no_duplicate_leading_root_column(page, served_app):
    # Regression für den Dopplungs-Bug: row.root ist per Definition identisch mit row.values[0] (die
    # الماضي-Form IST die Wurzel der Ableitungsreihe). Die frühere eigene .dt-rootcol/.dt-root-Spalte
    # zeigte dasselbe Wort wie die erste Datenspalte ein zweites Mal an. Fix: die Spalte wurde komplett
    # entfernt - jede Zeile hat jetzt genau so viele .dt-cell-Elemente wie m.columns Einträge, nicht mehr.
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1)); renderChat('tutor'); }")
    assert page.locator(".msg.derivTable .dt-rootcol").count() == 0
    assert page.locator(".msg.derivTable .dt-root").count() == 0
    n_columns = page.evaluate("() => DERIV_TABLES['b3-l16'][1].columns.length")
    first_row = page.locator(".msg.derivTable .dt-row:not(.dt-head-row)").first
    assert first_row.locator(".dt-cell").count() == n_columns
    # Die erste Datenspalte (values[0], immer given:true in allen bisherigen Einträgen) zeigt die Wurzel
    # genau EINMAL - nicht noch einmal als separates Label davor.
    first_row_texts = first_row.locator(".dt-cell").all_inner_texts()
    assert first_row_texts.count("كَبَّرَ") == 1


def test_entry_d_four_column_layout_is_usable_at_mobile_viewport(page, served_app):
    # Regression für den Layout-Bug aus dem Abschluss-Review 2026-11-13: Entry D (اسم المفعول, tableIndex
    # 3) hat 4 Spalten. VORHER quetschte msgHTML() Eingabe + Senden-Knopf + Hinweis + die volle 29-Tasten-
    # arabicKeysHTML()-Tastatur in EINE von 4 .dt-cell-Spalten - bei 390px Viewportbreite schrumpfte das
    # Eingabefeld auf ~25px, die Tastatur wurde zu einem 20-zeiligen Turm, und der eigene Zeileninhalt
    # sowie die Kopfzeile der Tabelle wurden weit nach unten/aus dem Bildschirm gedrängt (siehe
    # .qa-screenshots/entry-D-4col-active.png und viewport-entry-D-active.png, VOR dem Fix aufgenommen).
    # NACHHER lebt die interaktive UI in einem eigenständigen, volle-Breite-.dt-answer-Panel direkt nach
    # der .dt-row - die aktive .dt-cell selbst ist nur noch ein schmaler Marker (siehe .dt-active-marker),
    # das Spaltenzahl-Contract und die RTL-Spaltenreihenfolge bleiben dabei unverändert (dieselbe Prüfung
    # wie test_deriv_table_row_has_no_duplicate_leading_root_column /
    # test_deriv_table_columns_render_right_to_left_matching_print_order oben, hier gegen den schlimmsten
    # Fall mit 4 statt 2 Spalten).
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(served_app)
    page.evaluate("""() => {
      location.hash = 'tutor';
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 3));
      renderChat('tutor');
    }""")

    n_columns = page.evaluate("() => DERIV_TABLES['b3-l16'][3].columns.length")
    assert n_columns == 4

    # Spaltenzahl-Contract: die Zeile mit der aktiven Zelle hat weiterhin genau n_columns .dt-cell-
    # Elemente - der Fix darf diese Zahl nicht verändern (keine zusätzliche Spalte für die Antwort-UI).
    active_row = page.locator(".msg.derivTable .dt-row:has(.dt-cell.active)")
    assert active_row.count() == 1
    assert active_row.locator(".dt-cell").count() == n_columns

    # RTL-Spaltenreihenfolge unverändert: Spalte 0 (الماضي) weiterhin weiter rechts als die letzte Spalte
    # (اسم المفعول) - exakt dieselbe Prüfung wie test_deriv_table_columns_render_right_to_left_matching_print_order.
    heads = page.locator(".msg.derivTable .dt-col-head")
    assert heads.count() == n_columns
    first_head_box = heads.first.bounding_box()
    last_head_box = heads.last.bounding_box()
    assert first_head_box is not None and last_head_box is not None
    assert first_head_box["x"] > last_head_box["x"]

    # Eingabefeld ist jetzt vernünftig breit, nicht mehr ~25px (gemessen nach dem Fix: ~252px bei 390px
    # Viewportbreite - großzügige Schwelle von 150px, um nicht an exakten Pixelwerten zu kleben).
    answer_input = page.locator(".msg.derivTable .dt-answer input[type=text]")
    assert answer_input.count() == 1
    input_box = answer_input.bounding_box()
    assert input_box is not None
    assert input_box["width"] > 150

    # Tastatur ist kein 20-zeiliger Turm mehr: bei voller Panel-Breite wickeln sich die 29 Buchstaben +
    # 1 Rücktaste in wenige Zeilen (gemessen: ~124px hoch). Grosszügige Schwelle von 200px - ein echter
    # 20-Zeilen-Turm wäre um ein Vielfaches höher.
    keys = page.locator(".msg.derivTable .dt-answer .t-keys")
    assert keys.count() == 1
    keys_box = keys.bounding_box()
    assert keys_box is not None
    assert keys_box["height"] < 200

    # Tabellenkopf bleibt sichtbar/sinnvoll positioniert, statt durch eine überdimensionierte aktive Zelle
    # weit nach unten verdrängt zu werden (gemessen nach dem Fix: y≈64px bei 390px Viewportbreite).
    head = page.locator(".msg.derivTable .t-head")
    head_box = head.bounding_box()
    assert head_box is not None
    assert head_box["y"] < 150

    # Vorher/Nachher-Belege für den menschlichen Review: Panel- und Viewport-Screenshot nach dem Fix,
    # neben die bereits vor dem Fix aufgenommenen entry-D-4col-active.png / viewport-entry-D-active.png
    # abgelegt (.qa-screenshots/ ist gitignored).
    QA_SCREENSHOTS.mkdir(exist_ok=True)
    page.locator(".msg.derivTable").screenshot(path=str(QA_SCREENSHOTS / "entry-D-4col-active-after-fix.png"))
    page.screenshot(path=str(QA_SCREENSHOTS / "viewport-entry-D-active-after-fix.png"))
