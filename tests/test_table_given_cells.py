# Ridouane (2026-11-19): Lektion 30 (ذهب im Dual) soll die komplette klassische Personenliste (13 Zellen,
# siehe buildTableSteps()) zeigen statt nur die 3 Dual-Zellen isoliert - die 10 schon aus Lektion 13
# bekannten Formen werden dabei nur ANGEZEIGT (cell.given:true in TABLES['b2-l30']), nicht erneut
# abgefragt, damit sichtbar wird, wo die beiden "هما"-Zeilen (m./f.) in der Reihenfolge einsortiert sind
# und warum sie trotz gleichem Pronomen unterschiedliche Verbformen haben. Siehe
# tests/test_table_phases.py/tests/test_table_render.py für dieselbe Testumgebungs-Voraussetzung
# (Hash-Navigation vor fill()/click()).

def test_b2_l30_shows_all_13_classical_rows(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row").count() == 13
    assert page.locator(".msg.table .t-row.given").count() == 10
    assert page.locator(".msg.table .t-row.active input[type=text]").count() == 1

def test_b2_l30_given_rows_show_form_immediately_without_input(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row.given input").count() == 0
    assert page.locator(".msg.table .t-row.given .t-form").count() == 10

def test_b2_l30_only_the_three_dual_cells_are_gradeable(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert len(order) == 3
    pronouns = page.evaluate("() => CHAT.tutor.msgs[0].order.map(idx => CHAT.tutor.msgs[0].steps[idx].pronoun)")
    assert pronouns == ['هما', 'هما', 'أنتما']

def test_b2_l30_completes_through_both_phases(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    for _ in range(6):
        if page.evaluate("() => CHAT.tutor.msgs[0].done"):
            break
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.locator(".msg.table .t-row.given").count() == 10
    assert page.locator(".msg.table .t-row.active").count() == 0
