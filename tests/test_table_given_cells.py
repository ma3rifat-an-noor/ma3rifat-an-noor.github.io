# Ridouane (2026-11-19): Lektion 30 (ذهب im Dual) soll die komplette klassische Personenliste zeigen statt
# nur die Dual-Zellen isoliert - die 10 schon aus Lektion 13 bekannten Formen werden dabei nur ANGEZEIGT
# (cell.given:true in TABLES['b2-l30']), nicht erneut abgefragt, damit sichtbar wird, wo die "هما"-Zeilen
# (m./f.) in der Reihenfolge einsortiert sind und warum sie trotz gleichem Pronomen unterschiedliche
# Verbformen haben. Siehe tests/test_table_phases.py/tests/test_table_render.py für dieselbe
# Testumgebungs-Voraussetzung (Hash-Navigation vor fill()/click()).
#
# Ridouane (2026-11-20): die Anrede-Dualform (أنتما) bekommt jetzt zusätzlich eine zweite, eigene Zeile im
# weiblichen Block (buildTableSteps() hat dafür 2,m,du UND 2,f,du statt eines gemeinsamen Platzes) -
# dieselbe Form wie die männliche Anrede-Dualzeile, aber als eigene Zelle, damit die Parallelität zur
# 3. Person (die ja ebenfalls je eine m./f.-Dualzeile hat) sichtbar bleibt. Macht aus den bisherigen 13
# Zeilen/3 abfragbaren Zellen jetzt 14 Zeilen/4 abfragbare Zellen.

def test_b2_l30_shows_all_14_classical_rows(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row").count() == 14
    assert page.locator(".msg.table .t-row.given").count() == 10
    assert page.locator(".msg.table .t-row.active input[type=text]").count() == 1

def test_b2_l30_given_rows_show_form_immediately_without_input(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row.given input").count() == 0
    assert page.locator(".msg.table .t-row.given .t-form").count() == 10

def test_b2_l30_four_dual_cells_are_gradeable(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert len(order) == 4
    cells = page.evaluate("() => CHAT.tutor.msgs[0].order.map(idx => { const s = CHAT.tutor.msgs[0].steps[idx]; return [s.pronoun, s.gender]; })")
    assert cells == [['هما', 'm'], ['هما', 'f'], ['أنتما', 'm'], ['أنتما', 'f']]

def test_b2_l30_completes_through_both_phases(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l30', 0)); renderChat('tutor'); }")
    for _ in range(8):
        if page.evaluate("() => CHAT.tutor.msgs[0].done"):
            break
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.locator(".msg.table .t-row.given").count() == 10
    assert page.locator(".msg.table .t-row.active").count() == 0

# Ridouane (2026-11-20): Lektion 8 (Vergangenheit) und 13 (Präsens) sollen die Dualformen auch schon zeigen
# - vier given:true-Zellen (3m/3f/2m/2f-du), rein zur Ansicht, nicht abgefragt (der Dual wird inhaltlich
# erst in Lektion 30 eingeführt). Lektion 13 übernimmt dafür wortgleich die schon geprüften
# Präsens-Dualformen aus Lektion 30; Lektion 8 bekommt die bisher nirgends vorhandenen, regulär
# hergeleiteten Vergangenheits-Dualformen (ذَهَبَا/ذَهَبَتَا/ذَهَبْتُمَا).

def test_b2_l13_shows_dual_rows_as_given_context(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l13', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row").count() == 14
    assert page.locator(".msg.table .t-row.given").count() == 4
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert len(order) == 10
    dual_forms = page.evaluate("() => CHAT.tutor.msgs[0].steps.filter(s => s.num === 'du').map(s => s.form)")
    assert dual_forms == ['يَذْهَبَانِ', 'تَذْهَبَانِ', 'تَذْهَبَانِ', 'تَذْهَبَانِ']

def test_b2_l08_shows_dual_rows_as_given_context(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row").count() == 14
    assert page.locator(".msg.table .t-row.given").count() == 4
    order = page.evaluate("() => CHAT.tutor.msgs[0].order")
    assert len(order) == 10
    dual_forms = page.evaluate("() => CHAT.tutor.msgs[0].steps.filter(s => s.num === 'du').map(s => s.form)")
    assert dual_forms == ['ذَهَبَا', 'ذَهَبَتَا', 'ذَهَبْتُمَا', 'ذَهَبْتُمَا']

def test_b2_l08_dual_given_rows_have_no_input(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-row.given input").count() == 0
    assert page.locator(".msg.table .t-row.given .t-form").count() == 4
