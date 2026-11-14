# Regressionstest für die am 2026-11-14 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l17']
# (باب أَفْعَلَ, Lektion 17 aus Buch 3). Mirrors tests/test_deriv_table_content.py (Lektion 16): prüft
# denselben Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die
# REALEN Daten von DERIV_TABLES['b3-l17'] für mehrere Einträge (Haupttabelle, الأمر, اسم الفاعل) - das
# beweist, dass die hinterlegten Lösungsformen intern konsistent sind (buildDerivTableSteps() liefert
# für die erste Lückenzelle genau die Form, die submitDerivTableCell() als richtig akzeptiert), nicht nur
# dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l17', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # Haupttabelle (tableIndex 0). Erste Lückenzelle ist Reihe أَغْلَقَ (Reihen 0-1 أَرْسَلَ/أَسْلَمَ sind
    # vollständig vorgegebenes Modell, keine Steps) -> المضارع يُغْلِقُ.
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "أَغْلَقَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يُغْلِقُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_amr_table_real_imperative_answer_is_graded_correct(page, served_app):
    # الأمر-Tabelle (tableIndex 1). Reihe 0 (أَرْسَلَ) ist das vollständig vorgegebene Modell (تُرْسِلُ ->
    # أَرْسِلْ), erste Lückenzelle ist Reihe أَغْلَقَ -> الأمر أَغْلِقْ.
    page.goto(served_app)
    _push_entry(page, 1)
    step = _active_step(page)
    assert step["root"] == "أَغْلَقَ"
    assert step["column"] == "الأمر"
    assert step["form"] == "أَغْلِقْ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_ism_al_faail_table_real_answer_is_graded_correct(page, served_app):
    # اسم الفاعل-Tabelle (tableIndex 2). Erste Lückenzelle ist Reihe أَسْلَمَ -> اسم الفاعل مُسْلِمٌ.
    page.goto(served_app)
    _push_entry(page, 2)
    step = _active_step(page)
    assert step["root"] == "أَسْلَمَ"
    assert step["column"] == "اسم الفاعل"
    assert step["form"] == "مُسْلِمٌ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_ism_al_mafuul_table_real_answer_is_graded_correct(page, served_app):
    # اسم المفعول-Tabelle (tableIndex 3). Erste Lückenzelle ist Reihe أَغْلَقَ -> اسم المفعول مُغْلَقٌ.
    page.goto(served_app)
    _push_entry(page, 3)
    step = _active_step(page)
    assert step["root"] == "أَغْلَقَ"
    assert step["column"] == "اسم المفعول"
    assert step["form"] == "مُغْلَقٌ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
