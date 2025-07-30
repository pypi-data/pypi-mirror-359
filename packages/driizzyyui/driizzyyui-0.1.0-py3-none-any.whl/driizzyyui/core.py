import httpx
class DriizzyyuiClient:
    API_BASE = "https://discord.com/api/v10"
    def __init__(self, token: str):
        self.token = token
        self.session = httpx.Client(
            headers={
                "Authorization": self.token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
    def fetch_user(self):
        resp = self.session.get(f"{self.API_BASE}/users/@me")
        resp.raise_for_status()
        return resp.json()
    def fetch_channels(self):
        resp = self.session.get(f"{self.API_BASE}/users/@me/channels")
        resp.raise_for_status()
        return resp.json()
    def fetch_messages(self, channel_id: str, limit: int = 10):
        url = f"{self.API_BASE}/channels/{channel_id}/messages?limit={limit}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()
    def send_message(self, channel_id: str, content: str):
        url = f"{self.API_BASE}/channels/{channel_id}/messages"
        payload = {"content": content}
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()