import httpx
import asyncio
async def send_webhook_async(url: str, content: str, token: str, username: str = None, avatar_url: str = None):
    payload = {"content": content}
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url
    headers = {"Authorization": token}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return resp.text
def send_webhook(url: str, content: str, token: str, username: str = None, avatar_url: str = None):
    return asyncio.run(send_webhook_async(url, content, token, username, avatar_url))
class WebhookClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
    async def send_async(self, content, username=None, avatar_url=None):
        return await send_webhook_async(self.url, content, self.token, username, avatar_url)
    def send(self, content, username=None, avatar_url=None):
        return send_webhook(self.url, content, self.token, username, avatar_url)