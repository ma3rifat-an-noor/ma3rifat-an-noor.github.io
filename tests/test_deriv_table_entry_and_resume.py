# Einstieg in ein Typ-3-Thema (Themenauswahl), Robustheit bei defekten Lektionsdaten und Fortschritt über
# einen Reload hinweg - analog zu tests/test_table_entry_and_resume.py für Typ 2.
#
# 'b3-l16' ist (bewusst, siehe Aufgabenstellung dieser Phase) noch in KEINEM Themen-Picker/TOPICS-Eintrag
# registriert - das Einpflegen in die echte Themenliste ist eine spätere Content-Aufgabe. Für den
# Einstiegstest über den echten Eintrittspunkt (practiceTopic()) wird deshalb - exakt wie es
# tests/test_table_entry_and_resume.py für seine eigenen künstlichen Themen ('broken', 'mini', ...) bereits
# tut - ein TOPIC-Eintrag für 'b3-l16' zur Laufzeit der Testseite registriert, bevor practiceTopic()
# aufgerufen wird. practiceTopic() selbst bricht sonst schon in Zeile 1 ab (`const t = TOPIC[id]; if (!t)
# return;`), ohne das ist der echte Einstiegspfad gar nicht erreichbar.


def _register_b3_l16_topic(page):
    page.evaluate("""() => {
      if (!TOPIC['b3-l16']) {
        TOPIC['b3-l16'] = {id:'b3-l16', book:3, ar:'بَابُ فَعَّلَ', de:'Verbform II – Ableitungen', gram:'', ex:[], words:[]};
      }
    }""")


def test_selecting_topic_with_deriv_table_starts_table(page, served_app):
    page.goto(served_app)
    _register_b3_l16_topic(page)
    page.evaluate("() => { practiceTopic('b3-l16'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'derivTable')") == True
    m = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'derivTable')")
    assert m["tableIndex"] == 0
    assert m["topicId"] == "b3-l16"
    assert m["studyOnly"] == True  # Entry A ist die studyOnly-Referenzkarte


def test_reselecting_topic_does_not_duplicate_an_unfinished_study_card(page, served_app):
    # Regression (Abschluss-Review 2026-11-13): eine studyOnly-Referenzkarte ist seit makeDerivTable()
    # done:true, OHNE dass die lernende Person etwas getan hat - "done" heißt dort nur "nichts
    # abzufragen". ensureTutorDerivTable(true) (ausdrückliche Themenwahl) wertete das als "Lektion
    # abgeschlossen, darf neu starten" und legte bei jeder weiteren Themenwahl eine zweite, identische
    # Referenzkarte mit einem zweiten Weiter-Knopf in den Chat - zwei Knöpfe, die die Kette doppelt
    # verlängern konnten. Typ 2 hat dieses Loch nicht (dort wird eine Tabelle nur durch echtes
    # Durchspielen done). Erst m.advanced (Klick auf "Weiter") macht eine studyOnly-Karte wirklich
    # erledigt und damit neu startbar.
    page.goto(served_app)
    _register_b3_l16_topic(page)
    page.evaluate("() => { practiceTopic('b3-l16'); practiceTopic('b3-l16'); }")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'derivTable').length") == 1
    assert page.locator("[data-deriv-continue]").count() == 1


def test_finished_chain_can_be_restarted_by_explicit_topic_selection(page, served_app):
    # Gegenprobe zum Test darüber: die Blockade gilt nur, solange die Kette wirklich noch offen ist.
    # Eine komplett durchlaufene Kette (studyOnly-Karte weitergeklickt -> m.advanced, Drill-Tabelle
    # fertig -> m.done) darf auf ausdrücklichen Wunsch neu beginnen, genau wie bei Typ 2.
    page.goto(served_app)
    page.evaluate("""() => {
      TOPIC['mini-deriv'] = {id:'mini-deriv', book:3, ar:'م', de:'Mini', gram:'', ex:[], words:[]};
      DERIV_TABLES['mini-deriv'] = [
        {de:'Nur lesen', columns:['c1'], rows:[{root:'r', values:['r'], given:[true]}]}
      ];
      practiceTopic('mini-deriv');
    }""")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'derivTable').length") == 1
    # Solange nicht weitergeklickt: keine zweite Karte.
    page.evaluate("() => practiceTopic('mini-deriv')")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'derivTable').length") == 1
    # Nach dem Weiter-Klick ist die Kette abgeschlossen (einziger Eintrag) - jetzt darf neu gestartet
    # werden.
    page.evaluate("() => continueDerivTable('tutor', 1)")
    page.evaluate("() => practiceTopic('mini-deriv')")
    assert page.evaluate("() => CHAT.tutor.msgs.filter(m => m.role === 'derivTable').length") == 2


def test_lesson_without_columns_is_skipped_instead_of_crashing_the_chat(page, served_app):
    # Regression (Abschluss-Review 2026-11-13): makeDerivTable() prüfte nur entry.rows, nicht
    # entry.columns. Eine Lektion ohne (oder mit kaputter) columns-Liste lieferte deshalb eine
    # Nachricht statt null; buildDerivTableSteps() gibt für sie zurecht [] zurück, womit die Karte als
    # studyOnly durchging - und msgHTML() stürzte beim Rendern an `m.columns.map(...)` ab
    # ("Cannot read properties of undefined"), was renderChat() abbrach und den ganzen Chat
    # unbenutzbar machte. makeTable() hat denselben Defensiv-Check für entry.cells seit jeher.
    page.goto(served_app)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.evaluate("""() => {
      TOPIC['no-columns'] = {id:'no-columns', book:3, ar:'ك', de:'Ohne Spalten', gram:'', ex:[], words:[]};
      DERIV_TABLES['no-columns'] = [{de:'kaputt', rows:[{root:'r', values:['r'], given:[true]}]}];
      practiceTopic('no-columns');
    }""")
    assert page.evaluate("() => makeDerivTable('no-columns', 0)") is None
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'derivTable')") == False
    # Der Chat rendert weiter (die "Neues Thema"-Notiz ist sichtbar), kein JS-Fehler.
    assert page.locator("#tutor-msgs .note").count() == 1
    assert errors == []


def test_malformed_deriv_table_lesson_is_skipped_without_quiz_fallback(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      TOPIC['broken-deriv'] = {id:'broken-deriv', book:3, ar:'كسر', de:'Kaputte Ableitungslektion', gram:'', ex:[], words:[]};
      DERIV_TABLES['broken-deriv'] = [{de:'kaputt', columns:['A','B'], rows:[]}];
      practiceTopic('broken-deriv');
    }""")
    assert page.evaluate("() => CHAT.tutor.msgs.some(m => m.role === 'derivTable')") == False
    # Kein Durchfallen in die Typ-1-Logik: keine fremde Quizfrage, nur die "Neues Thema"-Notiz - analog zu
    # test_malformed_table_lesson_is_skipped_without_quiz_fallback für Typ 2.
    assert page.evaluate("() => CHAT.tutor.msgs.map(m => m.role)") == ["note"]
    page.evaluate("() => show('tutor')")
    page.evaluate("() => show('tutor')")
    assert page.evaluate("() => CHAT.tutor.msgs.map(m => m.role)") == ["note"]


def test_reload_resumes_deriv_table_mid_phase1(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1));
      renderChat('tutor');
    }""")
    step = page.evaluate("() => { const t = CHAT.tutor.msgs[0]; return t.steps[t.order[t.pos]]; }")
    page.fill(f"#dt-input-0-{step['rowIdx']}-{step['colIdx']}", "غلط1")
    page.click(f'[data-deriv-submit][data-mi="0"][data-ri="{step["rowIdx"]}"][data-ci="{step["colIdx"]}"]')
    page.fill(f"#dt-input-0-{step['rowIdx']}-{step['colIdx']}", "غلط2")
    page.click(f'[data-deriv-submit][data-mi="0"][data-ri="{step["rowIdx"]}"][data-ci="{step["colIdx"]}"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].pos") == 1
    page.reload()
    # CHAT.tutor.msgs wird beim Skript-Start synchron aus localStorage wiederhergestellt (saveChats() lief
    # bereits bei jedem Submit) - kein show('tutor') nötig, um den Zustand selbst zu lesen; show('tutor')
    # würde hier zusätzlich ensureTutorQuiz() auslösen (ctx.topic ist in diesem isolierten Test nie gesetzt)
    # und dadurch eine irrelevante fremde Quizfrage anhängen, ohne die Assertion unten zu beeinflussen.
    assert page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'derivTable').pos") == 1


def test_reload_resumes_exact_shuffle_in_phase2(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      CHAT.tutor.msgs.push(makeDerivTable('b3-l16', 1));
      renderChat('tutor');
    }""")
    n = page.evaluate("() => CHAT.tutor.msgs[0].steps.length")
    for _ in range(n):
        step = page.evaluate("() => { const t = CHAT.tutor.msgs[0]; return t.steps[t.order[t.pos]]; }")
        page.fill(f"#dt-input-0-{step['rowIdx']}-{step['colIdx']}", "غلط1")
        page.click(f'[data-deriv-submit][data-mi="0"][data-ri="{step["rowIdx"]}"][data-ci="{step["colIdx"]}"]')
        page.fill(f"#dt-input-0-{step['rowIdx']}-{step['colIdx']}", "غلط2")
        page.click(f'[data-deriv-submit][data-mi="0"][data-ri="{step["rowIdx"]}"][data-ci="{step["colIdx"]}"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].phase") == 2
    order_before = page.evaluate("() => CHAT.tutor.msgs[0].order")
    page.reload()
    order_after = page.evaluate("() => CHAT.tutor.msgs.find(m => m.role === 'derivTable').order")
    assert order_before == order_after
