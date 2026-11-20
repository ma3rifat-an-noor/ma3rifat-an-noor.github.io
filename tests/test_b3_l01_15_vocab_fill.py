# Ridouane (2026-11-20): zweiter Schritt des Quizlet-Vokabel-Abgleichs - Buch 3, Lektionen 1-15
# hatten bereits eigene Wortlisten (3-10 Woerter), die CSV liefert dort zusaetzliche Woerter zum
# Ergaenzen statt Neuaufbau. Neue Woerter werden an die bestehenden angehaengt (Reihenfolge/Inhalt
# der alten Woerter unveraendert); Card-IDs sind ueber `topic.id + slug(transliteration)` stabil
# (siehe `madina-arabisch.html` Kartenregister), ein Anhaengen verschiebt also keine bestehenden
# Lernfortschritte. Gleiche Zusammengesetzte-Formen-Policy wie beim ersten Schritt (Lektion 16-26):
# Hauptform + Zusatzform als Anmerkung ("Plural: ..." / "weitere Form: ..."), unvokalisierte
# Zusatzformen weggelassen.
#
# Gefundener und behobener echter Bug beim Bau dieser Liste: bei Lektion 12-15 paart die CSV Verben
# direkt mit ihrem Verbalnomen per "-" (ohne Praesensform dazwischen) - das alte "beginnt mit ي"-
# Erkennungsmuster aus Lektion 16-26 hat solche Verbalnomen faelschlich als "Plural" markiert, weil
# sie fast nie mit ي beginnen. Jetzt wird stattdessen geprueft, ob die Hauptform selbst auf Tanwin
# endet (= Nomen -> Plural) oder nicht (= Verb -> weitere Form).

import re

EXPECTED_COUNTS = {
    'b3-l01': 211, 'b3-l02': 242, 'b3-l03': 64, 'b3-l04': 83, 'b3-l05': 90,
    'b3-l06': 65, 'b3-l07': 90, 'b3-l08': 48, 'b3-l09': 53, 'b3-l10': 27,
    'b3-l11': 20, 'b3-l12': 88, 'b3-l13': 71, 'b3-l14': 36, 'b3-l15': 122,
}

def _goto_cards_book3(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='3']")

def _deck_card_count(page, topic_id):
    text = page.inner_text(f"[data-study='{topic_id}'] .d-meta")
    return int(re.match(r'(\d+)', text).group(1))

def test_b3_l01_15_lessons_gained_the_csv_words(page, served_app):
    _goto_cards_book3(page, served_app)
    for topic_id, expected in EXPECTED_COUNTS.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b3_l16_26_untouched_by_this_second_step(page, served_app):
    # Regression guard: the first step's lessons must not have been touched by this one.
    _goto_cards_book3(page, served_app)
    untouched = {
        'b3-l16': 117, 'b3-l17': 135, 'b3-l18': 7, 'b3-l19': 107, 'b3-l20': 47,
        'b3-l21': 114, 'b3-l22': 50, 'b3-l23': 77, 'b3-l24': 43, 'b3-l25': 69, 'b3-l26': 66,
    }
    for topic_id, expected in untouched.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b3_l01_word_chips_render_scoped_to_its_own_topic(page, served_app):
    # Regression guard for the page-wide-selector bug found earlier today: the Buecher-tab start
    # page renders every book-3 topic's word chips at once (capped at 10 each), so the selector
    # must be scoped to the clicked topic's own <details data-topic="..."> element.
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'start'; }")
    page.click("#book-seg [data-book='3']")
    page.click("[data-topic='b3-l01'] summary")
    page.wait_for_selector("[data-topic='b3-l01'] .t-words .chip")
    chips = page.locator("[data-topic='b3-l01'] .t-words .chip")
    assert chips.count() == 10
    for i in range(10):
        ar = chips.nth(i).locator(".ar-s").inner_text()
        de = chips.nth(i).locator(".de-s").inner_text()
        assert ar.strip() and de.strip()

# The two regression tests below check specific [ar, tl, de] tuples directly in the shipped
# TOPICS data rather than through the flashcard UI: a study session only ever samples up to 8
# random "fresh" cards per topic (see startSession()'s `fresh.slice(0, 8)`), so there is no
# reliable way to reach one specific word among a lesson's 200+ entries by clicking through the
# UI. Reading the real TOPICS array straight from the shipped file still verifies the actual
# artifact, just without the browser round-trip.

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
const hit = words.find(w => w[0] === ar);
console.log(JSON.stringify(hit || null));
"""

def _word_tuple(topic_id, ar):
    out = subprocess.run(
        ["node", "-e", _EXTRACT_WORD_JS, str(APP_HTML), topic_id, ar],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)

def test_hamza_initial_form_iv_verb_lands_with_correct_transliteration():
    # Regression guard for the translit.py bug found during this build: a word-initial hamza
    # without its own vowel mark (vowel placed on the next letter instead - a vocalization-
    # placement slip, not an unvocalized word) used to lose its initial vowel entirely
    # (أتَى -> "tā" instead of "atā"). b3-l02's "أرْسَلَ" (arsala, Form IV "to send") is exactly
    # this case.
    w = _word_tuple('b3-l02', 'أرْسَلَ')
    assert w is not None, "أرْسَلَ not found in b3-l02"
    assert w[1] == 'arsala'

def test_tanwin_fatha_ending_has_no_spurious_trailing_alif():
    # Regression guard: CONS + FATHATAN + ALEF (the "-an" ending spelled with a trailing bare
    # alif, e.g. dāʾiman) used to get a spurious extra "ā" appended (dāʾimanā instead of dāʾiman),
    # because the bare alif that only marks the tanwīn was reprocessed as if it were a separate
    # long vowel. "مُسْتَقْبَلًا" in b3-l02 ("mustaqbalan") exercises this exact pattern.
    w = _word_tuple('b3-l02', 'مُسْتَقْبَلًا')
    assert w is not None, "مُسْتَقْبَلًا not found in b3-l02"
    assert w[1] == 'mustaqbalan'
