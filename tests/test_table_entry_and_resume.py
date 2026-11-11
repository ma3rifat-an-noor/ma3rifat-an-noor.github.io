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
