# Hinweis: #v-tutor ist per `hidden`-Attribut ausgeblendet, solange currentView != 'tutor'. Playwrights
# fill()/click() verlangen ein sichtbares Element, daher muss jeder Test erst per Hash-Navigation (triggert
# den bestehenden hashchange->route()->show('tutor')-Pfad) in die Tutor-Ansicht wechseln, bevor er die
# Tabellennachricht einfügt und rendert. Reine Testumgebungs-Voraussetzung (wie in tests/test_table_submit.py),
# keine Änderung an den in der Aufgabenbeschreibung vorgegebenen Assertions/Funktionsaufrufen.

def _answer_all_phase1(page):
    for i in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill(f"#t-input-{pos}", step["form"])
        page.click(f'[data-table-submit][data-qi="{pos}"]')

def test_phase2_starts_with_same_cell_set(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    _answer_all_phase1(page)
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert sorted(order) == list(range(10))

def test_table_marks_done_after_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    _answer_all_phase1(page)
    for _ in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        if page.evaluate("() => CHAT.tutor.msgs[0].done"): break
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill(f"#t-input-{pos}", step["form"])
        page.click(f'[data-table-submit][data-qi="{pos}"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.locator(".msg.table .t-row.active").count() == 0
