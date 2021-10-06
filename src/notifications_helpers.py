from src.json_edit import access_json
import json

def find_handle(auth_user_id):
    # Finds the handle of the author of the message.
    users = access_json("users")
    for user in users:
        if user["u_id"] == auth_user_id:
            author_name = user["handle_str"]
    
    return author_name

def notifications_tag(auth_user_id, channel_id, dm_id, message):
    """
    Used for tagging users in messages in the functions: message_send, message_edit, message_share, message_senddm.

    Arguments:
        auth_user_id (integer) - the user id of the person who has sent the message, used for the notification message.
        channel_id (integer) - the id of the channel where the message was sent to, is -1 when sending to a dm.
        dm_id (integer) - the id of the dm where the message was sent to, is -1 when sending to a channel.
        message (string) - the message being sent with the handles inside, if there are no handles, then no notifications are updated.
    
    Return Value:
        Returns {}
    """
    # The list of group members in the dm/channel depending on whether the 
    # message was sent to a channel (then dm_id is -1) or dm, starts empty.
    group_members = []
    if channel_id != -1:
        channels = access_json("channels")
        for channel in channels:
            if channel["channel_id"] == channel_id:
                group_name = channel["name"]
                for member in channel["members_all"]:
                    group_members.append(member["u_id"])
    else:
        dms = access_json("dms")
        for dm in dms:
            if dm["dm_id"] == dm_id:
                group_name = dm["dm_name"]
                for member in dm["members_all"]:
                    group_members.append(member["u_id"])

    # Splits the message up into words to check if there are handles to tag.
    message_list = message.split()
    # The list of users tagged in the message, starts empty.
    tagged_list = []
    users = access_json("users")

    # Goes through each word in the message and checks if the handle 
    # corresponds to a user in the dm/channel and if so, adds to the
    #  tagged_list.
    for word in message_list:
        if word.startswith("@"):
            handle_str = word[1:]
            user_found = False
            user_id = -1
            for user in users:
                if user["handle_str"] == handle_str:
                    user_found = True
                    user_id = user["u_id"]
            if user_found and user_id in group_members:
                tagged_list.append(user_id)
    
    # Finds the handle of the author of the message.
    author_name = find_handle(auth_user_id)
    
    # Updates the notifications of the user(s) who have been tagged.
    for u_id in tagged_list:
        for user in users:
            if u_id == user["u_id"]:
                user["notifications"].insert(0, {
                    "channel_id": channel_id,
                    "dm_id": dm_id,
                    "notification_message": f"{author_name} tagged you in {group_name}: {message[:20]}"
                })
    
    with open('src/data.json', 'r+') as FILE:
        DATA = json.load(FILE)

        DATA["users"] = users
    
    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)
    
    return {}

def find_group_name(channel_id, dm_id):
    # Finds the name of the channel/dm.
    if channel_id != -1:
        channels = access_json("channels")
        for channel in channels:
            if channel["channel_id"] == channel_id:
                group_name = channel["name"]
    else:
        dms = access_json("dms")
        for dm in dms:
            if dm["dm_id"] == dm_id:
                group_name = dm["dm_name"]
    
    return group_name

def notifications_added(auth_user_id, channel_id, dm_id, u_id):
    """
    Used for notifying users being added to channels or dms in the functions: channel_invite, dm_invite, dm_create.

    Arguments:
        auth_user_id (integer) - the user id of the person who has added the new user, used for the notification message.
        channel_id (integer) - the id of the channel where the user was added to, is -1 when user is added to a dm.
        dm_id (integer) - the id of the dm where the user was added to, is -1 when the user is added to a channel.
        u_id (integer) - the id of the user being added to the channel/dm - who gets notified.

    Return Value:
        Returns {}
    """
    users = access_json("users")
    # Finds the handle of the author of the message.
    author_name = find_handle(auth_user_id)
    
    group_name = find_group_name(channel_id, dm_id)
    # Adds the notification to the user's notifications and dumps it to the
    #  data.json.
    for user in users:
        if user["u_id"] == u_id:
            user["notifications"].insert(0, {
                    "channel_id": channel_id,
                    "dm_id": dm_id,
                    "notification_message": f"{author_name} added you to {group_name}"
                })
    
    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)

        DATA["users"] = users
    
    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)
    
    return {}

def notifications_react(u_id, message_dict):
    """
    Used for notifications for reacting to a message - used in message_react

    Arguments:
        u_id (integer) - the user id of the person who has reacted to the message.
        message_dict (dict) - a dictionary containing the details of the message.
    
    Return Value:
        Returns {}
    """
    users = access_json("users")

    # Finds the auth_user_id of the writer of the message, the channel_id and dm_id of where the message was sent to.
    auth_user_id = message_dict["u_id"]
    channel_id = message_dict["channel_id"]
    dm_id = message_dict["dm_id"]
    
    # Finds the name of the group and the author's_handle.
    group_name = find_group_name(channel_id, dm_id)
    reactor_name = find_handle(u_id)

    # Inserts a notification into the user with the react message.
    for user in users:
        if user["u_id"] == auth_user_id:
            user["notifications"].insert(0, {
                    "channel_id": channel_id,
                    "dm_id": dm_id,
                    "notification_message": f"{reactor_name} reacted to your message in {group_name}"
                })
    
    # Saves it to data.json.
    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)

        DATA["users"] = users
    
    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)
    
    return {}