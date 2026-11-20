# Hinweis: #v-tutor ist per `hidden`-Attribut ausgeblendet, solange currentView != 'tutor'. Playwrights
# fill()/click() verlangen ein sichtbares Element, daher muss jeder Test erst per Hash-Navigation (triggert
# den bestehenden hashchange->route()->show('tutor')-Pfad) in die Tutor-Ansicht wechseln, bevor er die
# Tabellennachricht einfügt und rendert. Reine Testumgebungs-Voraussetzung (wie in tests/test_table_submit.py),
# keine Änderung an den in der Aufgabenbeschreibung vorgegebenen Assertions/Funktionsaufrufen.

def _answer_all_phase1(page):
    for i in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')

def test_phase2_starts_with_same_cell_set(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    # Erwartete Zell-Indizes dynamisch ermitteln statt range(10) hart zu kodieren: b2-l08 zeigt seit
    # 2026-11-20 zusätzlich 4 given-Zellen (Dual-Formen nur zur Ansicht), die NIE abgefragt werden und
    # darum die Indizes der 10 echten Phase-1-Zellen in m.steps auseinanderreißen (nicht mehr 0..9 lückenlos).
    expected = page.evaluate("() => CHAT.tutor.msgs[0].steps.map((s, i) => i).filter(i => !CHAT.tutor.msgs[0].steps[i].given)")
    _answer_all_phase1(page)
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert sorted(order) == expected

# Ridouane (2026-11-19): die Personen-Reihenfolge soll in Phase 2 drillbar bleiben - also exakt dieselbe
# klassische Reihenfolge wie Phase 1 (3. Pers. m -> f -> Anrede -> 1. Pers.), nicht zufällig gemischt.
def test_phase2_keeps_same_classical_order_as_phase1(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    expected = page.evaluate("() => CHAT.tutor.msgs[0].order")
    _answer_all_phase1(page)
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert order == expected

def test_table_marks_done_after_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    _answer_all_phase1(page)
    for _ in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        if page.evaluate("() => CHAT.tutor.msgs[0].done"): break
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.locator(".msg.table .t-row.active").count() == 0
