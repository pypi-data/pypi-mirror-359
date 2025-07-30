import requests

class PositionPortClient:
    def __init__(self, public_key: str, secret_key: str):
        self.base_url = "https://api.positionport.com/external"
        self.public_key = public_key
        self.secret_key = secret_key 

    def _auth_headers(self):
        return {
            "X-API-KEY": self.public_key,
            "X-API-SECRET": self.secret_key
        }

    def start_binance_tracking(self):
        res = requests.get(f"{self.base_url}/binance/start-tracking", headers=self._auth_headers())
        res.raise_for_status()
        return res.json()

    def stop_binance_tracking(self):
        res = requests.get(f"{self.base_url}/binance/stop-tracking", headers=self._auth_headers())
        res.raise_for_status()
        return res.json()
