import urllib.parse
import json
def saferates_encode_emoji(emoji):
    if emoji.startswith("<:") or emoji.startswith("<a:"):
        parts = emoji.strip("<>").split(":")
        if len(parts) == 3:
            name, eid = parts[1], parts[2]
            return f"{name}:{eid}"
    return urllib.parse.quote(emoji)
def saferates_pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)