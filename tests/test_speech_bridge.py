# Natives Vorlesen über die App-Hülle (Plan: Madina Arabisch App - Natives Vorlesen und Mikrofon).
# Ridouane (2026-11-26/27, Gerätetest + Voice Line): speechSynthesis funktioniert innerhalb der
# WebView auf Android ("not supported") und iPhone (stumm) nicht. Läuft die Seite in der nativen
# App-Hülle (erkennbar an window.ReactNativeWebView), schickt speak() deshalb eine
# postMessage-Nachricht {type:'speak', text, lang} an die native Seite (expo-speech) statt die
# Browser-API zu nutzen. Ohne App-Hülle (GitHub Pages) bleibt der bisherige
# speechSynthesis-Pfad exakt unverändert.
#
# speak() liegt in der App-IIFE und ist nicht global — die Tests lösen es über den
# dokumentweit delegierten [data-speak]-Klickpfad aus (Handler bei "Ereignisse").

import json

INIT_BRIDGE = """
window.__posted = [];
window.ReactNativeWebView = { postMessage: m => window.__posted.push(m) };
"""

# Fängt speechSynthesis.speak ab. Die stumme Unlock-Äußerung (volume 0, beim ersten
# pointerdown) wird ausgefiltert — sie ist Autoplay-Freischaltung, kein Vorlesen.
# getVoices liefert deterministisch keine Stimmen, damit lang immer 'ar-SA' ist.
INIT_SYNTH_SPY = """
window.__synthSpoken = [];
if (window.speechSynthesis) {
  window.speechSynthesis.getVoices = () => [];
  window.speechSynthesis.speak = u => { if (u.volume !== 0) window.__synthSpoken.push(u.text); };
}
"""


def _click_speak(page, text):
    page.evaluate(
        "t => { const b = document.createElement('button');"
        " b.dataset.speak = t; b.id = 'test-speak'; document.body.appendChild(b); }",
        text,
    )
    page.click("#test-speak")


def test_speak_in_app_huelle_schickt_bridge_nachricht_statt_speechsynthesis(page, served_app):
    page.add_init_script(INIT_BRIDGE)
    page.add_init_script(INIT_SYNTH_SPY)
    page.goto(served_app)
    _click_speak(page, "مَرْحَبًا")
    posted = page.evaluate("window.__posted")
    assert len(posted) == 1
    assert json.loads(posted[0]) == {"type": "speak", "text": "مَرْحَبًا", "lang": "ar-SA"}
    assert page.evaluate("window.__synthSpoken") == []


def test_speak_ohne_app_huelle_nutzt_weiter_speechsynthesis(page, served_app):
    page.add_init_script(INIT_SYNTH_SPY)
    page.goto(served_app)
    _click_speak(page, "مَرْحَبًا")
    assert page.evaluate("window.__synthSpoken") == ["مَرْحَبًا"]
    assert page.evaluate("typeof window.ReactNativeWebView") == "undefined"
