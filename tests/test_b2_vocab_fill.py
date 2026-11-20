# Ridouane (2026-11-20): dritter Schritt des Quizlet-Vokabel-Abgleichs - Buch 2 (Lektionen
# 1-11, 13-27; Lektion 12 und 28-31 hatten keine CSV-Lücken). Gleiche Zusammengesetzte-Formen-
# Policy wie bei Buch 3 (Hauptform + "Plural: ..."/"weitere Form: ..."-Anmerkung, unvokalisierte
# Zusatzformen weggelassen), plus drei CSV-Einträge, die eine Lektionsspanne statt einer
# einzelnen Lektion trugen ("8-9", "22-23", "24-25") - auf Ridouanes "ja passt" hin per Position
# in der Mitte auf die beiden Lektionen aufgeteilt.
#
# Zwei echte Fehler beim sorgfältigen Durchlesen der gebauten Liste gefunden und behoben:
# - translit.py-Bug: مِائَةٌ ("hundert") hat einen rein orthographischen, stummen Alif vor dem
#   Hamza-auf-Yā (ئ) - der Konverter liest ihn fälschlich als Langvokal und haengt ein
#   ueberfluessiges "ā" an ("miāʾatun" statt "miʾatun"). Nur fuer dieses eine, bekannt
#   irregulaer geschriebene Wort per Override korrigiert statt den allgemeinen Konverter
#   anzufassen.
# - Echter CSV-Tippfehler: "ذُّبَابٌ" (Fliege) hatte einen ueberfluessigen Shadda auf dem ersten
#   Buchstaben, korrekt ist ذُبَابٌ (dhubābun).

import re

EXPECTED_COUNTS = {
    'b2-l01': 16, 'b2-l02': 7, 'b2-l03': 14, 'b2-l04': 8, 'b2-l05': 24,
    'b2-l06': 18, 'b2-l07': 27, 'b2-l08': 12, 'b2-l09': 17, 'b2-l10': 31,
    'b2-l11': 20, 'b2-l13': 3, 'b2-l14': 29, 'b2-l15': 7, 'b2-l16': 18,
    'b2-l17': 24, 'b2-l18': 8, 'b2-l19': 18, 'b2-l20': 12, 'b2-l21': 13,
    'b2-l22': 5, 'b2-l23': 4, 'b2-l24': 4, 'b2-l25': 9, 'b2-l26': 63,
    'b2-l27': 49,
}

def _goto_cards_book2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='2']")

def _deck_card_count(page, topic_id):
    text = page.inner_text(f"[data-study='{topic_id}'] .d-meta")
    return int(re.match(r'(\d+)', text).group(1))

def test_b2_lessons_gained_the_csv_words(page, served_app):
    _goto_cards_book2(page, served_app)
    for topic_id, expected in EXPECTED_COUNTS.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b2_untouched_lessons_kept_their_original_counts(page, served_app):
    # Regression guard: lesson 12 and 28-31 had no CSV gaps and must stay exactly as before.
    _goto_cards_book2(page, served_app)
    untouched = {'b2-l12': 10, 'b2-l28': 0, 'b2-l29': 0, 'b2-l30': 0, 'b2-l31': 3}
    for topic_id, expected in untouched.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b2_word_chips_render_scoped_to_its_own_topic(page, served_app):
    # Same page-wide-selector regression guard as the Buch-3 build: the Buecher-tab start page
    # renders every book-2 topic's word chips at once (capped at 10 each), so the selector must
    # stay scoped to the clicked topic's own <details data-topic="..."> element.
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'start'; }")
    page.click("#book-seg [data-book='2']")
    page.click("[data-topic='b2-l05'] summary")
    page.wait_for_selector("[data-topic='b2-l05'] .t-words .chip")
    chips = page.locator("[data-topic='b2-l05'] .t-words .chip")
    assert chips.count() == 10
    for i in range(10):
        ar = chips.nth(i).locator(".ar-s").inner_text()
        de = chips.nth(i).locator(".de-s").inner_text()
        assert ar.strip() and de.strip()

# Direct TOPICS-data regression checks (same technique as the Buch-3 build): a study session
# only samples up to 8 random "fresh" cards per topic, so a specific word cannot be reached
# reliably by clicking through the UI.

import json
import pathlib
import subprocess

APP_HTML = pathlib.Path(__file__).resolve().parent.parent / "arabisch-app" / "madina-arabisch.html"

_EXTRACT_WORD_JS = """
const fs = require('fs');
const html = fs.readFileSync(process.argv[1], 'utf-8');
const topicId = process.argv[2], ar = process.argv[3];
const start = html.indexOf(`{id:'${topicId}'`);
let i = html.indexOf('[', html.indexOf('words:[', start));
let depth = 0, end = -1;
for (let j = i; j < html.length; j++) {
  if (html[j] === '[') depth++;
  else if (html[j] === ']') { depth--; if (depth === 0) { end = j; break; } }
}
const words = eval(html.slice(i, end + 1));
const skeleton = s => s.normalize('NFC').replace(/[\\u0610-\\u061A\\u064B-\\u065F\\u0670]/g, '');
const hit = words.find(w => w[0] === ar) || words.find(w => skeleton(w[0]) === skeleton(ar));
console.log(JSON.stringify(hit || null));
"""

def _word_tuple(topic_id, ar):
    out = subprocess.run(
        ["node", "-e", _EXTRACT_WORD_JS, str(APP_HTML), topic_id, ar],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)

def test_miatun_silent_alif_before_hamza_does_not_get_a_spurious_long_vowel():
    # Regression guard for the translit.py limitation found during this build: مِائَةٌ ("hundred")
    # has a purely orthographic, silent alif before the hamza-on-yaa (ئ) - treating it as a real
    # long vowel used to produce "miāʾatun" instead of the correct "miʾatun".
    w = _word_tuple('b2-l01', 'مِائَةٌ')
    assert w is not None, "مِائَةٌ not found in b2-l01"
    assert w[1] == 'miʾatun'

def test_dhubab_csv_typo_extra_shadda_was_corrected():
    # Regression guard: Ridouane's CSV had "ذُّبَابٌ" (an erroneous extra shadda on the first
    # letter); the correct spelling/transliteration is ذُبَابٌ / dhubābun.
    w = _word_tuple('b2-l17', 'ذُبَابٌ')
    assert w is not None, "ذُبَابٌ not found in b2-l17"
    assert w[1] == 'dhubābun'

def test_plural_vs_further_form_classification_handles_dash_only_entries():
    # Regression guard for the classification rule reused from the Buch-3 build: a two-part CSV
    # entry without a tilde (verb - present, no verbal noun given) must drop the present tense
    # and keep just the main verb, not be mistaken for a noun+plural pair.
    w = _word_tuple('b2-l04', 'فَرَّ')
    assert w is not None, "فَرَّ not found in b2-l04"
    assert w[2] == 'flüchten, abhauen, fliehen'
    # ...while a genuine noun+plural dash pair still gets its "(Plural: ...)" annotation.
    w2 = _word_tuple('b2-l03', 'نَافِذَةٌ')
    assert w2 is not None, "نَافِذَةٌ not found in b2-l03"
    assert 'Plural: نَوَافِذُ' in w2[2]
