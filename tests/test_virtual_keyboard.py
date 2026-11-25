# Ridouane (2026-11-25, Voice Line): Eingabe in Übersetzer/Tutor/Rollenspiel ist mit der Handy- oder
# Mac/PC-Tastatur schwierig - digitale Tastatur gewünscht, die Deutsch/Englisch/Arabisch beherrscht,
# zwischen den Sprachen umschaltbar ist, überall aufrufbar ist wo frei getippt wird, und beim Aufrufen
# die Handytastatur verschwinden lässt. Baut auf arabicKeysHTML()/inputmode="none" (siehe
# tests/test_table_input_helper.py) auf, erweitert das Prinzip aber auf die drei freien Composer-Felder
# (#tutor-input, #role-input, #tr-input) statt nur auf die Konjugationstabellen-Zellen, mit zusätzlicher
# Sprachumschaltung und einer Leertaste für Satzeingabe.
#
# Hinweis wie in tests/test_table_input_helper.py: #v-tutor/#v-rollen-play/#v-uebersetzer sind per
# `hidden`-Attribut ausgeblendet, bis die passende Ansicht aktiv ist. Jeder Test muss daher erst per
# Hash-Navigation (tutor/uebersetzer) bzw. Szenenwahl per Klick (rollen) in die richtige Ansicht
# wechseln. Zusätzlich liegen die Composer (#tutor-input/#role-input, nicht #tr-input) hinter dem
# [data-claude-ui]-Zweig, der laut applyModeUI() erst im Modus "claude" sichtbar ist (Standard ist
# "offline" - Übungsmodus ohne Composer) - jeder Tutor-/Rollenspiel-Test muss also zuerst per Klick
# in den "Frei mit Claude"-Modus wechseln.

import json


def _open_tutor(page):
    page.evaluate("() => { location.hash = 'tutor'; }")
    page.click('#v-tutor .chat-head [data-mode="claude"]')


def test_toggle_opens_panel_and_sets_inputmode_none(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    assert page.get_attribute("#tutor-input", "inputmode") is None
    page.click('[data-kb-toggle="tutor-input"]')
    assert page.is_visible("#vk-tutor .vk-keys")
    assert page.get_attribute("#tutor-input", "inputmode") == "none"
    assert page.get_attribute('[data-kb-toggle="tutor-input"]', "aria-pressed") == "true"


def test_toggle_again_closes_panel_and_restores_native_keyboard(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('[data-kb-toggle="tutor-input"]')
    assert page.locator("#vk-tutor .vk-keys").count() == 0
    assert page.get_attribute("#tutor-input", "inputmode") is None
    assert page.get_attribute('[data-kb-toggle="tutor-input"]', "aria-pressed") == "false"


def test_default_language_is_arabic_and_letter_keys_insert(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-lang") == "ar"
    page.click('#vk-tutor [data-key-insert="ذ"]')
    page.click('#vk-tutor [data-key-insert="ه"]')
    page.click('#vk-tutor [data-key-insert="ب"]')
    assert page.input_value("#tutor-input") == "ذهب"


def test_space_key_inserts_space(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.fill("#tutor-input", "ذهب")
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-insert=" "]')
    assert page.input_value("#tutor-input") == "ذهب "


def test_backspace_key_removes_last_char_in_composer(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.fill("#tutor-input", "test")
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-back]')
    assert page.input_value("#tutor-input") == "tes"


def test_arabic_tashkil_toggle_works_inside_composer_keyboard(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    assert page.locator('#vk-tutor [data-key-insert="َ"]').count() == 0
    page.click('#vk-tutor [data-key-tashkil]')
    assert page.locator('#vk-tutor [data-key-insert="َ"]').count() == 1
    page.click('#vk-tutor [data-key-insert="َ"]')
    assert page.input_value("#tutor-input") == "َ"


def test_tashkil_toggle_preserves_in_progress_input(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.fill("#tutor-input", "ذه")
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-tashkil]')
    assert page.input_value("#tutor-input") == "ذه"


def test_language_cycle_switches_letter_set_and_hides_tashkil_key(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-lang]')  # ar -> de
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-lang") == "de"
    assert page.locator('#vk-tutor [data-key-insert="q"]').count() == 1
    assert page.locator('#vk-tutor [data-key-tashkil]').count() == 0
    page.click('#vk-tutor [data-key-lang]')  # de -> en
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-lang") == "en"
    assert page.locator('#vk-tutor [data-key-insert="q"]').count() == 1
    page.click('#vk-tutor [data-key-lang]')  # en -> ar
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-lang") == "ar"
    assert page.locator('#vk-tutor [data-key-tashkil]').count() == 1


def test_language_choice_persists_in_settings_and_survives_reopen(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-lang]')  # ar -> de
    stored = json.loads(page.evaluate("() => localStorage.getItem('madina-arabisch-v1')"))
    assert stored["settings"]["kbLang"] == "de"
    page.click('[data-kb-toggle="tutor-input"]')  # schließen
    page.click('[data-kb-toggle="tutor-input"]')  # wieder öffnen
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-lang") == "de"


def test_language_choice_survives_reload(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-lang]')  # ar -> de
    page.click('#vk-tutor [data-key-lang]')  # de -> en
    page.reload()
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-lang") == "en"


def test_keyboard_available_on_roleplay_composer(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'rollen'; }")
    page.click('[data-scene="cafe"]')
    page.click('#v-rollen-play [data-mode="claude"]')
    page.click('[data-kb-toggle="role-input"]')
    assert page.is_visible("#vk-role .vk-keys")
    page.click('#vk-role [data-key-insert="ب"]')
    assert page.input_value("#role-input") == "ب"


def test_keyboard_available_on_translator(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'uebersetzer'; }")
    page.click('[data-kb-toggle="tr-input"]')
    assert page.is_visible("#vk-tr .vk-keys")
    assert page.get_attribute("#tr-input", "inputmode") == "none"
    page.click('#vk-tr [data-key-insert="ب"]')
    assert page.input_value("#tr-input") == "ب"


def test_table_cell_keyboard_untouched_by_composer_changes(page, served_app):
    # Regressionsschutz: arabicKeysHTML()/data-key-shift fuer die Konjugationstabellen-Zellen
    # darf durch die neuen composer-spezifischen Zweige (data-key-tashkil/data-key-lang) nicht
    # beeinflusst werden.
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'tutor'; CHAT.tutor.msgs.push(makeTable('b2-l08', 0)); renderChat('tutor'); }")
    assert page.locator('[data-key-lang]').count() == 0
    assert page.locator('[data-key-tashkil]').count() == 0
    page.click('[data-key-shift]')
    page.click('[data-key-insert="َ"][data-key-target="t-input-0"]')
    assert page.input_value("#t-input-0") == "َ"


# Ridouane (2026-11-25, Voice Line, zweite Runde): zwei Lücken nachgemeldet - Hamza-Formen أ/إ fehlten
# auf der Haupttastatur (sind seit Session 5 ueber die Tashkil-Taste erreichbar, hier erstmals getestet,
# siehe Handover "Keine Tests ... geschrieben"), und eine Groß-/Kleinschreibungs-Taste fuer Deutsch/
# Englisch fehlte komplett. Dieser Block deckt beides nach, plus die neue Ziffern-/Satzzeichen-Taste.


def test_hamza_alif_forms_reachable_via_tashkil_key(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-tashkil]')
    page.click('#vk-tutor [data-key-insert="أ"]')
    page.click('#vk-tutor [data-key-insert="إ"]')
    assert page.input_value("#tutor-input") == "أإ"


def test_caps_key_hidden_for_arabic_shown_for_latin(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    assert page.locator('#vk-tutor [data-key-caps]').count() == 0
    page.click('#vk-tutor [data-key-lang]')  # ar -> de
    assert page.locator('#vk-tutor [data-key-caps]').count() == 1


def test_caps_key_uppercases_german_letters_and_toggles_back(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-lang]')  # ar -> de
    page.click('#vk-tutor [data-key-insert="a"]')
    page.click('#vk-tutor [data-key-caps]')
    assert page.get_attribute('#vk-tutor [data-key-caps]', "aria-pressed") == "true"
    page.click('#vk-tutor [data-key-insert="A"]')
    page.click('#vk-tutor [data-key-caps]')
    page.click('#vk-tutor [data-key-insert="a"]')
    assert page.input_value("#tutor-input") == "aAa"


def test_caps_toggle_preserves_in_progress_input(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.fill("#tutor-input", "hi")
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-lang]')  # ar -> de
    page.click('#vk-tutor [data-key-caps]')
    assert page.input_value("#tutor-input") == "hi"


def test_punct_key_available_in_all_three_languages_and_inserts_digits_and_punctuation(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    for _ in range(3):  # ar, de, en, back to ar
        assert page.locator('#vk-tutor [data-key-punct]').count() == 1
        page.click('#vk-tutor [data-key-lang]')
    page.click('#vk-tutor [data-key-punct]')
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-punct") == "1"
    page.click('#vk-tutor [data-key-insert="7"]')
    page.click('#vk-tutor [data-key-insert="?"]')
    assert page.input_value("#tutor-input") == "7?"


def test_punct_key_hides_tashkil_and_caps_and_round_trips_back(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-punct]')
    assert page.locator('#vk-tutor [data-key-tashkil]').count() == 0
    page.click('#vk-tutor [data-key-punct]')  # back to letters
    assert page.get_attribute("#vk-tutor .vk-keys", "data-vk-punct") == "0"
    assert page.locator('#vk-tutor [data-key-tashkil]').count() == 1


def test_punct_toggle_preserves_in_progress_input(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.fill("#tutor-input", "ذه")
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-punct]')
    assert page.input_value("#tutor-input") == "ذه"


def test_arabic_specific_punctuation_reachable_via_tashkil_key(page, served_app):
    page.goto(served_app)
    _open_tutor(page)
    page.click('[data-kb-toggle="tutor-input"]')
    page.click('#vk-tutor [data-key-tashkil]')
    page.click('#vk-tutor [data-key-insert="،"]')
    page.click('#vk-tutor [data-key-insert="؛"]')
    page.click('#vk-tutor [data-key-insert="؟"]')
    assert page.input_value("#tutor-input") == "،؛؟"
