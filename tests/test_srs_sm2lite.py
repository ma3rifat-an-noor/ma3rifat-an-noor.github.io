"""Tests für das SM-2-lite Karteikarten-Scheduling."""
import json


def _grade_first_card(page, served_app, book, topic_id, grade):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click(f"#cards-book-seg [data-book='{book}']")
    page.click(f"#cards-root [data-study='{topic_id}']")
    page.click("[data-flip]")
    page.click(f"[data-grade='{grade}']")
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    card_id = list(stored["srs"].keys())[0]
    return stored["srs"][card_id], card_id


def test_new_card_graded_easy_gets_four_day_interval(page, served_app):
    c, _ = _grade_first_card(page, served_app, 1, 'b1-l05', 2)
    assert c["ivl"] == 4
    assert c["ease"] == 2.65
    assert c["b"] == 2


def test_new_card_graded_hard_gets_one_day_interval(page, served_app):
    c, _ = _grade_first_card(page, served_app, 1, 'b1-l06', 1)
    assert c["ivl"] == 1
    assert c["ease"] == 2.35
    assert c["b"] == 2


def test_new_card_graded_wrong_is_due_immediately(page, served_app):
    c, _ = _grade_first_card(page, served_app, 1, 'b1-l07', 0)
    assert c["ivl"] == 0
    assert c["ease"] == 2.3
    assert c["b"] == 1


def test_three_grade_buttons_are_present_with_correct_labels(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='1']")
    page.click("#cards-root [data-study='b1-l08']")
    page.click("[data-flip]")
    buttons = page.locator(".fc-actions button")
    assert buttons.count() == 3
    assert buttons.nth(0).inner_text().strip() == "Nicht gewusst"
    assert buttons.nth(1).inner_text().strip() == "Schwer gewusst"
    assert buttons.nth(2).inner_text().strip() == "Leicht gewusst"
