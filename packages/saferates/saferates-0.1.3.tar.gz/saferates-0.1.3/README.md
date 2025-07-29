# saferates
Developed by: DriizzyyB

> **NOTE:** Automation with user tokens is a ToS violation and will get your account banned.  
> This library is for educational use only.

## Usage

```python
from saferates import (
    SaferatesAPI,
    SaferatesUser,
    SaferatesChannels,
    SaferatesGuilds,
    SaferatesFriends,
    saferates_encode_emoji,
    saferates_upload_file,
)

token = "YOUR_USER_TOKEN"
api = SaferatesAPI(token)

# User
user = SaferatesUser(api)
print(user.profile())
print(user.settings())

# Channels
channels = SaferatesChannels(api)
channels.send_message("CHANNEL_ID", "Hello from saferates! " + saferates_encode_emoji("😄"))
channels.send_file("CHANNEL_ID", "example.png", "Here is an image.")

# Friends
friends = SaferatesFriends(api)
friends.add("USER_ID")

# Guilds
guilds = SaferatesGuilds(api)
print(guilds.list())