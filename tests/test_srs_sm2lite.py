"""Tests für das SM-2-lite Karteikarten-Scheduling."""
import json

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _mock_correction_reply(route, wrong, correct, correct_de):
    route.fulfill(status=200, content_type="application/json", body=json.dumps({"content": [{"type": "text", "text": json.dumps({
        "reply": "تمام", "translation": "Okay", "translit": "tamam", "tip": "",
        "correction": {"wrong": wrong, "correct": correct, "correct_de": correct_de, "explanation": ""}})}]}))


def _enable_claude_mode(page):
    page.click("#open-settings")
    page.fill("#set-byok", "sk-ant-test")
    page.dispatch_event("#set-byok", "change")
    page.uncheck("#set-spar")
    page.click("#close-settings")


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


def _force_due_and_regrade(page, served_app, book, topic_id, card_id, grade):
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    stored["srs"][card_id]["d"] = 0
    page.evaluate("(v) => localStorage.setItem('madina-arabisch-v1', JSON.stringify(v))", stored)
    page.reload()
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click(f"#cards-book-seg [data-book='{book}']")
    page.click(f"#cards-root [data-study='{topic_id}']")
    page.click("[data-flip]")
    page.click(f"[data-grade='{grade}']")
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    return stored["srs"][card_id]


def test_interval_soft_caps_at_180_days_and_stays_there(page, served_app):
    c, card_id = _grade_first_card(page, served_app, 1, 'b1-l09', 2)  # ivl=4, ease=2.65
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l09', card_id, 2)  # ivl=11, ease=2.80
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l09', card_id, 2)  # ivl=32, ease=2.95
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l09', card_id, 2)  # ivl=96, ease=3.00
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l09', card_id, 2)
    assert c["ivl"] == 180
    assert c["ease"] == 3.0
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l09', card_id, 2)  # ein weiterer Zyklus
    assert c["ivl"] == 180  # bleibt am Cap, läuft nicht weiter


def test_ease_floors_at_1_3_after_repeated_wrong_answers(page, served_app):
    c, card_id = _grade_first_card(page, served_app, 1, 'b1-l10', 0)  # ease=2.3
    for _ in range(5):  # -0.2 je Mal: 2.1, 1.9, 1.7, 1.5, 1.3
        c = _force_due_and_regrade(page, served_app, 1, 'b1-l10', card_id, 0)
    assert c["ease"] == 1.3
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l10', card_id, 0)
    assert c["ease"] == 1.3  # bleibt am Boden


def test_existing_card_graded_hard_grows_interval_by_1_2x(page, served_app):
    c, card_id = _grade_first_card(page, served_app, 1, 'b1-l11', 2)  # ivl=4, ease=2.65
    c = _force_due_and_regrade(page, served_app, 1, 'b1-l11', card_id, 1)  # hard regrade of an existing card
    assert c["ivl"] == 5  # max(1, round(4 * 1.2))
    assert c["ease"] == 2.5  # 2.65 - 0.15


def test_an_intervening_wrong_answer_resets_the_consecutive_correct_counter(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='1']")
    page.click("#cards-root [data-study='b1-l21']")
    page.click("[data-flip]")
    page.click("[data-grade='0']")  # falsch -> in den Fehler-Stapel, s=0
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    card_id = list(stored["srs"].keys())[0]

    _force_due_and_regrade(page, served_app, 1, 'b1-l21', card_id, 1)  # s=1
    _force_due_and_regrade(page, served_app, 1, 'b1-l21', card_id, 0)  # wrong again -> s resets to 0
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert card_id in stored["mistakes"]

    _force_due_and_regrade(page, served_app, 1, 'b1-l21', card_id, 2)  # s=1 (1st correct since the reset)
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert card_id in stored["mistakes"]  # one correct after the reset is not enough

    _force_due_and_regrade(page, served_app, 1, 'b1-l21', card_id, 1)  # s=2 (2nd consecutive correct)
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert card_id not in stored["mistakes"]


def test_mistake_pile_needs_two_consecutive_correct_regardless_of_hard_or_easy(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='1']")
    page.click("#cards-root [data-study='b1-l12']")
    page.click("[data-flip]")
    page.click("[data-grade='0']")  # falsch -> in den Fehler-Stapel
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    card_id = list(stored["srs"].keys())[0]
    assert card_id in stored["mistakes"]

    c = _force_due_and_regrade(page, served_app, 1, 'b1-l12', card_id, 1)  # 1x schwer richtig
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert card_id in stored["mistakes"]  # noch nicht raus

    c = _force_due_and_regrade(page, served_app, 1, 'b1-l12', card_id, 2)  # 2. Mal richtig (leicht)
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert card_id not in stored["mistakes"]  # jetzt raus


def _grade_first_card_by_key(page, served_app, book, topic_id, key):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click(f"#cards-book-seg [data-book='{book}']")
    page.click(f"#cards-root [data-study='{topic_id}']")
    page.click("[data-flip]")
    page.keyboard.press(key)
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    card_id = list(stored["srs"].keys())[0]
    return stored["srs"][card_id]


def test_keyboard_shortcut_1_grades_not_known(page, served_app):
    c = _grade_first_card_by_key(page, served_app, 1, 'b1-l14', '1')
    assert c["ivl"] == 0 and c["ease"] == 2.3


def test_keyboard_shortcut_arrowleft_grades_not_known(page, served_app):
    c = _grade_first_card_by_key(page, served_app, 1, 'b1-l15', 'ArrowLeft')
    assert c["ivl"] == 0 and c["ease"] == 2.3


def test_keyboard_shortcut_2_grades_hard(page, served_app):
    c = _grade_first_card_by_key(page, served_app, 1, 'b1-l16', '2')
    assert c["ivl"] == 1 and c["ease"] == 2.35


def test_keyboard_shortcut_3_grades_easy(page, served_app):
    c = _grade_first_card_by_key(page, served_app, 1, 'b1-l17', '3')
    assert c["ivl"] == 4 and c["ease"] == 2.65


def test_keyboard_shortcut_arrowright_grades_easy(page, served_app):
    c = _grade_first_card_by_key(page, served_app, 1, 'b1-l19', 'ArrowRight')
    assert c["ivl"] == 4 and c["ease"] == 2.65


def test_not_known_button_spans_full_width_above_hard_and_easy(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='1']")
    page.click("#cards-root [data-study='b1-l20']")
    page.click("[data-flip]")
    b0, b1, b2 = [page.locator(".fc-actions button").nth(i).bounding_box() for i in range(3)]
    assert b0["y"] < b1["y"] and b0["y"] < b2["y"]  # "Nicht gewusst" sits in its own row above the other two
    assert abs(b1["y"] - b2["y"]) < 2  # "Schwer"/"Leicht" share a row
    assert b1["x"] != b2["x"]  # ...side by side, not stacked


def test_tutor_correction_preserves_and_penalizes_existing_ease_and_interval(page, served_app):
    page.goto(served_app)
    page.route(ANTHROPIC_URL, lambda route: _mock_correction_reply(route, "احمد", "أحمد", "Ahmad (Name)"))
    _enable_claude_mode(page)
    page.evaluate("() => { location.hash = 'tutor'; }")
    page.fill("#tutor-input", "اسمي احمد")
    page.click("#tutor-send")
    page.wait_for_function("() => CHAT.tutor.msgs.some(m => m.role === 'tutor')")
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    card_id = list(stored["srs"].keys())[0]
    assert stored["srs"][card_id]["ivl"] == 0
    assert stored["srs"][card_id]["ease"] == 2.3  # EASE_START - 0.2, same shape grade(id, 0) produces

    # Simulate this custom card later reaching a well-known state via normal flashcard grading...
    stored["srs"][card_id] = {"b": 5, "d": 0, "w": 1, "r": 5, "s": 5, "ivl": 90, "ease": 2.0}
    page.evaluate("(v) => localStorage.setItem('madina-arabisch-v1', JSON.stringify(v))", stored)
    page.reload()

    # ...then fail the same correction again: progress must be penalized, not wiped back to defaults.
    page.evaluate("() => { location.hash = 'tutor'; }")
    page.fill("#tutor-input", "اسمي احمد")
    page.click("#tutor-send")
    page.wait_for_function("() => CHAT.tutor.msgs.some(m => m.role === 'tutor')")  # chat history is ephemeral, resets on reload
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert stored["srs"][card_id]["ivl"] == 0
    assert stored["srs"][card_id]["ease"] == 1.8  # 2.0 - 0.2, preserved then penalized, not reset to EASE_START
    assert stored["srs"][card_id]["w"] == 2


def test_wrong_answer_reappears_within_the_same_session(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='1']")
    page.click("#cards-root [data-study='b1-l13']")
    page.click("[data-flip]")
    front_ar = page.locator(".fc-big-ar").inner_text()
    page.click("[data-grade='0']")
    seen_again = False
    for _ in range(4):
        page.click("[data-flip]")
        if page.locator(".fc-big-ar").inner_text() == front_ar:
            seen_again = True
            break
        page.click("[data-grade='2']")  # andere Karten weiter durchklicken
    assert seen_again
