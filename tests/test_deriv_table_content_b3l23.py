# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l23']
# (باب افْتَعَلَ, Lektion 23 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l22.py: prüft denselben
# Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN Daten von
# DERIV_TABLES['b3-l23'] für alle vier Tabellen (Haupttabelle inkl. der ناقص- und أجوف-Wurzeln, sowie die
# drei ت-Assimilationsdrilltabellen د/ز/ذ, ص/ض/ط/ظ und و) - das beweist, dass die hinterlegten Lösungsformen
# intern konsistent sind (buildDerivTableSteps() liefert für die jeweilige Lückenzelle genau die Form, die
# submitDerivTableCell() als richtig akzeptiert), nicht nur dass die Daten vorhanden sind.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l23', {table_index}));
      renderChat('tutor');
    }}""")


def test_main_table_real_mudari_answer_is_graded_correct(page, served_app):
    # Haupttabelle (tableIndex 0). Reihe 0 (اِنْتَظَرَ) ist das vollständig vorgegebene Modell, keine Steps.
    # Erste Lückenzelle ist Reihe اِشْتَرَكَ -> المضارع يَشْتَرِكُ.
    page.goto(served_app)
    _push_entry(page, 0)
    step = _active_step(page)
    assert step["root"] == "اِشْتَرَكَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَشْتَرِكُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_main_table_real_imtihaan_masdar_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe اِمْتَحَنَ durchlaufen bis zur letzten Lückenzelle dieser Reihe: المصدر اِمْتِحَانٌ
    # ("Prüfung" - dasselbe Wort, das im Dialog dieser Lektion ständig als الامتحان vorkommt).
    page.goto(served_app)
    _push_entry(page, 0)
    for _ in range(4):  # اِشْتَرَكَ: المضارع/الأمر/اسم الفاعل/المصدر
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step1 = _active_step(page)  # اِمْتَحَنَ: المضارع
    assert step1["root"] == "اِمْتَحَنَ"
    assert step1["form"] == "يَمْتَحِنُ"
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # اِمْتَحَنَ: الأمر
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    step3 = _active_step(page)  # اِمْتَحَنَ: اسم الفاعل
    assert step3["column"] == "اسم الفاعل"
    assert step3["form"] == "مُمْتَحِنٌ"
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    step4 = _active_step(page)  # اِمْتَحَنَ: المصدر
    assert step4["root"] == "اِمْتَحَنَ"
    assert step4["column"] == "المصدر"
    assert step4["form"] == "اِمْتِحَانٌ"
    _submit(page, 0, step4["rowIdx"], step4["colIdx"], step4["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['7'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 8


def test_main_table_real_naaqis_ism_al_faail_answer_is_graded_correct(page, served_app):
    # Haupttabelle, Reihe اِلْتَقَى (ناقص-ي-Wurzel ل-ق-ي). المصدر ist im Druck MIT أصله-Hinweis vorgegeben
    # (kein Step dafür) - اسم الفاعل مُلْتَقٍ (اسم منقوص, wie مُنْجَلٍ in Lektion 22) ist die dritte und
    # letzte Lückenzelle dieser Reihe.
    page.goto(served_app)
    _push_entry(page, 0)
    # 4+4+4 = 12 Lückenzellen vor اِلْتَقَى (اِشْتَرَكَ, اِمْتَحَنَ, اِجْتَمَعَ).
    for _ in range(12):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِلْتَقَى: المضارع
    assert step_mudari["root"] == "اِلْتَقَى"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَلْتَقِي"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)  # اِلْتَقَى: الأمر
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "اِلْتَقِ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    step_ismfaail = _active_step(page)  # اِلْتَقَى: اسم الفاعل
    assert step_ismfaail["root"] == "اِلْتَقَى"
    assert step_ismfaail["column"] == "اسم الفاعل"
    assert step_ismfaail["form"] == "مُلْتَقٍ"
    _submit(page, 0, step_ismfaail["rowIdx"], step_ismfaail["colIdx"], step_ismfaail["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['14'].correct") == True


def test_main_table_real_hollow_row_full_row_is_graded_correct(page, served_app):
    # Haupttabelle, letzte Reihe اِخْتَارَ (أجوف-Wurzel خ-ي-ر). الماضي, اسم الفاعل (مُخْتَارٌ) und المصدر
    # (اِخْتِيَارٌ) sind im Druck vorgegeben - nur المضارع (يَخْتَارُ) und الأمر (اِخْتَرْ) sind Lückenzellen,
    # und الأمر ist die LETZTE Lückenzelle der gesamten Haupttabelle.
    page.goto(served_app)
    _push_entry(page, 0)
    # 12 Zellen (اِشْتَرَكَ/اِمْتَحَنَ/اِجْتَمَعَ) + 3 Zellen (اِلْتَقَى: المضارع/الأمر/اسم الفاعل) = 15 Zellen
    # vor اِخْتَارَ.
    for _ in range(15):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "اِخْتَارَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَخْتَارُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)
    assert step_amr["root"] == "اِخْتَارَ"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "اِخْتَرْ"
    # Das ist die LETZTE Lückenzelle der Haupttabelle (idx 16 von 0-16, 17 Steps insgesamt): das Submit
    # unten lässt buildDerivTableSteps() in Phase 2 umschalten statt m.done zu setzen - dabei wird
    # m.answers im selben synchronen Aufruf wieder auf {} zurückgesetzt (siehe submitDerivTableCell()).
    # Die Korrektheit dieser letzten Zelle ist daher nicht mehr über answers[] beobachtbar; der
    # Phasenübergang selbst beweist, dass die (echte, korrekte) Eingabe als richtig gewertet wurde.
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0


def test_dal_zay_dhal_table_real_mudakkara_answer_is_graded_correct(page, served_app):
    # ت-Assimilationsdrilltabelle فاء د/ز/ذ ← د (tableIndex 1). Reihe 0 (زَحَمَ) ist das vollständig
    # vorgegebene Modell. Reihe 2 (ذَكَرَ) ist der bekannte Sonderfall: ذ assimiliert zusätzlich in das aus
    # ت gewandelte د, daher اِدَّكَرَ (NICHT اِذْدَكَرَ) - im englischen Schlüssel wörtlich als
    # "idhtakara -> idhdakara -> iddakara" vorgerechnet, bekannt aus dem Koranvers "فهل من مُدَّكِر".
    page.goto(served_app)
    _push_entry(page, 1)
    step1 = _active_step(page)  # زَانَ
    assert step1["root"] == "زَانَ"
    assert step1["form"] == "اِزْدَانَ"
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # ذَكَرَ
    assert step2["root"] == "ذَكَرَ"
    assert step2["column"] == "اِفْتَعَلَ"
    assert step2["form"] == "اِدَّكَرَ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['1'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 2


def test_sad_dad_taa_zaa_table_real_no_merge_and_merge_answers_are_graded_correct(page, served_app):
    # ت-Assimilationsdrilltabelle فاء ص/ض/ط/ظ ← ط (tableIndex 2). Testet sowohl den Nicht-Verschmelzungsfall
    # (ظَلَمَ -> اِظْطَلَمَ, im Schlüssel wörtlich als "iztalama" bestätigt, bleibt getrennt) als auch den
    # Verschmelzungsfall (طَلَعَ -> اِطَّلَعَ, gleiche Buchstaben ط+ط zwingen Idgham).
    page.goto(served_app)
    _push_entry(page, 2)
    step1 = _active_step(page)  # صَفَا
    assert step1["root"] == "صَفَا"
    assert step1["form"] == "اِصْطَفَى"
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # ضَرَبَ
    assert step2["root"] == "ضَرَبَ"
    assert step2["form"] == "اِضْطَرَبَ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    step3 = _active_step(page)  # ظَلَمَ: KEINE Verschmelzung
    assert step3["root"] == "ظَلَمَ"
    assert step3["form"] == "اِظْطَلَمَ"
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['2'].correct") == True
    step4 = _active_step(page)  # طَلَعَ: MIT Verschmelzung (identische Buchstaben)
    assert step4["root"] == "طَلَعَ"
    assert step4["form"] == "اِطَّلَعَ"
    # Das ist die LETZTE Lückenzelle dieser Drilltabelle (4 Steps insgesamt, idx 0-3): wie beim
    # Hauptabellen-Test löst das Submit unten den Phasenübergang aus (answers wird dabei zurückgesetzt),
    # daher wird die Korrektheit über den Phasenübergang selbst geprüft, nicht über answers[].
    _submit(page, 0, step4["rowIdx"], step4["colIdx"], step4["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0


def test_waw_table_real_ittahada_answer_is_graded_correct(page, served_app):
    # ت-Assimilationsdrilltabelle فاء و (tableIndex 3). Reihe 0 (وَقَى) ist das vollständig vorgegebene
    # Modell. Reihe 2 (وَحَدَ -> اتَّحَدَ "sich vereinigen") ist im englischen Schlüssel wörtlich als
    # "iwtahada -> ittahada" bestätigt.
    page.goto(served_app)
    _push_entry(page, 3)
    step1 = _active_step(page)  # وَصَلَ
    assert step1["root"] == "وَصَلَ"
    assert step1["form"] == "اتَّصَلَ"
    _submit(page, 0, step1["rowIdx"], step1["colIdx"], step1["form"])
    step2 = _active_step(page)  # وَحَدَ
    assert step2["root"] == "وَحَدَ"
    assert step2["column"] == "اِفْتَعَلَ"
    assert step2["form"] == "اتَّحَدَ"
    _submit(page, 0, step2["rowIdx"], step2["colIdx"], step2["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['1'].correct") == True
    step3 = _active_step(page)  # وَفَقَ
    assert step3["root"] == "وَفَقَ"
    assert step3["form"] == "اتَّفَقَ"
    # Das ist die LETZTE Lückenzelle dieser Drilltabelle (3 Steps insgesamt, idx 0-2): das Submit unten
    # löst den Phasenübergang aus (answers wird dabei zurückgesetzt), daher Prüfung über den
    # Phasenübergang selbst statt über answers[].
    _submit(page, 0, step3["rowIdx"], step3["colIdx"], step3["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
