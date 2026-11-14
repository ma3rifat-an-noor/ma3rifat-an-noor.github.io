# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l19']
# (باب فَاعَلَ, Lektion 19 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l17.py: prüft denselben
# Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN Daten
# von DERIV_TABLES['b3-l19'] für alle vier Tabellen (Haupttabelle, مصدر وزن فِعَال, اسم الفاعل,
# اسم الفاعل/المفعول von خَاطَبَ) - das beweist, dass die hinterlegten Lösungsformen intern konsistent
# sind (buildDerivTableSteps() liefert für die erste Lückenzelle genau die Form, die
# submitDerivTableCell() als richtig akzeptiert), nicht nur dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l19', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # Haupttabelle (tableIndex 0). Reihen 0-1 (شَاهَدَ, قَابَلَ) sind das vollständig vorgegebene Modell,
    # keine Steps. Erste Lückenzelle ist Reihe سَامَحَ -> المضارع يُسَامِحُ.
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "سَامَحَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يُسَامِحُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_fial_masdar_table_real_answer_is_graded_correct(page, served_app):
    # مصدر وزن فِعَال-Tabelle (tableIndex 1). Erste Lückenzelle ist Reihe جَاهَدَ -> المصدر جِهَادٌ.
    page.goto(served_app)
    _push_entry(page, 1)
    step = _active_step(page)
    assert step["root"] == "جَاهَدَ"
    assert step["column"] == "المصدر"
    assert step["form"] == "جِهَادٌ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_ism_al_faail_table_real_answer_is_graded_correct(page, served_app):
    # اسم الفاعل-Tabelle (tableIndex 2). Erste Lückenzelle ist Reihe رَاسَلَ -> اسم الفاعل مُرَاسِلٌ.
    page.goto(served_app)
    _push_entry(page, 2)
    step = _active_step(page)
    assert step["root"] == "رَاسَلَ"
    assert step["column"] == "اسم الفاعل"
    assert step["form"] == "مُرَاسِلٌ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_khataba_ism_al_faail_wal_mafuul_table_real_answer_is_graded_correct(page, served_app):
    # اسم الفاعل/المفعول von خَاطَبَ (tableIndex 3, eine einzige Wurzel). Erste Lückenzelle ist
    # اسم الفاعل مُخَاطِبٌ (die zweite, اسم المفعول مُخَاطَبٌ, folgt danach in derselben Zeile).
    page.goto(served_app)
    _push_entry(page, 3)
    step = _active_step(page)
    assert step["root"] == "خَاطَبَ"
    assert step["column"] == "اسم الفاعل"
    assert step["form"] == "مُخَاطِبٌ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
