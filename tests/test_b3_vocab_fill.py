# Ridouane (2026-11-20): Buch 3, Lektionen 16-26 (die Verbform-Ableitungslektionen) hatten bisher 0
# Vokabelwörter in TOPICS - nur die Ableitungstabelle selbst war Inhalt. Ridouanes eigene
# Quizlet-Vokabelsammlung (CSV-Export) liefert dafür hunderte Einträge pro Lektion. Lektion 18 hatte
# bereits 7 eigene Wörter und bleibt unberührt (Scope war ausdrücklich nur die leeren Lektionen).
# Zusammengesetzte CSV-Einträge (Verb+Verbalnomen, Nomen+Plural) werden auf die Hauptform reduziert,
# die Zusatzform als Anmerkung ans Deutsche angehängt (Ridouane: "passt das so" + "ok verstanden, dann
# passt das so" zur Variante mit weggelassener Zweitform bei den 13 unvokalisierten Fällen).
#
# const TOPICS/TOPIC_CARDS sind top-level lexikalische Bindings und daher für page.evaluate() nicht
# sichtbar (anders als CHAT, das sich per `window.CHAT = CHAT` selbst exponiert) - deshalb prüfen diese
# Tests ausschließlich über das sichtbare DOM (Karteikarten-Stapelliste, Buch-Tab-Chips, Lernkarten-Flip),
# genau wie der Rest der Testsuite.

import re

EXPECTED_COUNTS = {
    'b3-l16': 117, 'b3-l17': 135, 'b3-l19': 107, 'b3-l20': 47,
    'b3-l21': 114, 'b3-l22': 50, 'b3-l23': 77, 'b3-l24': 43,
    'b3-l25': 69, 'b3-l26': 66,
}

def _goto_cards_book3(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='3']")

def _deck_card_count(page, topic_id):
    text = page.inner_text(f"[data-study='{topic_id}'] .d-meta")
    return int(re.match(r'(\d+)', text).group(1))

def test_previously_empty_b3_lessons_now_have_words(page, served_app):
    _goto_cards_book3(page, served_app)
    for topic_id, expected in EXPECTED_COUNTS.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b3_l18_is_untouched(page, served_app):
    _goto_cards_book3(page, served_app)
    assert _deck_card_count(page, 'b3-l18') == 7

def test_b3_l16_word_chips_render_with_content_in_bucher_tab(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'buecher'; }")
    page.click("#book-seg [data-book='3']")
    page.click("text=بَابُ فَعَّلَ")
    page.wait_for_selector("[data-topic='b3-l16'] .t-words .chip")
    chips = page.locator("[data-topic='b3-l16'] .t-words .chip")
    assert chips.count() == 10
    for i in range(10):
        ar = chips.nth(i).locator(".ar-s").inner_text()
        de = chips.nth(i).locator(".de-s").inner_text()
        assert ar.strip() and de.strip()

def test_hamza_initial_form_iv_verb_lands_with_correct_transliteration(page, served_app):
    # Regression guard: die CSV speicherte Hamza-Buchstaben teils zerlegt (ALEF + COMBINING HAMZA ABOVE
    # statt dem zusammengesetzten Zeichen) - ohne NFC-Normalisierung landete das rohe Diakritikum
    # wörtlich in der Umschrift. b3-l17s allererstes Wort (أَصْبَحَ) ist genau so ein Fall.
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='3']")
    page.click("[data-study='b3-l17']")
    page.click("#fc")
    ar = page.inner_text(".fc-big-ar")
    tl = page.inner_text(".fc-tl")
    assert ar == 'أَصْبَحَ'
    assert tl == 'aṣbaḥa'
    assert 'ٔ' not in tl and 'أ' not in tl and 'إ' not in tl
