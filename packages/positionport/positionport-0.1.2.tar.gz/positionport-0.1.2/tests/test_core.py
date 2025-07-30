from positionport import PositionPortClient

def test_headers():
    client = PositionPortClient("test_key", "test_secret")
    headers = client._auth_headers()
    assert headers["X-API-KEY"] == "test_key"
    assert headers["X-API-SECRET"] == "test_secret"
