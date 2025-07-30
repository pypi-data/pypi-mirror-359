from .logger import saferates_log
class SaferatesGuilds:
    def __init__(self, api):
        self.api = api
    def list(self):
        saferates_log("Fetching guilds list")
        return self.api.get("/users/@me/guilds")
    def leave(self, guild_id):
        saferates_log("Leaving guild", f"guild_id={guild_id}")
        return self.api.delete(f"/users/@me/guilds/{guild_id}")
    def join_by_invite(self, invite_code):
        saferates_log("Joining guild via invite", f"invite={invite_code}")
        return self.api.post(f"/invites/{invite_code}")