# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l25']
# (بَابُ اسْتَفْعَلَ, Lektion 25 aus Buch 3). Mirrors tests/test_deriv_table_content_b3l24.py: prüft denselben
# Scoring-Pfad (submitDerivTableCell() über den echten Klick-Handler-Weg) direkt gegen die REALEN Daten von
# DERIV_TABLES['b3-l25'] - das beweist, dass die hinterlegten Lösungsformen intern konsistent sind
# (buildDerivTableSteps() liefert für die jeweilige Lückenzelle genau die Form, die submitDerivTableCell()
# als richtig akzeptiert), nicht nur dass die Daten vorhanden sind. Nur eine Tabelle in dieser Lektion
# (tableIndex 0, Spalten الماضي/المضارع/الأمر/المصدر, 7 Wurzeln, Zeile 0 اِسْتَقْبَلَ ist das vollständig
# vorgegebene Modell ohne Steps).


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index=0):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l25', {table_index}));
      renderChat('tutor');
    }}""")


def test_first_gap_istaghfara_mudari_answer_is_graded_correct(page, served_app):
    # Reihe 1 (اِسْتَغْفَرَ, gesunde Wurzel غ-ف-ر). Erste Lückenzelle ist المضارع يَسْتَغْفِرُ - direkt durch
    # das in dieser Lektion zitierte Hadith Qudsi belegt ("فَاسْتَغْفِرُوني أَغْفِرْ لكم").
    page.goto(served_app)
    _push_entry(page)
    step = _active_step(page)
    assert step["root"] == "اِسْتَغْفَرَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَسْتَغْفِرُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_mudaaf_root_istaada_amr_fatha_is_graded_correct(page, served_app):
    # Reihe 2 (اِسْتَعَدَّ, مضعّف-Wurzel ع-د-د). الأمر trägt eine Fatha auf dem verdoppelten Letztradikal
    # (اِسْتَعِدَّ), nicht Sukun - Standard-Sarf-Regel für مضعّف-Imperative ohne Suffix. Direkt durch Übung 4
    # dieser Lektion belegt ("اِسْتَعِدّوا للامتحان فإنه قريب جداً").
    page.goto(served_app)
    _push_entry(page)
    step_mudari = _active_step(page)  # اِسْتَغْفَرَ: المضارع (erste Zelle insgesamt)
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)  # اِسْتَغْفَرَ: الأمر
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    step_masdar = _active_step(page)  # اِسْتَغْفَرَ: المصدر
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    # Jetzt bei اِسْتَعَدَّ: المضارع
    step = _active_step(page)
    assert step["root"] == "اِسْتَعَدَّ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يَسْتَعِدُّ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_amr2 = _active_step(page)
    assert step_amr2["root"] == "اِسْتَعَدَّ"
    assert step_amr2["column"] == "الأمر"
    assert step_amr2["form"] == "اِسْتَعِدَّ"
    _submit(page, 0, step_amr2["rowIdx"], step_amr2["colIdx"], step_amr2["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['4'].correct") == True


def test_naaqis_root_istalqaa_amr_drops_yaa_is_graded_correct(page, served_app):
    # Reihe 3 (اِسْتَلْقَى, ناقص-ي-Wurzel ل-ق-ي, direkt im Dialog dieser Lektion belegt: "فَاسْتَلْقَيْتُ على
    # قَفَايَ"). الأمر verliert das finale ي (اِسْتَلْقِ), analog zu لَاقَى/بَارَى in L19 bzw. اِلْتَقَى in L23.
    page.goto(served_app)
    _push_entry(page)
    for _ in range(6):  # اِسْتَغْفَرَ (3) + اِسْتَعَدَّ (3) = 6 Zellen vor اِسْتَلْقَى
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِسْتَلْقَى: المضارع
    assert step_mudari["root"] == "اِسْتَلْقَى"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَسْتَلْقِي"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)  # اِسْتَلْقَى: الأمر
    assert step_amr["root"] == "اِسْتَلْقَى"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "اِسْتَلْقِ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    step_masdar = _active_step(page)  # اِسْتَلْقَى: المصدر
    assert step_masdar["root"] == "اِسْتَلْقَى"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِسْتِلْقَاءٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['8'].correct") == True


def test_ajwaf_root_istaraaha_masdar_is_given_only_two_gaps(page, served_app):
    # Reihe 4 (اِسْتَرَاحَ, أجوف-Wurzel ر-و-ح) hat im Druck NUR المصدر vorgegeben (اِسْتِرَاحَةٌ), daher nur
    # ZWEI Lückenzellen (المضارع يَسْتَرِيحُ, الأمر اِسْتَرِحْ) statt der üblichen drei.
    page.goto(served_app)
    _push_entry(page)
    for _ in range(9):  # اِسْتَغْفَرَ (3) + اِسْتَعَدَّ (3) + اِسْتَلْقَى (3) = 9 Zellen vor اِسْتَرَاحَ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِسْتَرَاحَ: المضارع
    assert step_mudari["root"] == "اِسْتَرَاحَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَسْتَرِيحُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)  # اِسْتَرَاحَ: الأمر (letzte Zelle dieser Reihe, da المصدر given ist)
    assert step_amr["root"] == "اِسْتَرَاحَ"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "اِسْتَرِحْ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    # Direkt im Anschluss beginnt اِسْتَقَالَ (nächste Reihe) mit المضارع - bestätigt, dass die
    # المصدر-Zelle von اِسْتَرَاحَ korrekt als given übersprungen wurde, kein drittes Submit nötig.
    step_next = _active_step(page)
    assert step_next["root"] == "اِسْتَقَالَ"
    assert step_next["column"] == "المضارع"


def test_ajwaf_root_istaqaala_real_word_istiqaala_is_graded_correct(page, served_app):
    # Reihe 5 (اِسْتَقَالَ, أجوف-Wurzel ق-و-ل, "zurücktreten/kündigen" - sehr geläufiges Wort, المصدر
    # اِسْتِقَالَةٌ "Rücktritt/Kündigung", z. B. "قدَّم استقالته"). Volle Lückenzeile, keine Hinweiszelle.
    page.goto(served_app)
    _push_entry(page)
    for _ in range(11):  # اِسْتَغْفَرَ(3)+اِسْتَعَدَّ(3)+اِسْتَلْقَى(3)+اِسْتَرَاحَ(2) = 11 Zellen vor اِسْتَقَالَ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِسْتَقَالَ: المضارع
    assert step_mudari["root"] == "اِسْتَقَالَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَسْتَقِيلُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)  # اِسْتَقَالَ: الأمر
    assert step_amr["root"] == "اِسْتَقَالَ"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "اِسْتَقِلْ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    step_masdar = _active_step(page)  # اِسْتَقَالَ: المصدر
    assert step_masdar["root"] == "اِسْتَقَالَ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِسْتِقَالَةٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['13'].correct") == True


def test_last_row_istafaada_last_gap_triggers_phase_transition(page, served_app):
    # Letzte Reihe (اِسْتَفَادَ, أجوف-Wurzel ف-ي-د, "profitieren/Nutzen ziehen" - sehr geläufiges Wort
    # المصدر اِسْتِفَادَةٌ "Nutzen/Vorteil"). Die اِسْتَفَادَ:المصدر-Zelle ist die LETZTE Lückenzelle der
    # gesamten Tabelle (17 Steps insgesamt, idx 0-16) - das Submit darauf löst den Phasenübergang (Phase 2,
    # zufällige Wiederholung) aus, bei dem answers im selben synchronen Aufruf zurückgesetzt wird; die
    # Korrektheit dieser letzten Zelle ist daher nur über den Phasenübergang selbst beobachtbar.
    page.goto(served_app)
    _push_entry(page)
    # 3+3+3+2+3 = 14 Lückenzellen vor اِسْتَفَادَ (اِسْتَغْفَرَ, اِسْتَعَدَّ, اِسْتَلْقَى, اِسْتَرَاحَ, اِسْتَقَالَ).
    for _ in range(14):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِسْتَفَادَ: المضارع
    assert step_mudari["root"] == "اِسْتَفَادَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَسْتَفِيدُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_amr = _active_step(page)  # اِسْتَفَادَ: الأمر
    assert step_amr["root"] == "اِسْتَفَادَ"
    assert step_amr["column"] == "الأمر"
    assert step_amr["form"] == "اِسْتَفِدْ"
    _submit(page, 0, step_amr["rowIdx"], step_amr["colIdx"], step_amr["form"])
    step_masdar = _active_step(page)  # اِسْتَفَادَ: المصدر (letzte Lückenzelle der gesamten Tabelle)
    assert step_masdar["root"] == "اِسْتَفَادَ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِسْتِفَادَةٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0
