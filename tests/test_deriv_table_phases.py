# Phase 1 -> Phase 2 (Zufallswiederholung) + Tabellen-Abschluss für Typ-3-Ableitungstabellen, analog zu
# tests/test_table_phases.py für Typ 2. Nutzt die reale b3-l16-Lektion, Entry B (Index 1, 6 Lückenzellen).
# Durchlaufen wird bewusst ausschließlich mit FALSCHEN Eingaben: der Phasenübergang ist davon unabhängig
# (ob eine Zelle durch "richtig im ersten Versuch" oder durch zwei Fehlversuche weiterschaltet, ist in
# submitDerivTableCell() derselbe Code-Pfad, `if (correct || m.attempt >= 2)`), und so hängt dieser Test
# nicht an den konkreten Lösungsformen der Lektion. Dass die echten Formen als richtig gewertet werden,
# deckt tests/test_deriv_table_content.py ab.
#
# Entry B verkettet nach ihrer eigenen Fertigstellung automatisch zu Entry C (Index 2, siehe
# tests/test_deriv_table_chain.py) - deshalb wird hier, wo es um Entry B SELBST geht, über
# `.first` auf das ERSTE `.msg.derivTable`-Element gescoped, damit Entry C's frisch aktive Zelle (die nach
# dem Abschluss von Entry B automatisch erscheint) die Assertions über Entry B nicht verfälscht.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _answer_wrong_twice(page, mi=0):
    step = _active_step(page, mi)
    _submit(page, mi, step["rowIdx"], step["colIdx"], "غلط1")
    _submit(page, mi, step["rowIdx"], step["colIdx"], "غلط2")


def _push_entry_b(page):
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1));
      renderChat('tutor');
    }""")


def test_phase2_starts_with_same_cell_set(page, served_app):
    page.goto(served_app)
    _push_entry_b(page)
    n = page.evaluate("() => CHAT.tutor.msgs[0].steps.length")
    assert n == 6
    for _ in range(n):
        _answer_wrong_twice(page)
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert sorted(order) == list(range(n))
    assert page.locator(".msg.derivTable").first.locator(".t-phase2-label").count() == 1


def test_deriv_table_marks_done_after_phase2(page, served_app):
    page.goto(served_app)
    _push_entry_b(page)
    n = page.evaluate("() => CHAT.tutor.msgs[0].steps.length")
    for _ in range(2 * n):
        if page.evaluate("() => CHAT.tutor.msgs[0].done"):
            break
        _answer_wrong_twice(page)
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    first = page.locator(".msg.derivTable").first
    assert first.locator(".dt-cell.active").count() == 0
    assert first.locator(".t-done").count() == 1
