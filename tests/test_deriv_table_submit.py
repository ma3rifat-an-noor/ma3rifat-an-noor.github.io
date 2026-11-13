# Grading für Typ-3-Ableitungstabellen-Zellen (submitDerivTableCell()), analog zu tests/test_table_submit.py
# für Typ 2. Siehe tests/test_table_chain.py für die Begründung des
# `document.querySelector('#v-tutor').hidden = false`-Musters (macht #v-tutor für Playwrights fill()/
# click() sichtbar, ohne über show('tutor') zu gehen und damit ensureTutorQuiz()/ensureTutorDerivTable()
# auszulösen, die sonst ungewollt weitere Nachrichten anhängen könnten).
#
# Zur Fixture-Wahl: Die Kern-Verhaltensweisen der Bewertung (richtig / norm()-Variante / falsch einmal /
# falsch zweimal / leer / Doppel-Submit) werden hier gegen eine kleine, rein synthetische Test-Lektion
# geprüft - gleiches Vorbild wie tests/test_table_chain.py, das ebenfalls frei erfundene Test-Verben statt
# echter Lektionsdaten benutzt. Das hält die Tests unabhängig davon, wie die reale Lektion gerade
# aussieht. Ergänzend läuft derselbe Pfad gegen die reale b3-l16-Lektion (Entry B, Index 1), die
# vorgegebene "Haupt-Drill-Fixture".
#
# HINWEIS (Stand 2026-11-13, nach dem Nachtragen der Lösungsformen): Die realen Lückenzellen von b3-l16
# tragen inzwischen echte arabische Formen (vorher stand dort durchgängig `values[colIdx] === null`, womit
# eine richtige Antwort gegen die echte Lektion gar nicht erreichbar war). Dass eine richtige Antwort auch
# gegen die ECHTEN Daten als richtig gewertet wird, deckt tests/test_deriv_table_content.py ab; der Lauf
# gegen Entry B weiter unten prüft hier weiterhin bewusst nur den Falsch-Pfad über mehrere Zeilen/Spalten.


def _install_synthetic_fixture(page):
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      DERIV_TABLES['test-deriv-submit'] = [
        {de:'Test-Ableitungstabelle', columns:['col1','col2'], rows:[
          {root:'r1', values:['r1', 'form1'], given:[true, false]},
          {root:'r2', values:['r2', 'form2'], given:[true, false]}
        ]}
      ];
      CHAT.tutor.msgs.push(makeDerivTable('test-deriv-submit', 0));
      renderChat('tutor');
    }""")


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def test_correct_answer_advances(page, served_app):
    page.goto(served_app)
    _install_synthetic_fixture(page)
    step = _active_step(page)
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0


def test_norm_variant_spelling_counts_as_correct(page, served_app):
    page.goto(served_app)
    _install_synthetic_fixture(page)
    step = _active_step(page)
    _submit(page, 0, step["rowIdx"], step["colIdx"], "  " + step["form"] + "  ")  # abweichend: Leerzeichen
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_wrong_once_does_not_advance(page, served_app):
    page.goto(served_app)
    _install_synthetic_fixture(page)
    step = _active_step(page)
    _submit(page, 0, step["rowIdx"], step["colIdx"], "falsch")
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 1
    assert page.locator(".msg.derivTable .dt-hint").count() == 1


def test_wrong_twice_reveals_and_advances(page, served_app):
    page.goto(served_app)
    _install_synthetic_fixture(page)
    step = _active_step(page)
    _submit(page, 0, step["rowIdx"], step["colIdx"], "falsch1")
    _submit(page, 0, step["rowIdx"], step["colIdx"], "falsch2")
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == False
    # Die aufgedeckte Zelle zeigt jetzt die tatsächliche (richtige) Form als reinen Text, nicht die
    # falsche Eingabe der lernenden Person.
    assert page.locator(".msg.derivTable .dt-cell.done.bad").inner_text() == step["form"]


def test_empty_submit_does_not_consume_attempt(page, served_app):
    page.goto(served_app)
    _install_synthetic_fixture(page)
    step = _active_step(page)
    _submit(page, 0, step["rowIdx"], step["colIdx"], "   ")
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0


def test_double_submit_after_answered_is_noop(page, served_app):
    page.goto(served_app)
    _install_synthetic_fixture(page)
    first = _active_step(page)
    _submit(page, 0, first["rowIdx"], first["colIdx"], first["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    # Erneuter Submit mit den VERALTETEN rowIdx/colIdx der schon beantworteten ersten Zelle - der Guard in
    # submitDerivTableCell() (step.rowIdx/step.colIdx müssen zu m.order[m.pos] passen) muss das als No-Op
    # erkennen, unabhängig vom Inhalt der übergebenen Eingabe.
    page.evaluate(
        "([ri, ci, val]) => submitDerivTableCell('tutor', 0, ri, ci, val)",
        [first["rowIdx"], first["colIdx"], first["form"]],
    )
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


# Ergänzend: dasselbe Kernverhalten (falsch zweimal -> aufdecken + weiterschalten) gegen die REALE
# b3-l16-Lektion (Entry B, Index 1). Bestätigt, dass die Scoring-Engine mit der
# tatsächlichen Datenform (mehrere Zeilen, rowIdx/colIdx ungleich 0, given-Spalte gemischt mit
# Lückenspalte in derselben Zeile) genauso funktioniert wie mit der synthetischen 2-Zeilen-Fixture oben.
def test_real_b3_l16_entry_b_wrong_twice_advances_through_all_six_cells(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1));
      renderChat('tutor');
    }""")
    assert page.evaluate("() => CHAT.tutor.msgs[0].steps.length") == 6
    for _ in range(6):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], "غلط1")
        _submit(page, 0, step["rowIdx"], step["colIdx"], "غلط2")
    # Alle 6 Phase-1-Zellen durchlaufen (jede mit 2 Fehlversuchen) -> Phasenübergang zu Phase 2.
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    assert len(page.evaluate("() => Object.keys(CHAT.tutor.msgs[0].answers)")) == 0
