from positionport import say_hello

def test_say_hello(capfd):
    say_hello()
    out, err = capfd.readouterr()
    assert out.strip() == "Hello PositionPort"