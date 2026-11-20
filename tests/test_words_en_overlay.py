# Ridouane (2026-11-20): die heute (Buch 1-3, insgesamt 2595 Wörter) per CSV-Abgleich neu
# eingefügten Vokabeln hatten keine words_en-Übersetzung, deshalb fiel die App beim Umschalten
# auf Englisch für genau diese Wörter auf Deutsch zurück. Fix: pro betroffener Lektion wurde eine
# positionsgenaue words_en-Übersetzung ergänzt (für Lektionen ohne jede bisherige Übersetzung neu
# angelegt, mit Lücken für die unübersetzten alten Wörter; für Lektionen mit bereits vorhandener
# Teil-Übersetzung ans Ende angehängt). "(Plural: ...)"/"(weitere Form: ...)" wurden dabei zu
# "(plural: ...)"/"(also: ...)" uebersetzt, die arabische Form blieb unveraendert.
#
# Dieser Test prueft stichprobenartig je einen Fall aus allen vier heutigen Bausteinen (Buch 1,
# Buch 2, Buch 3 L1-15, Buch 3 L16-26), inklusive beider Faelle (words_en neu angelegt vs.
# bestehende Teil-Uebersetzung erweitert).
#
# Die Lektions-Kartenansicht (.t-words .chip) rendert pro Lektion nur die ersten 10 Woerter
# (renderStart() -> Math.min(10, words.length), siehe heutiger Testfehler weiter oben im
# Vokabel-Abgleich). Alle vier Testfaelle sind deshalb bewusst so gewaehlt, dass das JEWEILS
# ERSTE neue Wort noch innerhalb dieser ersten 10 Chips liegt (old_count <= 8).

def _open_settings_and_set_lang(page, lang):
    page.click("#open-settings")
    page.click(f"#set-applang button[data-applang='{lang}']")
    page.click("#close-settings")

def _chip_de_text(page, book, topic_id, index):
    page.evaluate("() => { location.hash = 'start'; }")
    page.click(f"#book-seg [data-book='{book}']")
    details = page.locator(f"[data-topic='{topic_id}']")
    if details.get_attribute("open") is None:
        details.locator("summary").click()
    page.wait_for_selector(f"[data-topic='{topic_id}'] .t-words .chip")
    chips = page.locator(f"[data-topic='{topic_id}'] .t-words .chip")
    return chips.nth(index).locator(".de-s").inner_text()

CASES = [
    # (book, topic_id, chip index of the first today's-new word, expected english text)
    (1, 'b1-l02', 6, 'Arabic (language)'),
    (2, 'b2-l08', 0, 'connection, relation (plural: عَلَاقَاتٌ)'),
    (3, 'b3-l02', 8, 'to return (also: يَرْجِعُ) / to return, come back, give back, come again, take refuge (also: رُجُوعٌ)'),
    (3, 'b3-l16', 0, 'to congratulate (II) (also: تَهْنِئَةً)'),
]

def test_todays_new_words_show_english_translation_when_lang_is_en(page, served_app):
    page.goto(served_app)
    _open_settings_and_set_lang(page, 'en')
    for book, topic_id, idx, expected_en in CASES:
        assert _chip_de_text(page, book, topic_id, idx) == expected_en, topic_id

def test_switching_back_to_german_restores_the_original_german_text(page, served_app):
    page.goto(served_app)
    _open_settings_and_set_lang(page, 'en')
    book, topic_id, idx, expected_en = CASES[1]  # b2-l08: brand-new words_en, old_count=0
    assert _chip_de_text(page, book, topic_id, idx) == expected_en
    _open_settings_and_set_lang(page, 'de')
    assert _chip_de_text(page, book, topic_id, idx) == 'Verbindung (Plural: عَلَاقَاتٌ)'
