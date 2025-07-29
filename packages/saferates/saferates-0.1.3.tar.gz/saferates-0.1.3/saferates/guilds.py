class SaferatesGuilds:
    def __init__(self, saferates_api):
        self.api = saferates_api
    def list(self):
        return self.api.get("/users/@me/guilds")
    def leave(self, guild_id):
        return self.api.delete(f"/users/@me/guilds/{guild_id}")
    def info(self, guild_id):
        return self.api.get(f"/guilds/{guild_id}")
    def channels(self, guild_id):
        return self.api.get(f"/guilds/{guild_id}/channels")