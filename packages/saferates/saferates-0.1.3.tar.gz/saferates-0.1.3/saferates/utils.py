import urllib.parse
def saferates_encode_emoji(emoji: str) -> str:
    if emoji.startswith("<:") or emoji.startswith("<a:"):
        parts = emoji.strip("<>").split(":")
        if len(parts) == 3:
            name, eid = parts[1], parts[2]
            return f"{name}:{eid}"
    return urllib.parse.quote(emoji)
def saferates_send_typing(api, channel_id):
    return api.post(f"/channels/{channel_id}/typing")
def saferates_upload_file(api, channel_id, file_path, content=None):
    with open(file_path, "rb") as f:
        files = {'file': (file_path, f)}
        data = {}
        if content:
            data["content"] = content
        return api.post(
            f"/channels/{channel_id}/messages",
            files=files,
            data=data
        )
def saferates_handle_rate_limit_error(response):
    if isinstance(response, dict) and response.get("retry_after"):
        print(f"[saferates] Rate limited! Retry after: {response['retry_after']} seconds.")
        return True
    return False