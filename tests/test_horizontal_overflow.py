# Gerätetest-Befund Build 11 (Ridouane, 2026-11-27): Auf der Bücher-/Startseite ließ
# sich der gesamte Bildschirminhalt horizontal aus dem Sichtfeld wegschieben.
# Ursache: .view hat durch overflow-y:auto implizit overflow-x:auto, und einzelne
# t-words-Chips mit langen deutschen Glossen (white-space:nowrap) waren breiter als
# der Viewport. Chromium clippt <details> intern (deshalb fiel es am Desktop nie auf),
# WKWebView auf iOS nicht — dort pannte der ganze Viewport.
# Fix: lange Chips dürfen intern umbrechen, und .view clippt horizontal explizit;
# bewusste horizontale Chip-Reihen (.scroller) scrollen weiter in sich selbst.

VIEWPORT = {"width": 390, "height": 844}

# Liefert sichtbare Elemente der aktiven Ansicht, die seitlich über den Viewport
# hinausragen, ohne in einem eigenen horizontalen Scroll-Container zu liegen.
JS_OFFENDERS = """(viewSel) => {
  const iw = window.innerWidth;
  const out = [];
  document.querySelectorAll(viewSel + ' *').forEach(el => {
    if (el.closest('[hidden]')) return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || (r.right <= iw + 1 && r.left >= -1)) return;
    for (let a = el.parentElement; a && !a.matches('.view'); a = a.parentElement) {
      const ox = getComputedStyle(a).overflowX;
      if (ox === 'auto' || ox === 'scroll') return; // bewusst scrollbar
    }
    out.push(el.tagName + '.' + String(el.className).slice(0, 40)
      + ' w=' + Math.round(r.width) + ' right=' + Math.round(r.right));
  });
  return out.slice(0, 8);
}"""


def test_startseite_hat_keine_unclippbaren_ueberbreiten_elemente(page, served_app):
    page.set_viewport_size(VIEWPORT)
    page.goto(served_app)
    offenders = page.evaluate(JS_OFFENDERS, "#v-start")
    assert offenders == []


def test_views_clippen_horizontal_explizit(page, served_app):
    # Backstop gegen künftige überbreite Elemente: Views dürfen nie selbst
    # horizontal scrollen/pannen, egal was ein Kind tut.
    page.set_viewport_size(VIEWPORT)
    page.goto(served_app)
    ox = page.evaluate("() => getComputedStyle(document.querySelector('.view')).overflowX")
    assert ox == "hidden"
