# Ridouane (2026-11-20): vierter und letzter Schritt des Quizlet-Vokabel-Abgleichs - Buch 1
# (alle Lektionen außer 11 und 16, die keine CSV-Lücken hatten). Gleiche Policy wie Buch 2/3
# (Hauptform + "Plural: ..."-Anmerkung bei Nomen, Präsensform fallengelassen bei Verben ohne
# Verbalnomen). Lektionsspanne "12-13" (13 Wörter) nach der in Buch 2 bestätigten Regel per
# Position in der Mitte geteilt (7 auf Lektion 12, 6 auf Lektion 13).
#
# Echter translit.py-Bug gefunden und behoben (betrifft auch bereits gepushte Buch-2/3-Daten
# nicht, da dort kein Wort dieses Muster hatte): ein Konsonant mit Tanwin-Fatha gefolgt von einem
# bloßen Alif wurde schon fuer die generische Konsonanten-Branch gefixt (مُسْتَقْبَلًا), aber die
# separate WAW/YEH-Branch (و/ي als Basisbuchstabe) hatte denselben Bug noch - مُرَاعِيًا wurde zu
# "murāʿiyanā" statt "murāʿiyan" (ueberfluessiges "ā" durch den bloßen Alif nach ي+Fathatan).
#
# Systematischer CSV-Tippfehler gefunden: Ridouane tippt bei -ات-Pluralen manchmal ة statt ت ans
# Ende (اةٌ statt اتٌ). Betraf 3 Stellen in Buch 1 (أُمَّهَاةٌ, رَكَعَاةٌ, كَلِمَاةٌ) und war in Buch 2
# schon einmal einzeln aufgefallen (خَادِمَاةٌ) - die komplette CSV wurde jetzt gezielt auf dieses
# Muster durchsucht, keine weiteren Fundstellen in Buch 2/3 (die dort gefundenen اة-Endungen sind
# alle legitime Singular-Instrumentnomen wie مِقْلَاةٌ, nicht fälschlich benannte Plurale).

import re

EXPECTED_COUNTS = {
    'b1-l01': 38, 'b1-l02': 15, 'b1-l03': 57, 'b1-l04': 56, 'b1-l05': 18,
    'b1-l06': 33, 'b1-l07': 16, 'b1-l08': 21, 'b1-l09': 47, 'b1-l10': 22,
    'b1-l12': 20, 'b1-l13': 30, 'b1-l14': 35, 'b1-l15': 13, 'b1-l17': 11,
    'b1-l18': 14, 'b1-l19': 21, 'b1-l20': 15, 'b1-l21': 7, 'b1-l22': 15,
    'b1-l23': 9,
}

def _goto_cards_book1(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'karten'; }")
    page.click("#cards-book-seg [data-book='1']")

def _deck_card_count(page, topic_id):
    text = page.inner_text(f"[data-study='{topic_id}'] .d-meta")
    return int(re.match(r'(\d+)', text).group(1))

def test_b1_lessons_gained_the_csv_words(page, served_app):
    _goto_cards_book1(page, served_app)
    for topic_id, expected in EXPECTED_COUNTS.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b1_untouched_lessons_kept_their_original_counts(page, served_app):
    # Regression guard: lessons 11 and 16 had no CSV gaps and must stay exactly as before.
    _goto_cards_book1(page, served_app)
    untouched = {'b1-l11': 10, 'b1-l16': 10}
    for topic_id, expected in untouched.items():
        assert _deck_card_count(page, topic_id) == expected, topic_id

def test_b1_word_chips_render_scoped_to_its_own_topic(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'start'; }")
    page.click("#book-seg [data-book='1']")
    page.click("[data-topic='b1-l03'] summary")
    page.wait_for_selector("[data-topic='b1-l03'] .t-words .chip")
    chips = page.locator("[data-topic='b1-l03'] .t-words .chip")
    assert chips.count() == 10
    for i in range(10):
        ar = chips.nth(i).locator(".ar-s").inner_text()
        de = chips.nth(i).locator(".de-s").inner_text()
        assert ar.strip() and de.strip()

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

def test_waw_yeh_tanwin_fatha_branch_has_no_spurious_trailing_alif():
    # Regression guard for the translit.py bug found during this build: the dedicated WAW/YEH
    # consonant branch was missing the "consume the bare alif after an -an ending" fix that the
    # generic consonant branch already had, so مُرَاعِيًا became "murāʿiyanā" instead of the
    # correct "murāʿiyan".
    w = _word_tuple('b1-l04', 'مُرَاعِيًا')
    assert w is not None, "مُرَاعِيًا not found in b1-l04"
    assert w[1] == 'murāʿiyan'

def test_mother_plural_e_t_typo_was_corrected():
    # Regression guard: Ridouane's CSV had "أُمَّهَاةٌ" (ة instead of ت at the end of the plural,
    # plus a missing shadda on the singular) - correct is أُمٌّ / أُمَّهَاتٌ (ummun / ummahātun).
    w = _word_tuple('b1-l09', 'أُمٌّ')
    assert w is not None, "أُمٌّ not found in b1-l09"
    assert w[1] == 'ummun'
    assert 'أُمَّهَاتٌ' in w[2]

def test_hamza_seat_typo_in_question_word_was_corrected():
    # Regression guard: Ridouane's CSV spelled "question" with hamza-on-alif (سُأَالٌ) instead of
    # the correct hamza-on-waw seat (سُؤَالٌ). The transliteration output was already correct
    # either way, but the stored Arabic spelling itself must be the correct one.
    w = _word_tuple('b1-l04', 'سُؤَالٌ')
    assert w is not None, "سُؤَالٌ not found in b1-l04"
