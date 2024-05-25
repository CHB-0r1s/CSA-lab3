from translator import text2terms


def test_text2terms():
    text = "( + 1 ( + 2 3 ) )"
    terms = text2terms(text)
    assert terms == ['(', '+', '1', '(', '+', '2', '3', ')', ')']
