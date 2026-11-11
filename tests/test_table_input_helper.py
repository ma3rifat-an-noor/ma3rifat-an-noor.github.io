# Hinweis: #v-tutor ist per `hidden`-Attribut ausgeblendet, solange currentView != 'tutor'. Playwrights
# fill()/click() verlangen ein sichtbares Element, daher muss jeder Test erst per Hash-Navigation (triggert
# den bestehenden hashchange->route()->show('tutor')-Pfad) in die Tutor-Ansicht wechseln, bevor er die
# Tabellennachricht einfügt und rendert. Reine Testumgebungs-Voraussetzung (wie in tests/test_table_submit.py
# und tests/test_table_phases.py), keine Änderung an den in der Aufgabenbeschreibung vorgegebenen
# Assertions/Funktionsaufrufen.

def test_virtual_keys_append_to_input(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.click('[data-key-insert="ذ"][data-key-target="t-input-0"]')
    page.click('[data-key-insert="ه"][data-key-target="t-input-0"]')
    page.click('[data-key-insert="ب"][data-key-target="t-input-0"]')
    assert page.input_value("#t-input-0") == "ذهب"

def test_backspace_key_removes_last_char(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهبx")
    page.click('[data-key-back="t-input-0"]')
    assert page.input_value("#t-input-0") == "ذهب"

def test_submit_via_helper_typed_value_is_graded(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    for ch in "ذهب":
        page.click(f'[data-key-insert="{ch}"][data-key-target="t-input-0"]')
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
