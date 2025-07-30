from saferates import (
    SaferatesAPI, SaferatesAccount, SaferatesMessaging, SaferatesDMs,
    SaferatesFriends, SaferatesGuilds, SaferatesReactions,
    saferates_pretty_json, saferates_log
)

def prompt(msg, required=True):
    value = input(msg)
    while required and not value.strip():
        value = input(msg)
    return value.strip()

def menu_account(account):
    while True:
        print("\n--- Account Menu ---")
        print("1. Show profile")
        print("2. Change username")
        print("3. Change custom status")
        print("4. Back")
        choice = prompt("Select option: ")
        if choice == "1":
            profile = account.get_profile()
            print(saferates_pretty_json(profile))
        elif choice == "2":
            newname = prompt("New username: ")
            password = prompt("Current password: ")
            print(account.change_username(newname, password))
        elif choice == "3":
            status = prompt("New custom status: ")
            print(account.set_status(status))
        elif choice == "4":
            return

def menu_messaging(messaging):
    while True:
        print("\n--- Messaging Menu ---")
        print("1. Send message")
        print("2. Edit message")
        print("3. Delete message")
        print("4. Bulk delete messages")
        print("5. Crosspost message")
        print("6. Pin message")
        print("7. Unpin message")
        print("8. Back")
        choice = prompt("Select option: ")
        if choice == "1":
            channel_id = prompt("Channel ID: ")
            content = prompt("Message content: ")
            print(messaging.send_message(channel_id, content))
        elif choice == "2":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            new_content = prompt("New content: ")
            print(messaging.edit_message(channel_id, msg_id, new_content))
        elif choice == "3":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            print(messaging.delete_message(channel_id, msg_id))
        elif choice == "4":
            channel_id = prompt("Channel ID: ")
            ids = prompt("Comma-separated message IDs: ").split(",")
            ids = [x.strip() for x in ids if x.strip()]
            print(messaging.bulk_delete(channel_id, ids))
        elif choice == "5":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            print(messaging.crosspost_message(channel_id, msg_id))
        elif choice == "6":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            print(messaging.pin_message(channel_id, msg_id))
        elif choice == "7":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            print(messaging.unpin_message(channel_id, msg_id))
        elif choice == "8":
            return

def menu_dms(dms):
    while True:
        print("\n--- DM Menu ---")
        print("1. List DM channels")
        print("2. Send DM")
        print("3. Back")
        choice = prompt("Select option: ")
        if choice == "1":
            print(saferates_pretty_json(dms.list_dm_channels()))
        elif choice == "2":
            user_id = prompt("Recipient user ID: ")
            content = prompt("Message: ")
            print(dms.send_dm(user_id, content))
        elif choice == "3":
            return

def menu_friends(friends):
    while True:
        print("\n--- Friends Menu ---")
        print("1. Add friend")
        print("2. Remove friend")
        print("3. Block user")
        print("4. Unblock user")
        print("5. Back")
        choice = prompt("Select option: ")
        if choice == "1":
            user_id = prompt("User ID: ")
            print(friends.add(user_id))
        elif choice == "2":
            user_id = prompt("User ID: ")
            print(friends.remove(user_id))
        elif choice == "3":
            user_id = prompt("User ID: ")
            print(friends.block(user_id))
        elif choice == "4":
            user_id = prompt("User ID: ")
            print(friends.unblock(user_id))
        elif choice == "5":
            return

def menu_guilds(guilds):
    while True:
        print("\n--- Guilds Menu ---")
        print("1. List my guilds")
        print("2. Leave guild")
        print("3. Join by invite code")
        print("4. Back")
        choice = prompt("Select option: ")
        if choice == "1":
            print(saferates_pretty_json(guilds.list()))
        elif choice == "2":
            guild_id = prompt("Guild ID: ")
            print(guilds.leave(guild_id))
        elif choice == "3":
            invite = prompt("Invite code (e.g. dQw4w9f): ")
            print(guilds.join_by_invite(invite))
        elif choice == "4":
            return

def menu_reactions(reactions):
    while True:
        print("\n--- Reactions Menu ---")
        print("1. React to message")
        print("2. Remove reaction")
        print("3. Back")
        choice = prompt("Select option: ")
        if choice == "1":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            emoji = prompt("Emoji (unicode or custom): ")
            print(reactions.react(channel_id, msg_id, emoji))
        elif choice == "2":
            channel_id = prompt("Channel ID: ")
            msg_id = prompt("Message ID: ")
            emoji = prompt("Emoji (unicode or custom): ")
            print(reactions.unreact(channel_id, msg_id, emoji))
        elif choice == "3":
            return

def main():
    print("=== saferates Discord Tool ===")
    token = prompt("Enter your Discord user token: ")
    api = SaferatesAPI(token)
    account = SaferatesAccount(api)
    messaging = SaferatesMessaging(api)
    dms = SaferatesDMs(api)
    friends = SaferatesFriends(api)
    guilds = SaferatesGuilds(api)
    reactions = SaferatesReactions(api)
    while True:
        print("\n=== Main Menu ===")
        print("1. Account actions")
        print("2. Messaging")
        print("3. Direct Messages")
        print("4. Friends")
        print("5. Guilds")
        print("6. Reactions")
        print("7. Exit")
        choice = prompt("Select option: ")
        if choice == "1":
            menu_account(account)
        elif choice == "2":
            menu_messaging(messaging)
        elif choice == "3":
            menu_dms(dms)
        elif choice == "4":
            menu_friends(friends)
        elif choice == "5":
            menu_guilds(guilds)
        elif choice == "6":
            menu_reactions(reactions)
        elif choice == "7":
            print("Goodbye from saferates!")
            break

if __name__ == "__main__":
    main()