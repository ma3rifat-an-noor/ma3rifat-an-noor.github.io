# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l24']
# (بابا افْعَلَّ/افْعَالَّ, Lektion 24 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l22.py: prüft
# denselben Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN
# Daten von DERIV_TABLES['b3-l24'] für beide Tabellen (اِفْعَلَّ-Haupttabelle und die اِفْعَالَّ-Intensiv-
# tabelle) - das beweist, dass die hinterlegten Lösungsformen intern konsistent sind (buildDerivTableSteps()
# liefert für die jeweilige Lückenzelle genau die Form, die submitDerivTableCell() als richtig akzeptiert),
# nicht nur dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l24', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # Haupttabelle (tableIndex 0, باب اِفْعَلَّ). Reihe 0 (اِحْمَرَّ) ist das vollständig vorgegebene Modell,
    # keine Steps. Erste Lückenzelle ist Reihe اِصْفَرَّ -> المضارع يَصْفَرُّ (direkt im Hadith-Zitat dieser
    # Lektion belegt: "حتى تَصْفَرَّ الشمس").
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "اِصْفَرَّ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَصْفَرُّ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_main_table_real_iswidad_masdar_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe اِسْوَدَّ durchlaufen bis zur المصدر-Lückenzelle: اِسْوِدَادٌ. Das zugehörige
    # المضارع (يَسْوَدُّ) dieser Reihe ist direkt durch das im Dialog dieser Lektion zitierte Koranvers
    # [آل عمران/106-107] belegt ("وَتَسْوَدُّ وُجُوهٌ").
    page.goto(served_app)
    _push_entry(page, 0)
    for _ in range(6):  # اِصْفَرَّ (3) + اِبْيَضَّ (3) = 6 Zellen vor اِسْوَدَّ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِسْوَدَّ: المضارع
    assert step_mudari["root"] == "اِسْوَدَّ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَسْوَدُّ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)  # اِسْوَدَّ: المصدر
    assert step_masdar["root"] == "اِسْوَدَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِسْوِدَادٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['7'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 8


def test_main_table_real_iwajja_last_row_is_graded_correct(page, served_app):
    # Haupttabelle, letzte Reihe اِعْوَجَّ (einzige Mangel- statt Farb-Wurzel, "krumm/schief werden"). Das
    # المصدر (اِعْوِجَاجٌ) dieser Reihe ist wörtlich im Dialog UND in Übung 6 dieser Lektion belegt
    # ("تَقْوِيمُ اعْوِجاجِه", "اسْتِقامَتُهُ في اعْوِجاجِهِ"). اسم الفاعل (مُعْوَجٌّ) ist die LETZTE
    # Lückenzelle der gesamten Haupttabelle.
    page.goto(served_app)
    _push_entry(page, 0)
    # 3+3+3+3 = 12 Lückenzellen vor اِعْوَجَّ (اِصْفَرَّ, اِبْيَضَّ, اِسْوَدَّ, اِخْضَرَّ).
    for _ in range(12):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِعْوَجَّ: المضارع
    assert step_mudari["root"] == "اِعْوَجَّ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَعْوَجُّ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)  # اِعْوَجَّ: المصدر
    assert step_masdar["root"] == "اِعْوَجَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِعْوِجَاجٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    step_ismfaail = _active_step(page)  # اِعْوَجَّ: اسم الفاعل
    assert step_ismfaail["root"] == "اِعْوَجَّ"
    assert step_ismfaail["column"] == "اسم الفاعل"
    assert step_ismfaail["form"] == "مُعْوَجٌّ"
    # Das ist die LETZTE Lückenzelle der Haupttabelle (idx 14 von 0-14, 15 Steps insgesamt): das Submit
    # unten lässt buildDerivTableSteps() in Phase 2 umschalten (zufällige Wiederholung derselben Steps)
    # statt m.done zu setzen - dabei wird m.answers im selben synchronen Aufruf wieder auf {} zurückgesetzt
    # (siehe submitDerivTableCell()). Die Korrektheit dieser letzten Zelle ist daher nicht mehr über
    # answers[] beobachtbar; der Phasenübergang selbst beweist, dass die (echte, korrekte) Eingabe als
    # richtig gewertet wurde.
    _submit(page, 0, step_ismfaail["rowIdx"], step_ismfaail["colIdx"], step_ismfaail["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0


def test_mubalagha_table_real_ihmiraar_answer_is_graded_correct(page, served_app):
    # Zweite Tabelle (tableIndex 1, باب اِفْعَالَّ - Intensivform). Reihe 0 (اِصْفَارَّ) ist das vollständig
    # vorgegebene Modell, keine Steps. Erste Lückenzelle ist Reihe اِحْمَارَّ ("sehr/tief rot werden",
    # Intensivform zu اِحْمَرَّ aus der ersten Tabelle) -> المضارع يَحْمَارُّ.
    page.goto(served_app)
    _push_entry(page, 1)
    step = _active_step(page)
    assert step["root"] == "اِحْمَارَّ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَحْمَارُّ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_masdar = _active_step(page)  # اِحْمَارَّ: المصدر
    assert step_masdar["root"] == "اِحْمَارَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِحْمِيرَارٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['1'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 2


def test_mubalagha_table_real_idhaamma_last_row_is_graded_correct(page, served_app):
    # Zweite Tabelle, letzte Reihe اِدْهَامَّ ("dunkel/schwärzlich-grün werden"). Die اسم-الفاعل-Form (Dual)
    # مُدْهَامَّتَانِ ist wörtlich Koran [الرحمن/64] für die beiden stets tiefgrünen Paradiesgärten - bestätigt
    # direkt die hier hergeleitete Singularform مُدْهَامٌّ, die LETZTE Lückenzelle dieser Tabelle.
    page.goto(served_app)
    _push_entry(page, 1)
    for _ in range(3):  # اِحْمَارَّ: المضارع/المصدر/اسم الفاعل
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِدْهَامَّ: المضارع
    assert step_mudari["root"] == "اِدْهَامَّ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَدْهَامُّ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)  # اِدْهَامَّ: المصدر
    assert step_masdar["root"] == "اِدْهَامَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِدْهِيمَامٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    step_ismfaail = _active_step(page)  # اِدْهَامَّ: اسم الفاعل
    assert step_ismfaail["root"] == "اِدْهَامَّ"
    assert step_ismfaail["column"] == "اسم الفاعل"
    assert step_ismfaail["form"] == "مُدْهَامٌّ"
    # LETZTE Lückenzelle dieser Tabelle (3 Steps insgesamt, idx 0-2): wie oben löst das Submit unten den
    # Phasenübergang aus (answers wird dabei zurückgesetzt), daher Prüfung über den Phasenübergang selbst.
    _submit(page, 0, step_ismfaail["rowIdx"], step_ismfaail["colIdx"], step_ismfaail["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
