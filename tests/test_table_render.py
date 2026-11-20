def test_table_starts_with_header_and_first_cell_active(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { CHAT.tutor.topic = 'b2-l08'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    assert page.locator(".msg.table .t-head").inner_text().strip() != ""
    assert page.locator(".msg.table .t-row.active input[type=text]").count() == 1
    # b2-l08 zeigt seit 2026-11-20 die Dual-Formen als given-Kontext (siehe test_table_given_cells.py) -
    # die sind von Anfang an "done", aber keine ECHTE Antwort wurde abgegeben, darum hier ausgeschlossen.
    assert page.locator(".msg.table .t-row.done:not(.given)").count() == 0
    # Regression: das Eingabefeld muss inputmode="none" tragen, damit auf Touch-Geräten nur die
    # eigene arabicKeysHTML()-Tastatur erscheint und nicht zusätzlich die native OS-Tastatur.
    assert page.locator(".msg.table .t-row.active input[type=text]").get_attribute("inputmode") == "none"

def test_make_table_returns_null_for_missing_topic(page, served_app):
    page.goto(served_app)
    result = page.evaluate("() => makeTable('does-not-exist', 0)")
    assert result is None
