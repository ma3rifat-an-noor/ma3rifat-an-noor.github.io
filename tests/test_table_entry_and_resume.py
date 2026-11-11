def test_selecting_topic_with_table_starts_table(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == True

def test_malformed_table_lesson_falls_back_to_quiz(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { TABLES['broken'] = [{verb:'x', cells:[]}]; }")
    page.evaluate("() => { practiceTopic('broken'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == False

def test_reload_resumes_table_mid_phase1(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    page.fill("#t-input-0", "ذهب")
    page.click('[data-table-submit][data-qi="0"]')
    page.reload()
    page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').pos") == 1

def test_reload_resumes_exact_shuffle_in_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    for i in range(10):
        pos = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').pos")
        step = page.evaluate(f"() => {{ const t = CHAT.tutor.msgs.find(m => m.role === 'table'); return t.steps[t.order[{pos}]]; }}")
        page.fill(f"#t-input-{pos}", step["form"])
        page.click(f'[data-table-submit][data-qi="{pos}"]')
    order_before = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').order")
    page.reload()
    page.evaluate("() => show('tutor')")
    order_after = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').order")
    assert order_before == order_after

# Regressionstest (Fix-Runde 1, Reviewer-Fund): ensureTutorQuiz() durfte für ein Typ-2-Thema NIE in die
# Typ-1-Logik (tutorQuiz()/EX) durchfallen, egal warum der Tabellen-Push-Zweig nicht greift. Vorher führte
# jeder erneute show('tutor')-Aufruf (z. B. Tab-Wechsel zurück zum Tutor, zweiter Reload) zu einer
# unbegrenzten table/quiz-Wechsel-Duplizierung: die letzte Nachricht war abwechselnd eine fremde quiz
# (von tutorQuiz()'s allgemeinem Themen-Pool-Fallback, da EX['b2-l08'] nicht existiert) und eine frische
# Tabelle - bei jedem Aufruf kam eine weitere Nachricht dazu, nie stabil. Dieser Test ruft show('tutor')
# mehrfach hintereinander auf (nach practiceTopic()) und prüft, dass sich die Nachrichtenliste nach dem
# ersten automatischen Tabellen-Push stabilisiert statt zu wachsen, und dass dabei keine weitere 'quiz'-
# Nachricht für dieses Typ-2-Thema entsteht.
def test_repeated_show_tutor_does_not_duplicate_table_or_quiz(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    lengths = []
    for _ in range(5):
        page.evaluate("() => show('tutor')")
        lengths.append(page.evaluate("() => CHAT.tutor.msgs.length"))
    # Nach dem ersten show('tutor')-Aufruf (der die Tabelle findet und nichts mehr anhängt) darf sich die
    # Länge nicht mehr verändern - kein Wachstum über die Aufrufe hinweg.
    assert lengths[0] == lengths[1] == lengths[2] == lengths[3] == lengths[4]
    table_count = page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length")
    assert table_count == 1
