# Hinweis: #v-tutor ist per `hidden`-Attribut ausgeblendet, solange currentView != 'tutor'. Playwrights
# fill()/click() verlangen ein sichtbares Element. tests/test_table_submit.py und tests/test_table_phases.py
# erreichen das per `location.hash = 'tutor'` (triggert hashchange->route()->show('tutor')). Für DIESE
# Testdatei funktioniert das nicht: show('tutor') ruft bei aktivem Sparmodus (Standardeinstellung,
# S.settings.mode === 'offline') ensureTutorQuiz() auf, und die schiebt automatisch eine zusätzliche
# role:'quiz'-Nachricht NACH der zuletzt gepushten Tabellennachricht, sobald die letzte Nachricht nicht
# schon eine unbeantwortete quiz ist (siehe Kommentar bei submitTableCell() in madina-arabisch.html, der
# genau dieses Verhalten bereits als Grund nennt, warum dort über role:'table' statt über die letzte
# Chat-Nachricht gesucht wird). Empirisch bestätigt: nach `location.hash='tutor'` + Tabellen-Push liegt
# CHAT.tutor.msgs kurz darauf bei ['table', 'quiz'] - das würde jede index-basierte Assertion auf
# msgs[1]/msgs.length in diesem Kettentest verfälschen (die eingekettete Verkettungs-Nachricht landet dann
# bei Index 2 statt 1, bzw. msgs.length wäre 3 statt 2). Deshalb wird die Tutor-Ansicht hier stattdessen
# direkt per `#v-tutor`.hidden = false sichtbar gemacht, ohne über route()/show() zu gehen - das reicht für
# Playwrights fill()/click() (der globale Klick-Handler für [data-table-submit] prüft currentView nicht)
# und löst ensureTutorQuiz() nicht aus. Ändert nichts an den in der Aufgabenbeschreibung vorgegebenen
# Assertions/Funktionsaufrufen, nur an der Testumgebungs-Voraussetzung für Sichtbarkeit.

def test_second_verb_starts_automatically(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      TABLES['test-chain'] = [
        {verb:'أ', tense:'madi', de:'Test A', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'أ1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'أ2'}]},
        {verb:'ب', tense:'madi', de:'Test B', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'ب1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'ب2'}]}
      ];
      CHAT.tutor.msgs.push(makeTable('test-chain', 0)); renderChat('tutor');
    }""")
    # Phase 1 + Phase 2 von Verb A, je 2 Zellen (4 Submits insgesamt). Die Vorlage im Brief übergibt dafür
    # die hart codierte Formenliste ["أ1","أ2","أ1","أ2"] - das ist aber gegen den echten shuffle() in
    # madina-arabisch.html (Math.random(), siehe Phasenübergang in submitTableCell()) nicht deterministisch:
    # bei nur 2 Zellen vertauscht Phase 2 die Reihenfolge mit 50% Wahrscheinlichkeit, wodurch die zweite
    # hart codierte Form (z. B. "أ1") auf die falsche, inzwischen umsortierte Zelle träfe (ein Fehlversuch,
    # der die 4 Submits nicht mehr bis zum fertigen Done-Zustand reichen lässt und den Test ca. jeden
    # zweiten Lauf durchfallen ließe - empirisch beim ersten Testlauf hier tatsächlich beobachtet). Deshalb
    # wie in tests/test_table_phases.py die tatsächlich erwartete Form bei jedem Schritt live aus
    # steps[order[pos]] lesen statt sie vorab zu raten; das ändert nichts an den vorgegebenen Assertions.
    for _ in range(4):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[1].verb") == "ب"
    assert page.evaluate("() => CHAT.tutor.msgs[1].verbIndex") == 1

def test_note_shown_after_last_verb_in_chain(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      TABLES['test-chain-single'] = [{verb:'أ', tense:'madi', de:'Test A', cells:[
        {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'أ1'},
        {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'أ2'}]}];
      CHAT.tutor.msgs.push(makeTable('test-chain-single', 0)); renderChat('tutor');
    }""")
    # Siehe Kommentar in test_second_verb_starts_automatically oben: Form live aus steps[order[pos]] lesen
    # statt hart codiert zu raten, da Phase 2 bei 2 Zellen mit 50% Wahrscheinlichkeit umsortiert wird.
    for _ in range(4):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "note"

# Regressionstest für den vom Controller gefundenen Bug in submitTableCell(): die Message-Suche lief über
# ctx.msgs.find(x => x.role === 'table'), was IMMER die erste role:'table'-Nachricht im Array trifft. Sobald
# durch die Verkettung oben eine zweite role:'table'-Nachricht (Verb B) nach der ersten (Verb A, jetzt done)
# angehängt wird, gibt es zwei solche Nachrichten gleichzeitig in ctx.msgs — .find() liefert weiterhin Verb
# A's (fertige, "done") Nachricht. Jeder weitere Submit für Verb B würde dann an der falschen, bereits
# abgeschlossenen Message-Objekt vorbei ins Leere laufen (die done-Prüfung in submitTableCell() greift
# sofort, m.pos von Verb B bleibt für immer bei 0 stehen) - ohne Fehler, ohne Crash, einfach unspielbar.
# (Seit dem Abschluss-Review adressiert submitTableCell() die Nachricht direkt über ihren Index in
# ctx.msgs - data-qi/#t-input-<index> -, statt sie über role/Position zu suchen; Verb B ist msgs[1] und
# wird deshalb unten über "#t-input-1" / [data-qi="1"] bedient.)
# Dieser Test vervollständigt Verb A komplett (Phase 1 + Phase 2, wie in den beiden Tests oben), reicht dann
# eine KORREKTE Antwort für Verb B's erste Zelle ein und prüft, dass CHAT.tutor.msgs[1].pos tatsächlich
# vorrückt - das beweist, dass der Submit gegen Verb B's Nachricht gewertet wurde, nicht gegen Verb A's
# veraltete. Die Form wird dynamisch aus Verb B's eigenen Daten gelesen (nicht hart codiert), damit dieser
# Test unabhängig vom Zufalls-Shuffle in Verb A's Phase 2 deterministisch bleibt.
def test_submit_after_chain_grades_new_verb_not_stale_one(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      TABLES['test-chain-regression'] = [
        {verb:'أ', tense:'madi', de:'Test A', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'أ1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'أ2'}]},
        {verb:'ب', tense:'madi', de:'Test B', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'ب1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'ب2'}]}
      ];
      CHAT.tutor.msgs.push(makeTable('test-chain-regression', 0)); renderChat('tutor');
    }""")
    # Verb A komplett durchspielen: Phase 1 + Phase 2, jeweils mit der tatsächlich erwarteten Form
    # (nicht hart codiert), damit der Zufalls-Shuffle in Phase 2 den Testlauf nicht verfälschen kann.
    for _ in range(4):
        if page.evaluate("() => CHAT.tutor.msgs[0].done"):
            break
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
    # Verb B's Tabelle steht jetzt an msgs[1], frisch (Phase 1, pos 0). Eine korrekte Antwort für ihre
    # erste Zelle einreichen und prüfen, dass msgs[1].pos vorrückt - vor dem Lookup-Fix würde
    # submitTableCell() hier immer noch Verb A's (done) Nachricht finden und sofort No-Op zurückkehren,
    # msgs[1].pos bliebe bei 0 stehen.
    assert page.evaluate("() => CHAT.tutor.msgs[1].pos") == 0
    pos_b = page.evaluate("() => CHAT.tutor.msgs[1].pos")
    step_b = page.evaluate(f"() => CHAT.tutor.msgs[1].steps[CHAT.tutor.msgs[1].order[{pos_b}]]")
    page.fill("#t-input-1", step_b["form"])
    page.click('[data-table-submit][data-qi="1"]')
    assert page.evaluate("() => CHAT.tutor.msgs[1].pos") == 1

# Regressionstest für den Null-Push-Bug in submitTableCell(): die Verkettungslogik prüfte bisher nur, ob
# TABLES[m.topicId][m.verbIndex + 1] EXISTIERT, nicht, ob makeTable() dafür tatsächlich eine gültige
# Tabellennachricht liefert. makeTable() gibt laut seinem eigenen Kommentar null zurück, wenn cells zwar
# gefüllt ist, aber keine Zelle in einen der festen Buckets von buildTableSteps() passt (z. B. ein
# Tippfehler bei group/gender/num). Ohne den Fix würde dieses null direkt in ctx.msgs gepusht, und
# msgHTML(null, ...) stürzt beim Lesen von m.role ab, weil es keine Null-Prüfung hat - der Chat-Render
# würde noch vor saveChats() crashen und das Problem damit bei jedem Reload wiederholen. Verb B hat hier
# absichtlich nur Zellen mit group/num-Werten, die in keinem Eintrag der Bucket-Liste in buildTableSteps()
# vorkommen, sodass buildTableSteps() eine leere Liste liefert und makeTable() laut seinem !steps.length-
# Guard null zurückgibt. Verb A wird komplett durchgespielt (Phase 1 + Phase 2); danach darf die App nicht
# abstürzen, und statt Verb B's (nicht existenter) Tabelle muss dieselbe Abschluss-Notiz erscheinen, die
# auch test_note_shown_after_last_verb_in_chain oben nach dem letzten Verb einer Kette erwartet.
def test_malformed_next_verb_shows_note_instead_of_crashing(page, served_app):
    page.goto(served_app)
    page.evaluate("""() => {
      document.querySelector('#v-tutor').hidden = false;
      TABLES['test-chain-malformed'] = [
        {verb:'أ', tense:'madi', de:'Test A', cells:[
          {group:'3',gender:'m',num:'sg',pronoun:'هو',form:'أ1'},
          {group:'1',gender:null,num:'sg',pronoun:'أنا',form:'أ2'}]},
        {verb:'ب', tense:'madi', de:'Test B (kaputt)', cells:[
          {group:'9',gender:'x',num:'bad',pronoun:'؟',form:'ب1'}]}
      ];
      CHAT.tutor.msgs.push(makeTable('test-chain-malformed', 0)); renderChat('tutor');
    }""")
    # Verb A komplett durchspielen: Phase 1 + Phase 2, mit der tatsächlich erwarteten Form (nicht hart
    # codiert), da der Zufalls-Shuffle in Phase 2 bei 2 Zellen die Reihenfolge vertauschen kann (siehe
    # Kommentar in test_second_verb_starts_automatically oben).
    for _ in range(4):
        pos = page.evaluate("() => CHAT.tutor.msgs[0].pos")
        step = page.evaluate(f"() => CHAT.tutor.msgs[0].steps[CHAT.tutor.msgs[0].order[{pos}]]")
        page.fill("#t-input-0", step["form"])
        page.click('[data-table-submit][data-qi="0"]')
    assert page.evaluate("() => CHAT.tutor.msgs[0].done") == True
    assert page.evaluate("() => CHAT.tutor.msgs.length") == 2
    assert page.evaluate("() => CHAT.tutor.msgs[1].role") == "note"
