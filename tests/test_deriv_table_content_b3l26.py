# Regressionstest für die am 2026-11-15 hinzugefügten echten Inhalte in DERIV_TABLES['b3-l26']
# (الفعل الرباعي, Lektion 26 aus Buch 3 - letzte Lektion der gesamten Verbform-Serie 16/17/19-26). Mirrors
# tests/test_deriv_table_content_b3l25.py: prüft denselben Scoring-Pfad (submitDerivTableCell() über den
# echten Klick-Handler-Weg) direkt gegen die REALEN Daten von DERIV_TABLES['b3-l26'] - das beweist, dass die
# hinterlegten Lösungsformen intern konsistent sind (buildDerivTableSteps() liefert für die jeweilige
# Lückenzelle genau die Form, die submitDerivTableCell() als richtig akzeptiert), nicht nur dass die Daten
# vorhanden sind. Nur eine Tabelle in dieser Lektion (tableIndex 0, Spalten الماضي/المضارع/المصدر, 11
# Wurzeln in 4 Unterkategorien [مجرد فَعْلَلَ, تَفَعْلَلَ, اِفْعَلَلَّ, اِفْعَنْلَلَ], je die erste Wurzel
# jeder Unterkategorie - تَرْجَمَ (Zeile 0), تَرَعْرَعَ (Zeile 4), اِطْمَأَنَّ (Zeile 6), اِحْرَنْجَمَ
# (Zeile 9) - ist das vollständig vorgegebene Modell ohne Steps; macht 14 Steps insgesamt über die 7
# übrigen Zeilen).


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index=0):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l26', {table_index}));
      renderChat('tutor');
    }}""")


def test_first_gap_baathara_mudari_answer_is_graded_correct(page, served_app):
    # Reihe 1 (بَعْثَرَ, باب مجرد فَعْلَلَ, "durcheinanderbringen/umstürzen" - Passiv بُعْثِرَ direkt in
    # dieser Lektion zitiert: "وَإِذَا الْقُبُورُ بُعْثِرَتْ" [الانفطار/4] bzw. [العاديات/9]). Erste
    # Lückenzelle ist المضارع يُبَعْثِرُ nach dem Modellmuster يُتَرْجِمُ (Zeile 0, تَرْجَمَ, ist komplett
    # vorgegeben und erzeugt daher keinen eigenen Step).
    page.goto(served_app)
    _push_entry(page)
    step = _active_step(page)
    assert step["root"] == "بَعْثَرَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يُبَعْثِرُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_mujarrad_root_harwala_masdar_is_graded_correct(page, served_app):
    # Reihe 2 (هَرْوَلَ, باب مجرد, "eilen/traben" - direkt im Hadith Qudsi dieser Lektion belegt: "وَامْشِ
    # إِلَيَّ أَهْرْوِلْ إِلَيْكَ"). Nach المضارع يُهَرْوِلُ folgt المصدر هَرْوَلَةٌ (Muster فَعْلَلَةٌ wie
    # تَرْجَمَةٌ).
    page.goto(served_app)
    _push_entry(page)
    step_mudari = _active_step(page)  # بَعْثَرَ: المضارع
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)  # بَعْثَرَ: المصدر
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    # Jetzt bei هَرْوَلَ: المضارع
    step = _active_step(page)
    assert step["root"] == "هَرْوَلَ"
    assert step["column"] == "المضارع"
    assert step["form"] == "يُهَرْوِلُ"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_masdar2 = _active_step(page)
    assert step_masdar2["root"] == "هَرْوَلَ"
    assert step_masdar2["column"] == "المصدر"
    assert step_masdar2["form"] == "هَرْوَلَةٌ"
    _submit(page, 0, step_masdar2["rowIdx"], step_masdar2["colIdx"], step_masdar2["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['3'].correct") == True


def test_zalzala_mudari_and_masdar_follow_model_pattern(page, served_app):
    # Reihe 3 (زَلْزَلَ, باب مجرد, "erschüttern"). المصدر ist hier bewusst das reguläre زَلْزَلَةٌ nach dem
    # Modellmuster فَعْلَلَةٌ (nicht das alternative Koran-مصدر زِلْزَالٌ, s. Code-Kommentar in
    # DERIV_TABLES['b3-l26']).
    page.goto(served_app)
    _push_entry(page)
    for _ in range(4):  # بَعْثَرَ(2) + هَرْوَلَ(2) = 4 Zellen vor زَلْزَلَ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # زَلْزَلَ: المضارع
    assert step_mudari["root"] == "زَلْزَلَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يُزَلْزِلُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)  # زَلْزَلَ: المصدر
    assert step_masdar["root"] == "زَلْزَلَ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "زَلْزَلَةٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['5'].correct") == True
    # Direkt im Anschluss beginnt تَرَعْرَعَ (Zeile 4, komplett vorgegebenes Modell der zweiten
    # Unterkategorie تَفَعْلَلَ) - erzeugt keinen eigenen Step, daher beginnt die nächste Lücke bereits bei
    # تَمَضْمَضَ (Zeile 5).
    step_next = _active_step(page)
    assert step_next["root"] == "تَمَضْمَضَ"
    assert step_next["column"] == "المضارع"


def test_tafalala_root_tamadmada_is_graded_correct(page, served_app):
    # Reihe تَمَضْمَضَ (باب تَفَعْلَلَ, "sich den Mund ausspülen" - direkt im selben Hadith dieser Lektion
    # belegt: "مَنْ تَمَضْمَضَ واسْتَنْثَرَ خرجت خطاياه من أنفه وفمه"). المضارع يَتَمَضْمَضُ, المصدر
    # تَمَضْمُضٌ (Muster تَفَعْلُلٌ wie تَرَعْرُعٌ).
    page.goto(served_app)
    _push_entry(page)
    for _ in range(6):  # بَعْثَرَ(2) + هَرْوَلَ(2) + زَلْزَلَ(2) = 6 Zellen vor تَمَضْمَضَ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "تَمَضْمَضَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَتَمَضْمَضُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)
    assert step_masdar["root"] == "تَمَضْمَضَ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "تَمَضْمُضٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['7'].correct") == True
    # Direkt im Anschluss beginnt اِطْمَأَنَّ (Zeile 6, komplett vorgegebenes Modell der dritten
    # Unterkategorie اِفْعَلَلَّ) - erzeugt keinen eigenen Step, daher beginnt die nächste Lücke bereits bei
    # اِشْمَأَزَّ (Zeile 7).
    step_next = _active_step(page)
    assert step_next["root"] == "اِشْمَأَزَّ"
    assert step_next["column"] == "المضارع"


def test_ifalalla_root_ishmaazza_matches_quran_verse_in_same_lesson(page, served_app):
    # Reihe اِشْمَأَزَّ (باب اِفْعَلَلَّ, "schaudern/von Abscheu erfasst werden" - الماضي اشمأزّتْ direkt im
    # Dialog dieser Lektion durch Koranvers [الزمر/45] belegt: "وَإِذَا ذُكِرَ اللَّهُ وَحْدَهُ اشْمَأَزَّتْ
    # قُلُوبُ الَّذِينَ لَا يُؤْمِنُونَ"). المضارع يَشْمَئِزُّ, المصدر اِشْمِئْزَازٌ (Muster اِفْعِلْلَال wie
    # اِطْمِئْنَانٌ).
    page.goto(served_app)
    _push_entry(page)
    for _ in range(8):  # بَعْثَرَ(2)+هَرْوَلَ(2)+زَلْزَلَ(2)+تَمَضْمَضَ(2) = 8 Zellen vor اِشْمَأَزَّ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "اِشْمَأَزَّ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَشْمَئِزُّ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)
    assert step_masdar["root"] == "اِشْمَأَزَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِشْمِئْزَازٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['9'].correct") == True


def test_ifalalla_root_iqshaarra_matches_quran_verse_in_same_lesson(page, served_app):
    # Reihe اِقْشَعَرَّ (باب اِفْعَلَلَّ, "Gänsehaut bekommen/erschaudern" - المضارع تَقْشَعِرُّ direkt im
    # Dialog dieser Lektion durch Koranvers [الزمر/23] belegt: "تَقْشَعِرُّ مِنْهُ جُلُودُ الَّذِينَ
    # يَخْشَوْنَ رَبَّهُمْ"). المصدر اِقْشِعْرَارٌ.
    page.goto(served_app)
    _push_entry(page)
    for _ in range(10):  # +اِشْمَأَزَّ(2) = 10 Zellen vor اِقْشَعَرَّ
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)
    assert step_mudari["root"] == "اِقْشَعَرَّ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَقْشَعِرُّ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)
    assert step_masdar["root"] == "اِقْشَعَرَّ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِقْشِعْرَارٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['11'].correct") == True
    # Direkt im Anschluss beginnt اِحْرَنْجَمَ (Zeile 9, komplett vorgegebenes Modell der vierten
    # Unterkategorie اِفْعَنْلَلَ) - erzeugt keinen eigenen Step, daher beginnt die letzte Lücke bereits bei
    # اِفْرَنْقَعَ (Zeile 10).
    step_next = _active_step(page)
    assert step_next["root"] == "اِفْرَنْقَعَ"
    assert step_next["column"] == "المضارع"


def test_last_row_ifranqaa_last_gap_triggers_phase_transition(page, served_app):
    # Letzte Reihe (اِفْرَنْقَعَ, باب اِفْعَنْلَلَ - das in Sarf-Lehrwerken klassische Paarbeispiel zu
    # اِحْرَنْجَمَ: "اِحْرَنْجَمَ القومُ ثم اِفْرَنْقَعُوا"). Die اِفْرَنْقَعَ:المصدر-Zelle ist die LETZTE
    # Lückenzelle der gesamten Tabelle (14 Steps insgesamt, idx 0-13) - das Submit darauf löst den
    # Phasenübergang (Phase 2, zufällige Wiederholung) aus, bei dem answers im selben synchronen Aufruf
    # zurückgesetzt wird; die Korrektheit dieser letzten Zelle ist daher nur über den Phasenübergang selbst
    # beobachtbar.
    page.goto(served_app)
    _push_entry(page)
    # بَعْثَرَ(2)+هَرْوَلَ(2)+زَلْزَلَ(2)+تَمَضْمَضَ(2)+اِشْمَأَزَّ(2)+اِقْشَعَرَّ(2) = 12 Zellen vor اِفْرَنْقَعَ.
    for _ in range(12):
        step = _active_step(page)
        _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    step_mudari = _active_step(page)  # اِفْرَنْقَعَ: المضارع
    assert step_mudari["root"] == "اِفْرَنْقَعَ"
    assert step_mudari["column"] == "المضارع"
    assert step_mudari["form"] == "يَفْرَنْقِعُ"
    _submit(page, 0, step_mudari["rowIdx"], step_mudari["colIdx"], step_mudari["form"])
    step_masdar = _active_step(page)  # اِفْرَنْقَعَ: المصدر (letzte Lückenzelle der gesamten Tabelle)
    assert step_masdar["root"] == "اِفْرَنْقَعَ"
    assert step_masdar["column"] == "المصدر"
    assert step_masdar["form"] == "اِفْرِنْقَاعٌ"
    _submit(page, 0, step_masdar["rowIdx"], step_masdar["colIdx"], step_masdar["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 0


def test_table_has_eleven_rows_and_four_fully_given_model_rows(page, served_app):
    # Strukturtest: bestätigt, dass die Tabelle wirklich EINE durchgehende Tabelle mit 11 Zeilen ist (nicht
    # 4 getrennte Tabellen, wie die ursprüngliche Vault-Schätzung hätte sein können) und genau 4 Zeilen
    # komplett vorgegeben sind (eine pro Unterkategorie).
    page.goto(served_app)
    rows = page.evaluate("() => DERIV_TABLES['b3-l26'][0].rows")
    assert len(rows) == 11
    fully_given = [r for r in rows if all(r["given"])]
    assert len(fully_given) == 4
    assert [r["root"] for r in fully_given] == ["تَرْجَمَ", "تَرَعْرَعَ", "اِطْمَأَنَّ", "اِحْرَنْجَمَ"]
    tables = page.evaluate("() => DERIV_TABLES['b3-l26']")
    assert len(tables) == 1
    steps = page.evaluate("() => buildDerivTableSteps(DERIV_TABLES['b3-l26'][0])")
    assert len(steps) == 14
