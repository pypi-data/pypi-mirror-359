class SaferatesFriends:
    def __init__(self, saferates_api):
        self.api = saferates_api
    def add(self, user_id):
        return self.api.put(f"/users/@me/relationships/{user_id}", json={"type": 1})
    def remove(self, user_id):
        return self.api.delete(f"/users/@me/relationships/{user_id}")
    def block(self, user_id):
        return self.api.put(f"/users/@me/relationships/{user_id}", json={"type": 2})
    def unblock(self, user_id):
        return self.api.delete(f"/users/@me/relationships/{user_id}")