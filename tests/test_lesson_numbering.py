# tests/test_lesson_numbering.py

def test_tutor_topic_dropdown_book2_is_in_ascending_lesson_order(page, served_app):
    page.goto(served_app)
    values = page.eval_on_selector_all(
        "#tutor-topic optgroup:nth-of-type(2) option",
        "els => els.map(e => e.value)",
    )
    nums = [int(v.split('-l')[1]) for v in values]
    assert nums == sorted(nums)
    assert nums[0] == 1
    assert nums[-1] == 31

def test_tutor_topic_dropdown_book1_and_book3_stay_in_order(page, served_app):
    page.goto(served_app)
    b1 = page.eval_on_selector_all("#tutor-topic optgroup:nth-of-type(1) option", "els => els.map(e => e.value)")
    b3 = page.eval_on_selector_all("#tutor-topic optgroup:nth-of-type(3) option", "els => els.map(e => e.value)")
    nums1 = [int(v.split('-l')[1]) for v in b1]
    assert nums1 == sorted(nums1)
    # book 3 has non-numbered appendix entries (anhang1/anhang2/tamarin-amma) at the end
    nums3 = [int(v.split('-l')[1]) for v in b3 if '-l' in v and v.split('-l')[1].isdigit()]
    assert nums3 == sorted(nums3)
    assert b3[-1] in ('b3-anhang1', 'b3-anhang2', 'b3-tamarin-amma') or nums3[-1] == 34

def test_home_topic_list_shows_lesson_number_for_book1(page, served_app):
    page.goto(served_app)
    text = page.inner_text("#start-books")
    assert "Lektion 1 · " in text

def test_home_topic_list_shows_lesson_number_for_book2_in_order(page, served_app):
    page.goto(served_app)
    page.click("#book-seg [data-book='2']")
    text = page.inner_text("#start-books")
    assert "Lektion 1 · " in text
    pos1 = text.index("Lektion 1 · ")
    pos2 = text.index("Lektion 2 · ")
    assert pos1 < pos2

def test_book3_lesson_label_is_not_duplicated(page, served_app):
    page.goto(served_app)
    page.click("#book-seg [data-book='3']")
    text = page.inner_text("#start-books")
    assert "Lektion 1 · " in text
    assert "Lektion 1 · Lektion 1:" not in text
    assert "Lektion 1: Deklinierbar" not in text

def test_next_up_suggests_book2_lesson1_first(page, served_app):
    page.goto(served_app)
    page.click("#book-seg [data-book='2']")
    text = page.inner_text("#start-next")
    assert "Lektion 1 · " in text

def test_flashcards_deck_list_shows_lesson_number(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    text = page.inner_text("#cards-root")
    assert "Lektion 1 · " in text

def test_tutor_new_topic_note_shows_lesson_number(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; }")
    page.select_option("#tutor-topic", "b1-l05")
    page.wait_for_selector("p.note")
    text = page.inner_text("p.note")
    assert "Lektion 5 · " in text
