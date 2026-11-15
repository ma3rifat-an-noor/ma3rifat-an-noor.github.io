# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l21']
# (باب تَفَاعَلَ, Lektion 21 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l20.py: prüft denselben
# Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN Daten
# von DERIV_TABLES['b3-l21'] für beide Tabellen (Haupttabelle inkl. der beiden ناقص-Wurzeln تَبَاكَى/تَعَامَى,
# und die اسم-الفاعل-Drilltabelle) - das beweist, dass die hinterlegten Lösungsformen intern konsistent
# sind (buildDerivTableSteps() liefert für die jeweilige Lückenzelle genau die Form, die
# submitDerivTableCell() als richtig akzeptiert), nicht nur dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l21', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # Haupttabelle (tableIndex 0). Reihe 0 (تَنَاوَلَ) ist das vollständig vorgegebene Modell, keine Steps.
    # Erste Lückenzelle ist Reihe تَعَاوَنَ -> المضارع يَتَعَاوَنُ.
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "تَعَاوَنَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَتَعَاوَنُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_main_table_real_masdar_hamza_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe تَسَاءَلَ (hamzierte Wurzel, belegt durch das in dieser Lektion zitierte
    # Qur'an-Beispiel عَمَّ يَتَسَاءَلُونَ) durchlaufen bis zur letzten Lückenzelle: المصدر تَسَاؤُلٌ.
    page.goto(served_app)
    _push_entry(page, 0)
    step1 = _active_step(page)  # تَعَاوَنَ: المضارع
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # تَعَاوَنَ: الأمر
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    step3 = _active_step(page)  # تَعَاوَنَ: المصدر
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    step4 = _active_step(page)  # تَسَاءَلَ: المضارع
    assert step4["root"] == "تَسَاءَلَ"
    assert step4["column"] == "المضارع"
    assert step4["form"] == "يَتَسَاءَلُ"
    _submit(page, 0, step4["rowIdx"], step4["colIdx"], step4["form"])
    step5 = _active_step(page)  # تَسَاءَلَ: الأمر
    assert step5["form"] == "تَسَاءَلْ"
    _submit(page, 0, step5["rowIdx"], step5["colIdx"], step5["form"])
    step6 = _active_step(page)  # تَسَاءَلَ: المصدر
    assert step6["root"] == "تَسَاءَلَ"
    assert step6["column"] == "المصدر"
    assert step6["form"] == "تَسَاؤُلٌ"
    _submit(page, 0, step6["rowIdx"], step6["colIdx"], step6["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['5'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 6


def test_main_table_real_naaqis_amr_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe تَبَاكَى (ناقص-Wurzel, المصدر ist im Druck MIT أصله-Hinweis vorgegeben, daher kein
    # Step dafür - nur المضارع und الأمر sind Lückenzellen). Prüft die defekte Amr-Bildung (finales Alif
    # fällt zusätzlich zu حرف المضارعة weg: تَتَبَاكَى -> تَبَاكَ).
    page.goto(served_app)
    _push_entry(page, 0)
    # Vier Lückenzellen vor تَبَاكَى durchlaufen (تَعَاوَنَ: 3, تَسَاءَلَ: 3, تَشَاجَرَ: 3 = 9 Zellen), dann
    # تَبَاكَى selbst.
    for _ in range(9):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "تَبَاكَى"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَتَبَاكَى"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)
    assert step_amr["root"] == "تَبَاكَى"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "تَبَاكَ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['10'].correct") == True


def test_main_table_real_second_naaqis_row_full_row_is_graded_correct(page, served_app):
    # Haupttabelle, letzte Reihe تَعَامَى (ناقص-Wurzel OHNE jeden gedruckten Hinweis - alle 3 Lückenzellen
    # المضارع/الأمر/المصدر müssen eigenständig abgeleitet werden, Modell: يَتَعَامَى belegt direkt durch
    # Übung 9 dieser Lektion "إنما يَتَعَامَى حتى يتصدق عليه الناس").
    page.goto(served_app)
    _push_entry(page, 0)
    # 9 Zellen (تَعَاوَنَ/تَسَاءَلَ/تَشَاجَرَ) + 2 Zellen (تَبَاكَى: المضارع, الأمر) = 11 Zellen vor تَعَامَى.
    for _ in range(11):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "تَعَامَى"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَتَعَامَى"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    # idx 11 (المضارع) ist noch nicht die letzte Zelle der Tabelle - answers[] ist hier noch unangetastet
    # von einem Phasenübergang, sicher prüfbar.
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['11'].correct") == True
    step_amr = _active_step(page)
    assert step_amr["root"] == "تَعَامَى"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "تَعَامَ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    step_masdar = _active_step(page)
    assert step_masdar["root"] == "تَعَامَى"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "تَعَامٍ"
    # Das ist die LETZTE Lückenzelle der Haupttabelle (idx 13 von 0-13): das Submit unten lässt
    # buildDerivTableSteps() in Phase 2 umschalten (zufällige Wiederholung derselben Steps) statt
    # m.done zu setzen - und dabei wird m.answers im selben synchronen Aufruf wieder auf {} zurückgesetzt
    # (siehe submitDerivTableCell()). Die Korrektheit dieser letzten Zelle ist daher NICHT mehr über
    # answers[] nach dem Submit beobachtbar; statt dessen beweist der Phasenübergang selbst, dass die
    # Eingabe als korrekt gewertet wurde (ein falsches zweites Attempt würde bei norm()-Mismatch zwar auch
    # weiterschalten, aber hier wird bewusst die ECHTE, korrekte Form übergeben, siehe step_masdar oben).
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0


def test_ism_al_faail_table_real_answer_is_graded_correct(page, served_app):
    # اسم-الفاعل-Drilltabelle (tableIndex 1). Reihe 0 (تَفَاعَلَ, das generische Platzhalterverb) -> اسم
    # الفاعل مُتَفَاعِلٌ.
    page.goto(served_app)
    _push_entry(page, 1)
    step = _active_step(page)
    assert step["root"] == "تَفَاعَلَ"
    assert step["column"] == "اسم الفاعل"
    assert step["form"] == "مُتَفَاعِلٌ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_ism_al_faail_table_real_tashaa_um_answer_is_graded_correct(page, served_app):
    # اسم-الفاعل-Drilltabelle (tableIndex 1), zweite Reihe تَشَاءَمَ (hamziert) -> مُتَشَائِمٌ ("Pessimist").
    page.goto(served_app)
    _push_entry(page, 1)
    step1 = _active_step(page)
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)
    assert step2["root"] == "تَشَاءَمَ"
    assert step2["column"] == "اسم الفاعل"
    assert step2["form"] == "مُتَشَائِمٌ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['1'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 2
