def test_order_without_dual(page, served_app):
    page.goto(served_app)
    cells = [
        {"group":"1","gender":None,"num":"pl","pronoun":"نحن","form":"ذهبنا"},
        {"group":"3","gender":"f","num":"sg","pronoun":"هي","form":"ذهبت"},
        {"group":"2","gender":"m","num":"sg","pronoun":"أنت","form":"ذهبت"},
        {"group":"3","gender":"m","num":"sg","pronoun":"هو","form":"ذهب"},
        {"group":"1","gender":None,"num":"sg","pronoun":"أنا","form":"ذهبت"},
        {"group":"2","gender":"f","num":"sg","pronoun":"أنتِ","form":"ذهبتِ"},
    ]
    result = page.evaluate("cells => buildTableSteps(cells)", cells)
    order = [(c["group"], c["gender"], c["num"]) for c in result]
    assert order == [("3","m","sg"), ("3","f","sg"), ("2","m","sg"), ("2","f","sg"), ("1",None,"sg"), ("1",None,"pl")]

# Ridouane (2026-11-20): die Anrede-Dualform (أنتما) ist für m./f. identisch, soll aber trotzdem als ZWEI
# eigene, getrennte Zellen (2,m,du UND 2,f,du) in ihrem jeweiligen Geschlechter-Block erscheinen - Symmetrie
# zur 3. Person, die ja ebenfalls je eine eigene m./f.-Dualzeile hat, auch wenn beide Formen bei "2" am Ende
# gleich aussehen. Ersetzt den früheren gemeinsamen (gender:None) Dual-Platz.
def test_order_with_dual_both_genders(page, served_app):
    page.goto(served_app)
    cells = [
        {"group":"3","gender":"m","num":"sg","pronoun":"هو","form":"ذهب"},
        {"group":"3","gender":"m","num":"du","pronoun":"هما","form":"ذهبا"},
        {"group":"3","gender":"f","num":"du","pronoun":"هما","form":"ذهبتا"},
        {"group":"2","gender":"m","num":"sg","pronoun":"أنت","form":"ذهبت"},
        {"group":"2","gender":"m","num":"du","pronoun":"أنتما","form":"ذهبتما"},
        {"group":"2","gender":"f","num":"du","pronoun":"أنتما","form":"ذهبتما"},
        {"group":"2","gender":"f","num":"sg","pronoun":"أنتِ","form":"ذهبتِ"},
    ]
    result = page.evaluate("cells => buildTableSteps(cells)", cells)
    order = [(c["group"], c["gender"], c["num"]) for c in result]
    assert order == [("3","m","sg"), ("3","m","du"), ("3","f","du"), ("2","m","sg"), ("2","m","du"), ("2","f","sg"), ("2","f","du")]

# Eine alte (gender:None) 2-du-Zelle, wie sie vor dieser Änderung in TABLES stand, darf nicht mehr
# aufgenommen werden - sie passt jetzt in keinen der beiden geschlechtsspezifischen Dual-Plätze mehr.
def test_old_shared_gender_none_dual_no_longer_matches(page, served_app):
    page.goto(served_app)
    cells = [
        {"group":"3","gender":"m","num":"sg","pronoun":"هو","form":"ذهب"},
        {"group":"2","gender":None,"num":"du","pronoun":"أنتما","form":"ذهبتما"},
    ]
    result = page.evaluate("cells => buildTableSteps(cells)", cells)
    order = [(c["group"], c["gender"], c["num"]) for c in result]
    assert order == [("3","m","sg")]
