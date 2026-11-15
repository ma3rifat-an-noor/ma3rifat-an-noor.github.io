# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l22']
# (باب انْفَعَلَ, Lektion 22 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l21.py: prüft denselben
# Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN Daten
# von DERIV_TABLES['b3-l22'] (einzige Tabelle dieser Lektion) - das beweist, dass die hinterlegten
# Lösungsformen intern konsistent sind (buildDerivTableSteps() liefert für die jeweilige Lückenzelle genau
# die Form, die submitDerivTableCell() als richtig akzeptiert), nicht nur dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l22', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # Haupttabelle (tableIndex 0, einzige Tabelle dieser Lektion). Reihe 0 (اِنْكَسَرَ) ist das vollständig
    # vorgegebene Modell, keine Steps. Erste Lückenzelle ist Reihe اِنْفَتَحَ -> المضارع يَنْفَتِحُ.
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "اِنْفَتَحَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَنْفَتِحُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_main_table_real_masdar_infitah_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe اِنْفَتَحَ komplett durchlaufen bis zur letzten Lückenzelle dieser Reihe:
    # المصدر اِنْفِتَاحٌ (geläufiger politischer Fachbegriff "Infitah/Öffnung").
    page.goto(served_app)
    _push_entry(page, 0)
    step1 = _active_step(page)  # اِنْفَتَحَ: المضارع
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # اِنْفَتَحَ: اسم الفاعل
    assert step2["root"] == "اِنْفَتَحَ"
    assert step2["column"] == "اسم الفاعل"
    assert step2["form"] == "مُنْفَتِحٌ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    step3 = _active_step(page)  # اِنْفَتَحَ: المصدر
    assert step3["root"] == "اِنْفَتَحَ"
    assert step3["column"] == "المصدر"
    assert step3["form"] == "اِنْفِتَاحٌ"
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['2'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 3


def test_main_table_real_mudaaf_row_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe اِنْشَقَّ (مضعّف-Wurzel ش-ق-ق, اسم الفاعل مُنْشَقٌّ ist im Druck MIT
    # Idgham/Shadda vorgegeben, daher kein Step dafür - nur المضارع und المصدر sind Lückenzellen). Prüft die
    # Idgham-Bildung im المضارع (يَنْشَقُّ) und den Masdar (اِنْشِقَاقٌ, bezeugt durch den Namen von
    # Sure 84 "الانشقاق").
    page.goto(served_app)
    _push_entry(page, 0)
    # 12 Lückenzellen vor اِنْشَقَّ durchlaufen (اِنْفَتَحَ, اِنْقَلَبَ, اِنْقَطَعَ, اِنْصَرَفَ je 3 = 12).
    for _ in range(12):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "اِنْشَقَّ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَنْشَقُّ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)
    assert step_masdar["root"] == "اِنْشَقَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِنْشِقَاقٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['13'].correct") == True


def test_main_table_real_naaqis_waawi_last_row_is_graded_correct(page, served_app):
    # Haupttabelle, letzte Reihe اِنْجَلَى (ناقص-واوي-Wurzel ج-ل-و). اسم الفاعل (مُنْجَلٍ) UND المصدر
    # (اِنْجِلاَءٌ، أصله: اِنْجِلاَوٌ) sind im Druck vorgegeben - nur المضارع (يَنْجَلِي) ist die letzte
    # Lückenzelle der gesamten Tabelle, direkt wortwörtlich belegt durch das in dieser Lektion zitierte
    # Bukhari-Hadith "حَتَّى يَنْجَلِيَ" (S.189, dort منصوب durch حتى; Grundform مرفوع يَنْجَلِي).
    page.goto(served_app)
    _push_entry(page, 0)
    # 12 Zellen (اِنْفَتَحَ/اِنْقَلَبَ/اِنْقَطَعَ/اِنْصَرَفَ) + 2 Zellen (اِنْشَقَّ: المضارع, المصدر) = 14
    # Zellen vor اِنْجَلَى.
    for _ in range(14):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "اِنْجَلَى"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَنْجَلِي"
    # Das ist die LETZTE Lückenzelle der Haupttabelle (idx 14 von 0-14, 15 Steps insgesamt): das Submit
    # unten lässt buildDerivTableSteps() in Phase 2 umschalten (zufällige Wiederholung derselben Steps)
    # statt m.done zu setzen - dabei wird m.answers im selben synchronen Aufruf wieder auf {} zurückgesetzt
    # (siehe submitDerivTableCell()). Die Korrektheit dieser letzten Zelle ist daher NICHT mehr über
    # answers[] nach dem Submit beobachtbar; statt dessen beweist der Phasenübergang selbst, dass die
    # Eingabe als korrekt gewertet wurde (ein falsches zweites Attempt würde bei norm()-Mismatch zwar auch
    # weiterschalten, aber hier wird bewusst die ECHTE, korrekte Form übergeben, siehe step_mudari oben).
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
