# Verkettung mehrerer Ableitungstabellen-Einträge innerhalb einer Lektion (Typ 3), analog zu
# tests/test_table_chain.py für Typ 2. Zwei Verkettungswege existieren hier (anders als bei Typ 2):
# (1) eine normale Drill-Tabelle wird nach Phase 2 fertig -> submitDerivTableCell() verkettet automatisch;
# (2) eine studyOnly-Referenzkarte (z. B. b3-l16 Entry A) ist von Anfang an done, braucht also den
# expliziten Weiter-Button/continueDerivTable(), um überhaupt weiterzuschalten (siehe Design-Doc und
# Kommentare bei continueDerivTable() in madina-arabisch.html).
#
# Für Weg (1) wird hier - wie in tests/test_table_chain.py selbst - eine kleine, rein synthetische
# Zwei-Einträge-Fixture benutzt (je 1 Lückenzelle, schnell durchzuspielen), PLUS ergänzend ein Lauf gegen
# die reale b3-l16-Lektion (Entry B -> Entry C), um die echte Datenform mit abzudecken.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def test_second_entry_starts_automatically(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      DERIV_TABLES['test-deriv-chain'] = [
        {de:'Kette A', columns:['col1','col2'], rows:[{root:'r1', values:['r1','a1'], given:[true,false]}]},
        {de:'Kette B', columns:['col1','col2'], rows:[{root:'r2', values:['r2','b1'], given:[true,false]}]}
      ];
      CHAT.tutor.msgs.push(makeDerivTable('test-deriv-chain', 0));
      renderChat('tutor');
    }""")
    # Entry A hat genau 1 Lückenzelle -> ein richtiger Submit beendet Phase 1 (1 von 1 Zellen), der
    # nächste beendet Phase 2 (ebenfalls 1 von 1 Zellen, triviale Shuffle-Permutation).
    _submit(page, 0, 0, 1, "a1")
    _submit(page, 0, 0, 1, "a1")
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "derivTable"
    assert page.evaluate("() => CHAT.tutor.msgs[1].de") == "Kette B"
    assert page.evaluate("() => CHAT.tutor.msgs[1].tableIndex") == 1


def test_note_shown_after_last_entry_in_chain(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      DERIV_TABLES['test-deriv-chain-single'] = [
        {de:'Kette Einzel', columns:['col1','col2'], rows:[{root:'r1', values:['r1','a1'], given:[true,false]}]}
      ];
      CHAT.tutor.msgs.push(makeDerivTable('test-deriv-chain-single', 0));
      renderChat('tutor');
    }""")
    _submit(page, 0, 0, 1, "a1")
    _submit(page, 0, 0, 1, "a1")
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "note"
    # Exakt dieselbe Abschluss-Notiz wie Typ 2 (submitTableCell()s Verkettung) - bewusst wiederverwendet,
    # keine neue Notiz-Variante erfunden.
    assert page.evaluate("() => CHAT.tutor.msgs[1].text") == "Tabellen dieser Lektion abgeschlossen."


def test_real_b3_l16_entry_b_completion_chains_to_entry_c(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1));
      renderChat('tutor');
    }""")
    for _ in range(30):
        if page.evaluate("() => CHAT.tutor.msgs[0].done"):
            break
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], "غلط")
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "derivTable"
    assert page.evaluate("() => CHAT.tutor.msgs[1].tableIndex") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[1].topicId") == "b3-l16"


def test_studyonly_entry_a_can_be_advanced_into_entry_b(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 0));
      renderChat('tutor');
    }""")
    assert page.evaluate("() => CHAT.tutor.msgs[0].studyOnly") == True
    assert page.locator(".msg.derivTable.studyOnly [data-deriv-continue]").count() == 1
    page.click('[data-deriv-continue][data-mi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "derivTable"
    assert page.evaluate("() => CHAT.tutor.msgs[1].tableIndex") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[1].studyOnly") == False
    # Der Weiter-Button verschwindet nach dem Klick aus dem Re-Render (m.advanced).
    assert page.locator('[data-deriv-continue]').count() == 0
    # Ein zweiter, direkter Aufruf (z. B. ein Doppel-Tap, der den alten Button noch getroffen hätte) darf
    # die Kette nicht ein zweites Mal verlängern.
    page.evaluate("() => continueDerivTable('tutor', 0)")
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
