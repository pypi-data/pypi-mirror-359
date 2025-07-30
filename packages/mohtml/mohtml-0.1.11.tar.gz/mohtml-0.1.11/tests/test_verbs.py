from mohtml import div, p, br, svg, circle

def test_basic_div_p():
    assert str(div(p("hello"))) == "<div><p>hello</p></div>"

def test_basic_div_p_br():
    assert str(div(p("hello"), br())) == "<div><p>hello</p><br/></div>"

def test_basic_klass():
    assert str(div(p("hello"), klass="foo bar")) == "<div class=\"foo bar\"><p>hello</p></div>"

def test_basic_svg():
    elem = svg(circle(r=10))
    assert str(elem) == '<svg><circle r="10"/></svg>'