from src.error import InputError, AccessError
import src.exceptions
import json
from src.secret import token_decode
from src.exceptions import token_invalid_id_AccessError, channel_id_invalid_InputError,\
    channel_is_private_AccessError, auth_user_not_channel_member_AccessError,\
    start_number_too_high_InputError
from src.json_edit import access_json, add_to_json, remove_from_json
from src.notifications_helpers import notifications_added
from src.user import users_stats_update, channel_no_finder, involvement_rate_finder

def channel_invite_v2(token, channel_id, u_id):
    '''
    Function that invites user to a channel where token is the person inviting,
    u_id is the person that is invited and channel_id is a valid channel that has been created

    Arguments: 
    token (string) - a encoded string of the auth_user_id and session_id
    channel_id (integer) - an integer created by a channel_create function channel_id 
    used to join specific channels for Dreams.
    u_id (integer) - an integer that identifies the registered invitee user id for Dreams.

    Exceptions:
    InputError - Occurs when the channel_id does not refer to to valid channel
    InputError - Occurs when the u_id is not a valid user
    AccessError - Occurs when the auth_user_id is not a valid user
    AccessError - Occurs when the auth_user_id that is trying to invite someone 
    that is not part of the channel

    '''
    auth_user_id = src.exceptions.token_invalid_id_AccessError(token)
    src.exceptions.channel_id_invalid_InputError(channel_id)
    src.exceptions.user_id_invalid_InputError(u_id)
    src.exceptions.auth_user_not_channel_member_AccessError(token, channel_id)
    
    # 5 Adding the u_id into the channel_id's channel in data.json
    channels = access_json("channels")
    
    for channel in channels:
        if (channel["channel_id"] == channel_id): 
            channel["members_all"].append({"u_id" : u_id})
            
    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)
        DATA["channels"] = channels

        with open('src/data.json', 'w') as FILE:
            json.dump(DATA, FILE)
    notifications_added(auth_user_id, channel_id, -1, u_id)
    users_stats_update()
    
    channel_no_finder(u_id)
    involvement_rate_finder(u_id)
    return {

    }

def channel_details_v2(token, channel_id):
    '''
    Function that provides basic details of a valid channel if the token is already
    apart of that channel

    Arguments: 
    token (string) - encoded string of the auth_user_id and session_id
    channel_id (integer) - an integer created by a channel_create function channel_id 
    used to join specific channels for Dreams.

    Exceptions:
    InputError - Occurs when the channel_id does not refer to to valid channel
    AccessError - Occurs when the auth_user_id that is trying to invite someone 
    that is not part of the channel

    Return Value:
    Returns dictionary { 'name' : tmp_name,
        'is_public' : 'tmp_name'
        'owner_members' : owner_members,
        'all_members' : all_members,} 
    '''
    # 1 
    src.exceptions.token_invalid_id_AccessError(token)
    src.exceptions.channel_id_invalid_InputError(channel_id)
    src.exceptions.auth_user_not_channel_member_AccessError(token, channel_id)
    
    channels = access_json("channels")
    users = access_json("users")

    list_owners = []
    list_members = []
    # Find the designated channel in the data.json
    for channel in channels:
        if (channel["channel_id"] == channel_id):
            tmp_name = channel["name"]
            tmp_public = channel["is_public"]
            tmp_channel = channel
            for user in tmp_channel["members_owner"]:
                list_owners.append(user["u_id"])

            for user in tmp_channel["members_all"]:
                list_members.append(user["u_id"])
           
    # Finds the correct channel
   
    # New dictionaries to store u_id, name_first, name_last permissions
    owner_members = []
    all_members = []
    
    # Appends the user owner id to the owner_members dictionary
    for owner in users:
        tmp_owner = owner["u_id"]
        if tmp_owner in list_owners:
            owner_members.append({'u_id' : tmp_owner, 
                                'name_first' : owner["name_first"],
                                'name_last' : owner["name_last"],
                                'email' : owner["email"],
                                'handle_str' : owner["handle_str"],
                                'profile_img_url': owner["profile_img_url"],
                                })
          
    # Appends the user members id to the member_all dictionary
    for member in users:
        tmp_member = member["u_id"]
        if tmp_member in list_members:
            all_members.append({'u_id' : tmp_member, 
                                'name_first' : member["name_first"],
                                'name_last' : member["name_last"],
                                'email' : member["email"],
                                'handle_str' : member["handle_str"],
                                'profile_img_url': member["profile_img_url"],
                                })  
    # latest merge "hand_str", "user_str"                                                 
    return {
        'name' : tmp_name,
        'is_public' : tmp_public,
        'owner_members' : owner_members,
        'all_members' : all_members,
    }


def channel_messages_v2(token, channel_id, start):

    '''
    Returns a dictionary with messages, start index and end index which are boundary of messages returned. Messages
    are returned based on start index and channel in which messages are sent of which user given is a member of.

    Arguments:
        token (string)      - an encoded string that when decoded contains a dictionary with
            auth_user_id and session_id.
        channel_id (int)    - an unique identifier for a channel
        start (int)         - an index which points to start of messages chronologically

    Exceptions:
        InputError  - Occurs when channel_id is invalid, auth_user_id is invalid, start is greater than total
                        number of messages in channel    
        AccessError - Occurs when user is not a member of channel

    Returns:
        Returns messages
        Returns start
        Returns end
    '''

    u_id = token_invalid_id_AccessError(token)
    channel_id_invalid_InputError(channel_id)
    auth_user_not_channel_member_AccessError(token, channel_id)
    messages_in_channel = start_number_too_high_InputError(start, channel_id, -1)

    messages_length = len(messages_in_channel)

    # sort messages based on time in ascending order
    messages_sorted = sorted(messages_in_channel, key = lambda i: i["time_created"])

    # filter messages based on start index
    messages_filtered = messages_sorted[start:start + 50]

    # set end based on number of messages filtered
    end = start + len(messages_filtered)

    if end == messages_length:
        end = -1

    # add only properties specified in readme to list
    for msg in messages_filtered:
        del msg['channel_id']
        del msg['dm_id']

        for react in msg["reacts"]:
            if u_id in react["u_ids"]:
                react["is_this_user_reacted"] = True
            else:
                react["is_this_user_reacted"] = False

    return {
        "messages": messages_filtered,
        "start": start,
        "end": end
    }

def channel_leave_v1(token, channel_id):
    '''
    Function that removes a user from the channel. If they are an owner 
    they get removed from both the owner_members and members_all lists. If they are a member only 
    they get removed from members_all list

    Arguments: 
    token (string) - a encoded string of the auth_user_id and session_id
    channel_id (integer) - an integer created by a channel_create function channel_id 
    used to join specific channels for Dreams.

    Exceptions:
    InputError - channel_id does not refer to a valid channel.
    AccessError - An AccessError is thrown when the token passed in is not a valid id.
    AccessError - the authorised user is not a member of the channel with channel_id.

    Return:
    {}
    '''
    auth_user_id = src.exceptions.token_invalid_id_AccessError(token)
    src.exceptions.channel_id_invalid_InputError(channel_id)
    src.exceptions.auth_user_not_channel_member_AccessError(token, channel_id)

    channels = access_json("channels")
    
    for channel in channels:
        if channel["channel_id"] == channel_id:  
            # If the user is a owner, remove them from members_owner
            for user in channel["members_owner"]:     
                if user["u_id"] == auth_user_id:
                    channel["members_owner"].remove({"u_id" : auth_user_id})
            
            channel["members_all"].remove({"u_id" : auth_user_id})

    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)
        DATA["channels"] = channels

        with open('src/data.json', 'w') as FILE:
            json.dump(DATA, FILE)

    users_stats_update()
    channel_no_finder(auth_user_id)
    involvement_rate_finder(auth_user_id)
    return {
    }

def channel_join_v2(token, channel_id):
    
    '''
    Adds a user to a channel when given a user id and channel id when
    the channel and user are both valid and the user has permission to
    join the channel

    Arguments:
        token (string)      - an encoded string that when decoded contains a dictionary with
            auth_user_id and session_id.
        channel_id (int)    - a unique identifier for a channel
    '''

    # handle exceptions
    auth_user_id = token_invalid_id_AccessError(token)
    channel_id_invalid_InputError(channel_id)
    channel_is_private_AccessError(channel_id, token)

    # get channel
    channel_select = {}
    channels = access_json("channels")
    for channel in channels:
        if channel["channel_id"] == channel_id:
            channel_select = channel

    # update channel in json by removing from json then adding back
    remove_from_json("channels", channel_select)

    channel_select["members_all"].append({"u_id": auth_user_id})

    add_to_json("channels", channel_select)
    users_stats_update()
    channel_no_finder(auth_user_id)
    involvement_rate_finder(auth_user_id)
    return {}



def channel_addowner_v1(token, channel_id, u_id):
    '''
    Function that adds a valid u_id as a owner of the channel, it is added to the members_owner if 
    the person is already a member. If the person is not a member, they are automatically added to members_all
    and owner_members lists

    Arguments: 
    token (string) - a encoded string of the auth_user_id and session_id
    channel_id (integer) - an integer created by a channel_create function channel_id 
    used to join specific channels for Dreams.
    u_id (integer) - an integer that identifies the registered invitee user id for Dreams.

    Exceptions:
    AccessError - An AccessError is raised when the token passed in is not a valid.
    InputError - channel_id does not refer to a valid channel.
    InputError - user with user id u_id is already an owner of the channel.
    AccessError - the authorised user is not an owner of the Dreams or an owner of this channel.

    Return: 
    {}
    '''
    src.exceptions.token_invalid_id_AccessError(token)
    src.exceptions.channel_id_invalid_InputError(channel_id)
    src.exceptions.user_already_owner_InputError(channel_id, u_id)
    src.exceptions.auth_user_not_owner_AccessError(token, channel_id)
    
    channels = access_json("channels")
    
    # Checking whether the u_id is a member or not in the channel
    is_member = False
    for channel in channels:
        if channel["channel_id"] == channel_id:
            tmp_channel = channel

            for user in tmp_channel["members_all"]:
                if user["u_id"] == u_id:
                    is_member = True

    # Add to members_owner if the person is already in members_all list
    if is_member:
        for channel in channels:
            if channel["channel_id"] == channel_id:
                channel["members_owner"].append({"u_id" : u_id})

    # Add to members_owner and members_all if person is not a member        
    if not is_member:
        for channel in channels:
            if channel["channel_id"] == channel_id:
                channel["members_owner"].append({"u_id" : u_id})
                channel["members_all"].append({"u_id" : u_id})
        channel_no_finder(u_id)
        involvement_rate_finder(u_id)
        users_stats_update()
                
    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)
        DATA["channels"] = channels

        with open('src/data.json', 'w') as FILE:
            json.dump(DATA, FILE)

    return {
    }

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    Function removes an owner from the channel. 
    list.

    Arguments:
    token (string) - a encoded string of the auth_user_id and session_id
    channel_id (integer) - an integer created by a channel_create function channel_id 
    used to join specific channels for Dreams.
    u_id (integer) - an integer that identifies the registered invitee user id for Dreams.

    Exceptions:
    AccessError - An AccessError is raised when the token passed in is not a valid id.
    InputError - channel_id does not refer to a valid channel. 
    InputError - when user with user id u_id is not an owner of the channel.
    AccessError - the authorised user is not an owner of the Dreams or an owner of this channel.
    InputError - user with user id u_id is not an owner of channel

    Return:
    {}

    '''
    src.exceptions.token_invalid_id_AccessError(token)
    src.exceptions.channel_id_invalid_InputError(channel_id)
    src.exceptions.user_not_owner_InputError(u_id, channel_id)
    src.exceptions.user_only_channel_owner_InputError(u_id, channel_id)
    src.exceptions.auth_user_not_owner_AccessError(token, channel_id)
    src.exceptions.user_not_owner_InputError(u_id, channel_id)
    
    channels = access_json("channels")
    
    for channel in channels:
        if channel["channel_id"] == channel_id:
            channel["members_owner"].remove({"u_id" : u_id})
    
    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)
        DATA["channels"] = channels

        with open('src/data.json', 'w') as FILE:
            json.dump(DATA, FILE)

    return {
    }
