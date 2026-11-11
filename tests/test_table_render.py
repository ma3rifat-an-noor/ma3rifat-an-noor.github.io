def test_table_starts_with_header_and_first_cell_active(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.topic = 'b2-l08'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-head").inner_text().strip() != ""
    assert page.locator(".msg.table .t-row.active input[type=text]").count() == 1
    assert page.locator(".msg.table .t-row.done").count() == 0

def test_make_table_returns_null_for_missing_topic(page, served_app):
    page.goto(served_app)
    result = page.evaluate("() => makeTable('does-not-exist', 0)")
    assert result is None
