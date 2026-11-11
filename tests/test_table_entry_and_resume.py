# Einstieg in ein Typ-2-Thema (Themenauswahl), Robustheit bei defekten Lektionsdaten und Fortschritt über
# einen Reload hinweg.
#
# Adressierung (Abschluss-Review, Finding 1/4): Eingabefeld-Id und data-qi tragen den INDEX DER NACHRICHT in
# CHAT.tutor.msgs, nicht den Zell-Cursor m.pos. Anders als in tests/test_table_submit.py liegt die Tabelle
# hier nicht zwangsläufig auf msgs[0] (practiceTopic() legt vorher eine "Neues Thema"-Notiz an), deshalb
# wird der Index über _table_index() live ermittelt.


def _table_index(page):
    return page.evaluate("() => CHAT.tutor.msgs.findIndex(m => m.role === 'table')")


def _answer_current_cell(page, mi):
    pos = page.evaluate(f"() => CHAT.tutor.msgs[{mi}].pos")
    step = page.evaluate(f"() => {{ const t = CHAT.tutor.msgs[{mi}]; return t.steps[t.order[{pos}]]; }}")
    page.fill(f"#t-input-{mi}", step["form"])
    page.click(f'[data-table-submit][data-qi="{mi}"]')


def test_selecting_topic_with_table_starts_table(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == True


# Abschluss-Review, Finding 3: Dieser Test hieß vorher
# test_malformed_table_lesson_falls_back_to_quiz und rief practiceTopic('broken') auf, OHNE dass 'broken'
# je in TOPICS/TOPIC registriert war. practiceTopic() bricht aber schon in Zeile 1 ab (`const t =
# TOPIC[id]; if (!t) return;`), der Pfad für defekte Lektionsdaten wurde also nie betreten und die
# Zusicherung "keine Tabellennachricht" galt nur deshalb, weil CHAT.tutor.msgs leer blieb. Jetzt wird das
# Thema zuerst registriert, damit practiceTopic() wirklich bis zum Typ-2-Einstieg läuft.
# Auch der Name war falsch: Für ein Thema MIT TABLES-Eintrag fällt die App bewusst NICHT auf eine
# Typ-1-Quizfrage zurück (das wäre eine fremde Frage aus einer anderen Lektion, siehe ensureTutorTable()
# in madina-arabisch.html) - die kaputte Lektion wird still übersprungen.
def test_malformed_table_lesson_is_skipped_without_quiz_fallback(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      TOPIC['broken'] = {id:'broken', book:2, ar:'كسر', de:'Kaputte Lektion', gram:'', ex:[], words:[]};
      TABLES['broken'] = [{verb:'x', tense:'madi', de:'kaputt', cells:[]}];
      practiceTopic('broken');
    }""")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == False
    # Kein Durchfallen in die Typ-1-Logik: keine fremde Quizfrage, nur die "Neues Thema"-Notiz.
    assert page.evaluate("() => CHAT.tutor.msgs.map(m => m.role)") == ["note"]
    # Auch ein erneutes Anzeigen des Tutor-Tabs darf hier nichts anhängen (kein Einfrieren, kein Wachsen).
    page.evaluate("() => show('tutor')")
    page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.map(m => m.role)") == ["note"]


# Abschluss-Review, Finding 2: cells ist NICHT leer, aber keine einzige Zelle passt in einen der festen
# Buckets von buildTableSteps() (hier: unbekannte group/num). buildTableSteps() liefert dann ein leeres
# Array; ohne die Prüfung in makeTable() entstünde eine Tabellennachricht ohne Zeilen - eine tote Blase,
# die nie beantwortbar und nie done ist und die Lektion damit dauerhaft blockiert.
def test_table_with_zero_matching_cells_is_skipped(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      TOPIC['broken-cells'] = {id:'broken-cells', book:2, ar:'كسر', de:'Zellen ohne Bucket', gram:'', ex:[], words:[]};
      TABLES['broken-cells'] = [{verb:'y', tense:'madi', de:'kaputt', cells:[
        {group:'9', gender:'m', num:'sg', pronoun:'هو', form:'ي1'},
        {group:'1', gender:null, num:'xx', pronoun:'أنا', form:'ي2'}
      ]}];
    }""")
    assert page.evaluate("() => makeTable('broken-cells', 0)") is None
    assert page.evaluate("() => buildTableSteps(TABLES['broken-cells'][0].cells).length") == 0
    page.evaluate("() => { practiceTopic('broken-cells'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'table')") == False
    assert page.evaluate("() => CHAT.tutor.msgs.map(m => m.role)") == ["note"]
    page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.map(m => m.role)") == ["note"]


def test_reload_resumes_table_mid_phase1(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    mi = _table_index(page)
    page.fill(f"#t-input-{mi}", "ذهب")
    page.click(f'[data-table-submit][data-qi="{mi}"]')
    page.reload()
    page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').pos") == 1


def test_reload_resumes_exact_shuffle_in_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    mi = _table_index(page)
    for _ in range(10):
        _answer_current_cell(page, mi)
    order_before = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').order")
    page.reload()
    page.evaluate("() => show('tutor')")
    order_after = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'table').order")
    assert order_before == order_after


# Regressionstest (Fix-Runde 1, Reviewer-Fund): ensureTutorQuiz() durfte für ein Typ-2-Thema NIE in die
# Typ-1-Logik (tutorQuiz()/EX) durchfallen, egal warum der Tabellen-Push-Zweig nicht greift. Vorher führte
# jeder erneute show('tutor')-Aufruf (z. B. Tab-Wechsel zurück zum Tutor, zweiter Reload) zu einer
# unbegrenzten table/quiz-Wechsel-Duplizierung: die letzte Nachricht war abwechselnd eine fremde quiz
# (von tutorQuiz()'s allgemeinem Themen-Pool-Fallback, da EX['b2-l08'] nicht existiert) und eine frische
# Tabelle - bei jedem Aufruf kam eine weitere Nachricht dazu, nie stabil. Dieser Test ruft show('tutor')
# mehrfach hintereinander auf (nach practiceTopic()) und prüft, dass sich die Nachrichtenliste nach dem
# ersten automatischen Tabellen-Push stabilisiert statt zu wachsen, und dass dabei keine weitere 'quiz'-
# Nachricht für dieses Typ-2-Thema entsteht.
def test_repeated_show_tutor_does_not_duplicate_table_or_quiz(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    lengths = []
    for _ in range(5):
        page.evaluate("() => show('tutor')")
        lengths.append(page.evaluate("() => CHAT.tutor.msgs.length"))
    # Nach dem ersten show('tutor')-Aufruf (der die Tabelle findet und nichts mehr anhängt) darf sich die
    # Länge nicht mehr verändern - kein Wachstum über die Aufrufe hinweg.
    assert lengths[0] == lengths[1] == lengths[2] == lengths[3] == lengths[4]
    table_count = page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length")
    assert table_count == 1


# Abschluss-Review, Finding 1: der ECHTE Bedienweg, auf dem der Fehler auftrat - Tutor-Tab öffnen, das
# Konjugations-Thema im #tutor-topic-Dropdown wählen, Tab wechseln und zurückkommen. Dabei lief
# practiceTopic() im Sparmodus direkt in tutorQuiz() (vorbei an der Typ-2-Prüfung in ensureTutorQuiz()) und
# hängte eine FREMDE Quizfrage hinter die Tabelle; beim nächsten Tab-Wechsel sah ensureTutorQuiz() als
# letzte Nachricht diese quiz und legte eine ZWEITE Tabelle an. Beide aktiven Eingabefelder trugen dann
# dieselbe DOM-Id, und eine richtige Antwort in der sichtbaren (unteren) Tabelle wurde wirkungslos.
def test_dropdown_entry_then_tab_switch_keeps_one_playable_table(page, served_app):
    page.goto(served_app)
    page.set_viewport_size({"width": 390, "height": 844})
    page.click('.tab[data-view="tutor"]')
    page.select_option("#tutor-topic", "b2-l08")
    for other in ["karten", "start", "uebersetzer"]:
        page.click(f'.tab[data-view="{other}"]')
        page.click('.tab[data-view="tutor"]')
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length") == 1
    # Nach der Tabelle darf keine (fremde) Quizfrage mehr stehen.
    roles_after_table = page.evaluate(
        "() => { const i = CHAT.tutor.msgs.findIndex(m => m.role === 'table'); return CHAT.tutor.msgs.slice(i).map(m => m.role); }")
    assert "quiz" not in roles_after_table
    # Genau ein aktives Eingabefeld, eindeutige Id.
    ids = page.evaluate("() => [...document.querySelectorAll('.msg.table .t-row.active input')].map(e => e.id)")
    assert len(ids) == 1
    # Und die richtige Antwort wird auch tatsächlich gewertet.
    mi = _table_index(page)
    _answer_current_cell(page, mi)
    assert page.evaluate(f"() => CHAT.tutor.msgs[{mi}].pos") == 1


# Abschluss-Review, Finding 1b: Der Duplikat-Schutz in ensureTutorTable() prüft das GESAMTE msgs-Array,
# nicht nur die letzte Nachricht. Sobald irgendeine Nachricht NACH der Tabelle landet - egal aus welchem
# Grund: eigener Chat-Beitrag im Sparmodus, Abschlussnotiz der Verb-Verkettung, früher die fremde
# Quizfrage aus practiceTopic() -, würde eine Prüfung auf "letzte Nachricht ist eine Tabelle" beim
# nächsten Anzeigen des Tutor-Tabs eine ZWEITE Tabelle für dasselbe Thema anhängen.
def test_stray_message_after_table_does_not_trigger_duplicate(page, served_app):
    page.goto(served_app)
    page.evaluate("() => { practiceTopic('b2-l08'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length") == 1
    page.evaluate("() => { CHAT.tutor.msgs.push({role:'me', text:'مرحبا'}); }")
    for _ in range(3):
        page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length") == 1


# Abschluss-Review, Finding 1 (Nebenwirkung): Eine ABGESCHLOSSENE Lektion darf beim nächsten Anzeigen des
# Tutor-Tabs nicht stillschweigend wieder bei verbIndex 0 starten (alte Bedingung: "ist die letzte
# Nachricht eine Tabelle"). Ein ausdrückliches erneutes Wählen des Themas startet sie dagegen weiterhin
# neu - sichtbar, weil practiceTopic() dabei die "Neues Thema"-Notiz in den Chat legt.
def test_finished_lesson_restarts_only_on_explicit_topic_pick(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      TOPIC['mini'] = {id:'mini', book:2, ar:'صغير', de:'Mini-Lektion', gram:'', ex:[], words:[]};
      TABLES['mini'] = [{verb:'م', tense:'madi', de:'Mini', cells:[
        {group:'3', gender:'m', num:'sg', pronoun:'هو', form:'م1'},
        {group:'1', gender:null, num:'sg', pronoun:'أنا', form:'م2'}
      ]}];
      practiceTopic('mini');
    }""")
    mi = _table_index(page)
    for _ in range(4):  # Phase 1 + Phase 2, je 2 Zellen
        _answer_current_cell(page, mi)
    assert page.evaluate(f"() => CHAT.tutor.msgs[{mi}].done") == True
    before = page.evaluate("() => CHAT.tutor.msgs.length")
    for _ in range(3):
        page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.length") == before
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length") == 1
    # Ausdrückliche Themenwahl: neue Tabelle, frisch bei pos 0.
    page.evaluate("() => { practiceTopic('mini'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').length") == 2
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').pop().pos") == 0
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'table').pop().done") == False
