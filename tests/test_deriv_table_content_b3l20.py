# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l20']
# (باب تَفَعَّلَ, Lektion 20 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l19.py: prüft denselben
# Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN Daten
# von DERIV_TABLES['b3-l20'] für beide Tabellen (sālim-Haupttabelle, nāqis-Tabelle inkl. der dort
# zusätzlichen أصله-Spalte) - das beweist, dass die hinterlegten Lösungsformen intern konsistent sind
# (buildDerivTableSteps() liefert für die jeweilige Lückenzelle genau die Form, die
# submitDerivTableCell() als richtig akzeptiert), nicht nur dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l20', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # سالِم-Haupttabelle (tableIndex 0). Reihe 0 (تَعَلَّمَ) ist das vollständig vorgegebene Modell, keine
    # Steps. Erste Lückenzelle ist Reihe تَحَدَّثَ -> المضارع يَتَحَدَّثُ.
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "تَحَدَّثَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَتَحَدَّثُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_main_table_real_ism_al_faail_answer_is_graded_correct(page, served_app):
    # سالِم-Haupttabelle (tableIndex 0), zweite Lückenzelle derselben Reihe (تَحَدَّثَ) -> الأمر تَحَدَّثْ,
    # dritte -> اسم الفاعل مُتَحَدِّثُ. Prüft, dass die Lückenzellen auch über die erste hinaus konsistent
    # bewertet werden.
    page.goto(served_app)
    _push_entry(page, 0)
    step1 = _active_step(page)
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)
    assert step2["root"] == "تَحَدَّثَ"
    assert step2["column"] == "الأمر"
    assert step2["form"] == "تَحَدَّثْ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    step3 = _active_step(page)
    assert step3["root"] == "تَحَدَّثَ"
    assert step3["column"] == "اسم الفاعل"
    assert step3["form"] == "مُتَحَدِّثُ"
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['2'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 3


def test_naaqis_table_real_mudari_answer_is_graded_correct(page, served_app):
    # نَاقِص-Tabelle (tableIndex 1). Reihe 0 (تَغَدَّى) ist das vollständig vorgegebene Modell, keine Steps.
    # Erste Lückenzelle ist Reihe تَعَشَّى -> المضارع يَتَعَشَّى.
    page.goto(served_app)
    _push_entry(page, 1)
    step = _active_step(page)
    assert step["root"] == "تَعَشَّى"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَتَعَشَّى"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_naaqis_table_real_asluhu_answer_is_graded_correct(page, served_app):
    # نَاقِص-Tabelle (tableIndex 1), Reihe تَعَشَّى durchlaufen bis zur vierten (letzten) Lückenzelle
    # dieser Reihe: أصله تَعَشُّيُ - die für diese Lektion neue fünfte Spalte (ersetzt اسم الفاعل aus der
    # ersten Tabelle). Prüft, dass auch diese Spalte korrekt bewertet wird.
    page.goto(served_app)
    _push_entry(page, 1)
    step1 = _active_step(page)  # المضارع
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # الأمر
    assert step2["column"] == "الأمر"
    assert step2["form"] == "تَعَشَّ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    step3 = _active_step(page)  # المصدر
    assert step3["column"] == "المصدر"
    assert step3["form"] == "تَعَشٍّ"
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    step4 = _active_step(page)  # أصله
    assert step4["root"] == "تَعَشَّى"
    assert step4["column"] == "أصله"
    assert step4["form"] == "تَعَشُّيُ"
    _submit(page, 0, step4["rowIdx"], step4["colIdx"], step4["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['3'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 4
