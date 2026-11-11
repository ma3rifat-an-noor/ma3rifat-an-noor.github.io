# Hinweis: #v-tutor ist per `hidden`-Attribut ausgeblendet, solange currentView != 'tutor'. Playwrights
# fill()/click() verlangen ein sichtbares Element, daher muss jeder Test erst per Hash-Navigation (triggert
# den bestehenden hashchange->route()->show('tutor')-Pfad) in die Tutor-Ansicht wechseln, bevor er die
# Tabellennachricht einfügt und rendert. Reine Testumgebungs-Voraussetzung, keine Änderung an den in der
# Aufgabenbeschreibung vorgegebenen Assertions/Funktionsaufrufen.

def test_correct_answer_advances(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهب")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0

def test_norm_variant_spelling_counts_as_correct(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", " ذهب ")  # abweichend: Leerzeichen
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1

def test_wrong_once_does_not_advance(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "قرأ")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 1

def test_wrong_twice_reveals_and_advances(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "قرأ"); page.click('[data-table-submit][data-qi="0"]')
    page.fill("#t-input-0", "كتب"); page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == False

def test_empty_submit_does_not_consume_attempt(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "   ")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0

def test_double_submit_after_answered_is_noop(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهب"); page.click('[data-table-submit][data-qi="0"]')
    page.evaluate("() => submitTableCell('tutor', 0, 'ذهب')")  # Zelle 0 ist schon fertig, Zelle 1 ist jetzt aktiv
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1  # unverändert, kein zweiter Advance durch den alten Aufruf
