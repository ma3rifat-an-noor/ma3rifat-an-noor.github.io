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

def test_order_with_shared_dual(page, served_app):
    page.goto(served_app)
    cells = [
        {"group":"3","gender":"m","num":"sg","pronoun":"هو","form":"ذهب"},
        {"group":"3","gender":"m","num":"du","pronoun":"هما","form":"ذهبا"},
        {"group":"3","gender":"f","num":"du","pronoun":"هما","form":"ذهبتا"},
        {"group":"2","gender":"m","num":"sg","pronoun":"أنت","form":"ذهبت"},
        {"group":"2","gender":None,"num":"du","pronoun":"أنتما","form":"ذهبتما"},
        {"group":"2","gender":"f","num":"sg","pronoun":"أنتِ","form":"ذهبتِ"},
    ]
    result = page.evaluate("cells => buildTableSteps(cells)", cells)
    order = [(c["group"], c["gender"], c["num"]) for c in result]
    assert order == [("3","m","sg"), ("3","m","du"), ("3","f","du"), ("2","m","sg"), ("2",None,"du"), ("2","f","sg")]
