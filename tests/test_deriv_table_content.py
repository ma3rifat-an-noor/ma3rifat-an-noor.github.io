# Regressionstest für die am 2026-11-13 nachgetragenen echten Lösungsformen in DERIV_TABLES['b3-l16']
# (Entries B-F). Vor diesem Fix trug jede Lückenzelle (given:false) dort `values[colIdx] === null` -
# siehe den Modul-Docstring von tests/test_deriv_table_submit.py, der genau deshalb eine rein
# synthetische Fixture für "richtige Antwort wird erkannt" brauchte, weil die reale Lektion dafür keine
# echte Form hatte. Dieser Test prüft denselben Scoring-Pfad (submitDerivTableCell() über den echten
# Klick-Handler-Weg, wie in tests/test_deriv_table_submit.py), aber direkt gegen die REALEN Daten von
# DERIV_TABLES['b3-l16'] für drei verschiedene Einträge (B, D, F) - das hätte die ursprüngliche Lücke
# (keine echte Form zum Abgleich) zuverlässig aufgedeckt, bevor die Formen nachgetragen wurden.


def _active_step(page, mi=0):
    return page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[t.pos]]; }}")


def _submit(page, mi, ri, ci, value):
    page.fill(f"#dt-input-{mi}-{ri}-{ci}", value)
    page.click(f'[data-deriv-submit][data-mi="{mi}"][data-ri="{ri}"][data-ci="{ci}"]')


def _push_entry(page, table_index):
    page.evaluate(f"""() => {{
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', {table_index}));
      renderChat('tutor');
    }}""")


def test_entry_b_real_masdar_answer_is_graded_correct(page, served_app):
    # Entry B (مصدر باب فعّل, tableIndex 1). Erste Lückenzelle: كَبَّرَ -> المصدر, jetzt mit der echten
    # Form تَكْبِيرٌ statt null hinterlegt.
    page.goto(served_app)
    _push_entry(page, 1)
    step = _active_step(page)
    assert step["form"], "Entry B: erste Lückenzelle hat immer noch keine echte Form hinterlegt"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_entry_d_real_ism_al_mafuul_answer_is_graded_correct(page, served_app):
    # Entry D (اسم المفعول, tableIndex 3, 3 Lückenspalten pro Zeile). Erste Lückenzelle: أَلَّفَ ->
    # المضارع, jetzt mit يُؤَلِّفُ statt null hinterlegt.
    page.goto(served_app)
    _push_entry(page, 3)
    step = _active_step(page)
    assert step["form"], "Entry D: erste Lückenzelle hat immer noch keine echte Form hinterlegt"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1


def test_entry_f_real_masdar_fiaal_answer_is_graded_correct(page, served_app):
    # Entry F (مصدر وزن فِعَال, tableIndex 5). Erste Lückenzelle: قَامَ -> المصدر, jetzt mit قِيَامٌ statt
    # null hinterlegt.
    page.goto(served_app)
    _push_entry(page, 5)
    step = _active_step(page)
    assert step["form"], "Entry F: erste Lückenzelle hat immer noch keine echte Form hinterlegt"
    _submit(page, 0, step["rowIdx"], step["colIdx"], step["form"])
    assert page.evaluate("() => CHAT.tutor.msgs[0].answers['0'].correct") == True
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
