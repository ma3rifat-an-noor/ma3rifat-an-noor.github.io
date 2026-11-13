def test_order_and_skip_given(page, served_app):
    page.goto(served_app)
    entry = {
        "columns": ["C1", "C2", "C3"],
        "rows": [
            {"root": "R1", "values": ["r1c1", "r1c2", "r1c3"], "given": [True, True, True]},
            {"root": "R2", "values": ["r2c1", None, None], "given": [True, False, False]},
            {"root": "R3", "values": [None, "r3c2", None], "given": [False, True, False]},
        ],
    }
    result = page.evaluate("entry => buildDerivTableSteps(entry)", entry)
    # Zeile 1 ist komplett given -> keine Steps. Zeile 2 liefert colIdx 1 und 2 (in dieser Reihenfolge).
    # Zeile 3 liefert colIdx 0 und 2 (colIdx 1 ist given, wird übersprungen). Reihenfolge: Zeile für Zeile,
    # darin Spalte für Spalte, exakt wie entry.columns - keine universelle Umsortierung wie bei
    # buildTableSteps().
    assert [(s["rowIdx"], s["colIdx"]) for s in result] == [(1, 1), (1, 2), (2, 0), (2, 2)]
    assert result[0] == {"rowIdx": 1, "colIdx": 1, "root": "R2", "column": "C2", "form": None}
    assert result[1] == {"rowIdx": 1, "colIdx": 2, "root": "R2", "column": "C3", "form": None}
    assert result[2] == {"rowIdx": 2, "colIdx": 0, "root": "R3", "column": "C1", "form": None}
    assert result[3] == {"rowIdx": 2, "colIdx": 2, "root": "R3", "column": "C3", "form": None}


def test_all_given_row_produces_no_steps(page, served_app):
    page.goto(served_app)
    entry = {
        "columns": ["A", "B"],
        "rows": [{"root": "X", "values": ["xa", "xb"], "given": [True, True]}],
    }
    result = page.evaluate("entry => buildDerivTableSteps(entry)", entry)
    assert result == []


def test_identifying_info_and_form_for_blank_cells(page, served_app):
    page.goto(served_app)
    entry = {
        "columns": ["الماضي", "المضارع", "المصدر"],
        "rows": [
            {"root": "دَرَسَ", "values": ["دَرَسَ", "يَدْرُسُ", None], "given": [True, True, False]},
        ],
    }
    result = page.evaluate("entry => buildDerivTableSteps(entry)", entry)
    assert result == [
        {"rowIdx": 0, "colIdx": 2, "root": "دَرَسَ", "column": "المصدر", "form": None}
    ]


def test_b3_l16_entry_a_model_has_zero_blank_cells(page, served_app):
    # Eintrag A (Hauptmodell) ist absichtlich 100% given - siehe Design-Doc zum studyOnly-Sonderfall.
    page.goto(served_app)
    entry = page.evaluate("DERIV_TABLES['b3-l16'][0]")
    result = page.evaluate("entry => buildDerivTableSteps(entry)", entry)
    assert result == []


def test_b3_l16_entry_b_masdar_drill_order_and_count(page, served_app):
    page.goto(served_app)
    entry = page.evaluate("DERIV_TABLES['b3-l16'][1]")
    result = page.evaluate("entry => buildDerivTableSteps(entry)", entry)
    # 9 Zeilen, 6 davon mit given:[true,false] (المصدر fehlt), 3 davon irregulär mit vorgegebenem Hinweis
    # (given:[true,true]) - die drei dürfen keine Steps erzeugen, die restlichen sechs schon, in
    # gedruckter Zeilenreihenfolge.
    assert [s["root"] for s in result] == ["كَبَّرَ", "عَلَّمَ", "وَضَّحَ", "وَزَّعَ", "سَجَّلَ", "رَبَّى"]
    assert all(s["colIdx"] == 1 and s["column"] == "المصدر" for s in result)
    # Die Lücken-Zellen haben jetzt echte, verifizierte مصدر-Formen hinterlegt (kein null mehr) -
    # siehe DERIV_TABLES['b3-l16'][1] in madina-arabisch.html, Entry B.
    assert [s["form"] for s in result] == [
        "تَكْبِيرٌ", "تَعْلِيمٌ", "تَوْضِيحٌ", "تَوْزِيعٌ", "تَسْجِيلٌ", "تَرْبِيَةٌ",
    ]


def test_make_deriv_table_returns_null_for_missing_topic(page, served_app):
    page.goto(served_app)
    result = page.evaluate("() => makeDerivTable('does-not-exist', 0)")
    assert result is None


def test_make_deriv_table_marks_zero_step_entry_as_study_only(page, served_app):
    page.goto(served_app)
    result = page.evaluate("() => makeDerivTable('b3-l16', 0)")
    assert result["role"] == "derivTable"
    assert result["studyOnly"] is True
    assert result["done"] is True
    assert result["steps"] == []


def test_make_deriv_table_normal_drill_entry_is_not_study_only(page, served_app):
    page.goto(served_app)
    result = page.evaluate("() => makeDerivTable('b3-l16', 1)")
    assert result["role"] == "derivTable"
    assert result["studyOnly"] is False
    assert result["done"] is False
    assert len(result["steps"]) == 6
