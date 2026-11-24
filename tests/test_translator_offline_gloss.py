# Ridouane (2026-11-24): im Übersetzer-Sparmodus erkennt lookupAr() Präfixe/Suffixe korrekt
# (sichtbar im kleinen Hinweistext), aber die große, prominente Übersetzung zeigte nur die nackte
# Grundbedeutung der Karte - z.B. بَيْتِي ("mein Haus") zeigte groß nur "Haus". Diese Tests prüfen,
# dass die Präfix-/Suffix-Bedeutung jetzt in der großen Übersetzung selbst steckt.

def _offline_word_gloss(page, served_app, arabic_text):
    page.goto(served_app)
    page.evaluate("() => { location.hash = 'uebersetzer'; }")
    page.fill("#tr-input", arabic_text)
    page.click("#tr-go")
    page.wait_for_selector(".wd")
    return page.inner_text(".wd .wd-de")


def test_possessive_suffix_shown_in_headline_gloss(page, served_app):
    assert _offline_word_gloss(page, served_app, "بَيْتِي") == "mein Haus"


def test_plural_suffix_shown_in_headline_gloss(page, served_app):
    assert _offline_word_gloss(page, served_app, "مُدَرِّسُونَ") == "Lehrer (Plural)"


def test_prefix_and_possessive_suffix_combined_in_headline_gloss(page, served_app):
    assert _offline_word_gloss(page, served_app, "وَبَيْتُهُمْ") == "und ihr Haus"


def test_prefix_alone_shown_in_headline_gloss(page, served_app):
    assert _offline_word_gloss(page, served_app, "وَالْمَسْجِدُ") == "und die Moschee (Ausnahmeform)"
