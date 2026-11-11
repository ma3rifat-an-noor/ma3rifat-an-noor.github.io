# Hinweis: #v-tutor ist per `hidden`-Attribut ausgeblendet, solange currentView != 'tutor'. Playwrights
# fill()/click() verlangen ein sichtbares Element, daher muss jeder Test erst per Hash-Navigation (triggert
# den bestehenden hashchange->route()->show('tutor')-Pfad) in die Tutor-Ansicht wechseln, bevor er die
# Tabellennachricht einfügt und rendert. Reine Testumgebungs-Voraussetzung, keine Änderung an den in der
# Aufgabenbeschreibung vorgegebenen Assertions/Funktionsaufrufen.
#
# Adressierung (Abschluss-Review, Finding 1/4): Eingabefeld-Id und data-qi tragen den INDEX DER NACHRICHT
# in CHAT.tutor.msgs, nicht mehr den Zell-Cursor m.pos. In dieser Datei liegt die Tabelle immer auf
# msgs[0], deshalb sind "#t-input-0" und [data-qi="0"] über alle Zellen und Phasen hinweg konstant.

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

# Doppeltes Absenden (Doppel-Tap auf den Senden-Knopf) darf eine Zelle nicht zweimal werten / zweimal
# weiterschalten. Geprüft wird hier der echte UI-Weg, nicht ein direkter Funktionsaufruf: der erste Klick
# wertet und rendert den Chat neu, wodurch das Eingabefeld der nächsten Zelle leer ist; der zweite Klick
# landet damit auf einem leeren Submit, der laut test_empty_submit_does_not_consume_attempt ein No-Op ist.
def test_double_submit_after_answered_is_noop(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    page.fill("#t-input-0", "ذهب")
    page.click('[data-table-submit][data-qi="0"]')
    page.click('[data-table-submit][data-qi="0"]')  # zweiter Tap unmittelbar danach
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1  # nur ein Advance
    assert page.evaluate("() => CHAT.tutor.msgs[0].attempt") == 0  # kein verbrauchter Versuch auf Zelle 2


# Regressionstest zum Abschluss-Review (Finding 1c/4): Zwei gleichzeitig offene Typ-2-Tabellen
# VERSCHIEDENER Themen. Vorher trugen beide aktiven Eingabefelder dieselbe DOM-Id (t-input-<m.pos>, also
# bei zwei frischen Tabellen beide "t-input-0"), und submitTableCell() suchte seine Nachricht über
# ctx.msgs.filter(role==='table').pop() - die ZULETZT angehängte. Ein Klick in die obere Tabelle las
# deshalb das falsche Eingabefeld aus und wertete gegen die falsche Nachricht. Jetzt tragen Id und data-qi
# den Nachrichten-Index, beide Felder sind eindeutig und jeder Klick wertet genau seine eigene Tabelle.
def _push_two_tables(page):
    page.evaluate("""() => {
      location.hash = 'tutor';
      TABLES['probe-x'] = [{verb:'س', tense:'madi', de:'Probe X', cells:[
        {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'س1'},
        {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'س2'}]}];
      TABLES['probe-y'] = [{verb:'ص', tense:'madi', de:'Probe Y', cells:[
        {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'ص1'},
        {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'ص2'}]}];
      CHAT.tutor.msgs = [makeTable('probe-x', 0), makeTable('probe-y', 0)];
      renderChat('tutor');
    }""")


def test_two_open_tables_have_distinct_input_ids(page, served_app):
    page.goto(served_app)
    _push_two_tables(page)
    ids = page.evaluate("() => [...document.querySelectorAll('.msg.table .t-row.active input')].map(e => e.id)")
    assert len(ids) == 2
    assert len(set(ids)) == 2, f"DOM-Id-Kollision zwischen zwei Tabellen: {ids}"


def test_submit_grades_the_table_that_was_typed_into(page, served_app):
    page.goto(served_app)
    _push_two_tables(page)
    # In die ERSTE (obere) Tabelle tippen und deren Senden-Knopf drücken.
    page.fill("#t-input-0", "س1")
    page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1  # Tabelle 1 gewertet
    assert page.evaluate("() => CHAT.tutor.msgs[1].pos") == 0  # Tabelle 2 unberührt
    # Und umgekehrt: in die ZWEITE Tabelle tippen.
    page.fill("#t-input-1", "ص1")
    page.click('[data-table-submit][data-qi="1"]')
    assert page.evaluate("() => CHAT.tutor.msgs[1].pos") == 1
    assert page.evaluate("() => CHAT.tutor.msgs[1].answers['0'].correct") == True
