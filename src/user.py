from src.error import AccessError, InputError
from src.secret import token_encode, token_decode
from src.json_edit import access_json, add_to_json
import json
from src.exceptions import token_invalid_id_AccessError, name_length_incorrect_InputError, email_repeat_InputError, email_invalid_InputError, handle_length_incorrect_InputError, handle_repeat_InputError, user_id_invalid_InputError, img_url_not_jpg_InputError, img_dimensions_invalid_InputError, img_url_not_success_InputError
import uuid
from datetime import datetime, timezone
import urllib.request
from PIL import Image
import os
from src import config

def user_profile_v2(token, u_id):
    """
    Creates a user dictionary for a valid user, based on the user id, containing u_id, email, first name, last name and handle.  
    Returns the user dictionary. 

    Arguments:
        token (string) - the token of the user who is requesting this function.
        u_id (int) - the user's id whom the user dictionary is based on.

    Exceptions:
        AccessError - Occurs when a matching token is not found in the data.json file after a function searches for a match in the users list.
        InputError - Occurs when a valid u_id is not found in the database (data.json).
   
    Return Value:
        Returns the 'user' profile dicitonary containing u_id, email, first name, last name and handle
        in the format:
        {"user": 
        {
            "u_id": <int>,
            "email": <string>,
            'name_first': <string>,
            'name_last': <string>,
            "handle_str": <string>,
            'profile_img_url': <string>
        },   
    }
    """
    #Checks for validity of the user
    token_invalid_id_AccessError(token)
    user_id_invalid_InputError(u_id)


    #Loops to find where user is in users dictionary and creates profile dictionary 
    users = access_json("users")
    for user in users:  
        if u_id == user["u_id"]: 
            user_profile = {}
            user_profile["u_id"] = user["u_id"]
            user_profile["email"] = user["email"]
            user_profile["name_first"] = user["name_first"]
            user_profile["name_last"] = user["name_last"]
            user_profile["handle_str"] = user["handle_str"]
            user_profile["profile_img_url"] = user["profile_img_url"]
 
    user_profile_dict = {"user": user_profile} 

    #Returns new dictionary associated with token
    return user_profile_dict



def user_profile_setname_v2(token, name_first, name_last):
    """
    For a valid user, updates the first and/or last name and changes the data.json file.  

    Arguments:
        token (string) - the token of the user who is requesting this function.
        name_first (string) - the new first name of the user.
        name_last (string) - the new last name of the user.

     Exceptions:
        AccessError - Occurs when a matching token is not found in the data.json file after a function searches for a match in the users list.
        InputError - Occurs when the name_first paramter is not between 1 and 50 characters inclusively in length.
        InputError - Occurs when the name_last paramter is not between 1 and 50 characters inclusively in length.

    Return Value:
        Returns {}
    """
    #Checks for validity of token 
    auth_user_id = token_invalid_id_AccessError(token)

    #Checks for InputError in names
    name_length_incorrect_InputError(name_first, name_last)
    
    #Sets new name
    with open('src/data.json', 'r') as FILE: 
        DATA = json.load(FILE)
        for user in DATA["users"]:
            if user["u_id"] == auth_user_id:
                user["name_first"] = name_first 
                user["name_last"] = name_last

    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)

    return {
    }



def user_profile_setemail_v2(token, email):
    """
    For a valid user, updates the email of the user while changing the data.json file.  

    Arguments:
        token (string) - the token of the user who is requesting this function.
        email (string) - the new email of the user.

    Exceptions:
        AccessError - Occurs when a matching token is not found in the data.json file after a function searches for a match in the users list.
        InputError - Occurs when the email paramater is not valid based on the rules provided. 
        InputError - Occurs when the email paramter is already in use by another user. 

    Return Value:
        Returns {}
    """

    #Checks for validity of token 
    auth_user_id = token_invalid_id_AccessError(token)

    #Checks if email entered is a valid email type 
    email_invalid_InputError(email)

    #Checks if email entered is already taken by other user 
    email_repeat_InputError(email)

    #Sets new email
    with open('src/data.json', 'r') as FILE: 
        DATA = json.load(FILE)
        for user in DATA["users"]:
            if user["u_id"] == auth_user_id:
                user["email"] = email
                
    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)

    return {
    }
    
    

def user_profile_sethandle_v1(token, handle_str):
    """
    For a valid user, updates the handle of the user while changing the data.json file.  

    Arguments:
        token (string) - the token of the user who is requesting this function.
        handle_str (string) - the new handle of the user.

    Exceptions:
        AccessError - Occurs when a matching token is not found in the data.json file after a function searches for a match in the users list.
        InputError - Occurs when the handle_str paramater is not between 3 and 20 characters inclusive. 
        InputError - Occurs when the handle_str paramter is already in use by another user. 

    Return Value:
        Returns {}
    """
    #Checks for validity of token 
    auth_user_id = token_invalid_id_AccessError(token)

    #Checks if handle is valid 
    handle_length_incorrect_InputError(handle_str)

    #Checks if handle is already in use by another person 
    handle_repeat_InputError(handle_str)

    #Sets new handle
    with open('src/data.json', 'r') as FILE: 
        DATA = json.load(FILE)
        for user in DATA["users"]:
            if user["u_id"] == auth_user_id:
                user["handle_str"] = handle_str
                
    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)

    return {
    }



def users_all_v1(token):
    """
    After taking in a valid token, creates a users dictionary (dictionary containing list of dictionairies) containing the user id, containing u_id, email, first name, 
    last name and handles of all the users. Returns the users dictionary. 

    Arguments:
        token (string) - the token of the user who is requesting this function.

    Exceptions:
        AccessError - Occurs when a matching token is not found in the data.json file after a function searches for a match in the users list.

    Return Value:
        Returns the users dicitonary containing u_id, email, first name, last name and handles of all users
        in the format:
        {"users": [
        {
            "u_id": <int>,
            "email": <string>,
            'name_first': <string>,
            'name_last': <string>,
            "handle_str": <string>,
            "profile_img_url": <string>,
        },   
    ]}
    """

    #Checks for validity of the user
    token_invalid_id_AccessError(token)

    #Loops to find where user is in users dictionary and creates profile dictionary 
    users_list = []

    users = access_json("users")
    for user in users:  
        user_profile = {}
        user_profile["u_id"] = user["u_id"]
        user_profile["email"] = user["email"]
        user_profile["name_first"] = user["name_first"]
        user_profile["name_last"] = user["name_last"]
        user_profile["handle_str"] = user["handle_str"]
        user_profile["profile_img_url"] = user["profile_img_url"]

        users_list.append(user_profile)
 
    users_all_dict = {"users": users_list} 

    #Returns new dictionary associated with token
    return users_all_dict

def users_stats_initialise():
    """
    When clear/v1 activates, initialises the dreams stats with starting values for 
    num_channels_exist, num_dms_exist, num_messages exist and the timestamp.
    """
    dt = datetime.now(timezone.utc)
    time_created = dt.replace(tzinfo=timezone.utc).timestamp()

    dreams_stats = {
        'channels_exist': [{
            'num_channels_exist': 0, 
            'time_stamp': time_created
        }],
        'dms_exist': [{
            'num_dms_exist': 0, 
            'time_stamp': time_created
        }], 
        'messages_exist': [{
            'num_messages_exist': 0, 
            'time_stamp': time_created
        }], 
        'utilization_rate': 0.0
    }

    with open('src/data.json', 'r') as FILE: 
        DATA = json.load(FILE)
        DATA["dreams_stats"] = dreams_stats

    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)


def find_utilization_rate():
    """
    Finds the utilization rate by calculating the total number of users and 
    calculating the number of users not in any channels or dms, subtracting 
    that from the total amount of users to find those who have joined at least
    one channel or dm and divides this number by the total number of users.

    Return Values:
        Returns a float of the utilization rate.
    """
    users = access_json("users")
    channels = access_json("channels")
    dms = access_json("dms")
    total_num_users = len(users)

    count = 0

    for user in users:
        found = False
        for channel in channels:
            for channel_m in channel["members_all"]:
                if user["u_id"] == channel_m["u_id"]:
                    found = True

        for dm in dms:
            for dm_m in dm["members_all"]:
                if user["u_id"] == dm_m["u_id"]:
                    found = True
        
        if found == False:
            count += 1
    
    count_user_not_in_channel = count
    num_users_who_have_joined_at_least_one_channel_or_dm = (total_num_users - count_user_not_in_channel)

    try:
        return float(num_users_who_have_joined_at_least_one_channel_or_dm / total_num_users)
    except:
        return float(0.0)


def users_stats_update(channels=False, dms=False, messages=False):
    """
    Updates the dreams_stats data in the dictionary with the data necessary 
    based on whether channels, dms or messages need to be updated and updates 
    the utilization rate to the data.json file.

    Arguments:
        channels (bool) - checks if it should be updating the dreams stats for channels.
        dms (bool) - checks if it should be updating the dreams stats for dms.
        messages (bool) - checks if it should be updating the dreams stats for messages.

    """
    dt = datetime.now(timezone.utc)
    time_created = dt.replace(tzinfo=timezone.utc).timestamp()
    dreams_stats = access_json("dreams_stats")

    if channels:
        channels_list = access_json("channels")
        num_channels_exist = len(channels_list)

        dreams_stats["channels_exist"].append({
            "num_channels_exist": num_channels_exist,
            "time_stamp": time_created
        })

    if dms:
        dms_list = access_json("dms")
        num_dms_exist = len(dms_list)

        dreams_stats["dms_exist"].append({
            "num_dms_exist": num_dms_exist,
            "time_stamp": time_created
        })
    
    if messages:
        messages_list = access_json("messages")
        num_messages_exist = len(messages_list)

        dreams_stats["messages_exist"].append({
            "num_messages_exist": num_messages_exist,
            "time_stamp": time_created
        })
    
    dreams_stats["utilization_rate"] = find_utilization_rate()

    with open('src/data.json', 'r') as FILE: 
        DATA = json.load(FILE)
        DATA["dreams_stats"] = dreams_stats

    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)

def users_stats_v1(token):
    """
    Gets the users (dreams) overall stats at that moment with the data of 
    number of messages, dms, channels and utilization rate.

    Arguments:
        token (string) - used for checking if the user has valid u_id and session_id.

    Exceptions:
        AccessError - Occurs when the token provided is invalid.
    
    Return Value:
        Returns a dictionary with the dreams_stats in the form:
        {
            dreams_stats: {
                'channels_exist': [{num_channels_exist, time_stamp}], 
                'dms_exist': [{num_dms_exist, time_stamp}], 
                'messages_exist': [{num_messages_exist, time_stamp}], 
                'utilization_rate': <float>
            }
        }
    """
    token_invalid_id_AccessError(token)
    
    return {
        "dreams_stats" : access_json("dreams_stats")
    }

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """
    Allows the user to upload a profile picture, given a url on the internet and crops it to the specified area.

    Arguments:
        token (string) - the token of the user who's profile picture wants to be changed.
        img_url (sring) - the url of the picture that the user wants to change to.
        x_start (int) - the first x-coordinate to crop to (from the left).
        y_start (int) - the first y-coordinate to crop to (from the top).
        x_end (int) - the second x-coordinate to crop to (from the left).
        y_end (int) - the second y-coordinate to crop to (from the top).
    
    Exceptions:
        InputError - Occurs when img_url returns an HTTP status other than 200, any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL or if the image uploaded is not a JPG.
        AccessError - Occurs when the token provided is invalid.
    
    Return Value:
        Returns {}
    """

    # Checks the exceptions related to the function.
    u_id = token_invalid_id_AccessError(token)
    
    img_url_not_success_InputError(img_url)
    img_url_not_jpg_InputError(img_url)
    img_dimensions_invalid_InputError(img_url, x_start, y_start, x_end, y_end)
    
    profile_id = int(str(uuid.uuid1().int)[0:15])
    # Retrieves the image and saves it if it passes the exceptions.
    urllib.request.urlretrieve(img_url, f"src/static/{profile_id}.jpg")

    # Crops the image and saves the cropped version.
    imageObject = Image.open(f"src/static/{profile_id}.jpg")
        
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(f"src/static/{profile_id}.jpg")

    # Updates the user's profile_img_url with the new link to the photo.
    users = access_json("users")
    for user in users:
        if user["u_id"] == u_id:
            user["profile_img_url"] = f'{config.url}static/{profile_id}.jpg'
    
    with open('src/data.json', 'r') as FILE: 
        DATA = json.load(FILE)
        DATA["users"] = users

    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)
    
    return {}

def channel_no_finder(u_id, update_stats=True):
    #finding no of channels the user is a part of + the number of total channels:
    dt = datetime.now(timezone.utc)
    time_created = dt.replace(tzinfo=timezone.utc).timestamp()

    channels_part = 0
    channels_total = 0
    channels = access_json("channels")
    for channel in channels:
        channels_total += 1
        if {"u_id": u_id} in channel["members_all"]:
            channels_part += 1
    
    users = access_json("users")
    for user in users:
        if user["u_id"] == u_id and update_stats:
            user["user_stats"]["channels_joined"].append({"num_channels_joined": channels_part, "time_stamp": time_created})
            with open('src/data.json', 'r+') as FILE:
                DATA = json.load(FILE)
                DATA["users"] = users
            with open('src/data.json', 'w') as FILE:
                json.dump(DATA, FILE) 
    
    return [channels_part, channels_total]

def dm_part_finder(u_id, update_stats=True):
    #finding no of dms the user is a part of + the number of total dms:
    dt = datetime.now(timezone.utc)
    time_created = dt.replace(tzinfo=timezone.utc).timestamp()
    
    dms_part = 0
    dms_total = 0
    dms = access_json("dms")
    for dm in dms:
        dms_total += 1
        if {"u_id": u_id} in dm["members_all"]:
            dms_part += 1

    users = access_json("users")
    for user in users:
        if user["u_id"] == u_id and update_stats:
            user["user_stats"]["dms_joined"].append({"num_dms_joined": dms_part, "time_stamp": time_created})
            with open('src/data.json', 'r+') as FILE:
                DATA = json.load(FILE)
                DATA["users"] = users
            with open('src/data.json', 'w') as FILE:
                json.dump(DATA, FILE) 

    return [dms_part, dms_total]

def no_messages_sent(u_id, update_stats=True):
     #finding no of messages user has sent + the number of total messages:
    dt = datetime.now(timezone.utc)
    time_created = dt.replace(tzinfo=timezone.utc).timestamp()

    messages_sent = 0
    messages_total = 0
    messages = access_json("messages")
    for message in messages:
        messages_total += 1
        if message["u_id"] == u_id:
            messages_sent += 1
    
    users = access_json("users")
    for user in users:
        if user["u_id"] == u_id and update_stats:
            user["user_stats"]["messages_sent"].append({"num_messages_sent": messages_sent, "time_stamp": time_created})
            with open('src/data.json', 'r+') as FILE:
                DATA = json.load(FILE)
                DATA["users"] = users
            with open('src/data.json', 'w') as FILE:
                json.dump(DATA, FILE)
    return [messages_sent, messages_total]

def involvement_rate_finder(u_id):
    channels_joined = channel_no_finder(u_id, update_stats=False)[0]
    channels_total = channel_no_finder(u_id, update_stats=False)[1]
    
    dms_joined = dm_part_finder(u_id, update_stats=False)[0]
    dms_total = dm_part_finder(u_id, update_stats=False)[1]
    
    messages_sent = no_messages_sent(u_id, update_stats=False)[0]
    messages_total = no_messages_sent(u_id, update_stats=False)[1]

    if not channels_total + dms_total + messages_total == 0:
        involvement_rate = (channels_joined + dms_joined + messages_sent)/(channels_total + dms_total + messages_total)
    else:
        involvement_rate = 0
    
    users = access_json("users")
    for user in users:
        if user["u_id"] == u_id:
            user["user_stats"]["involvement_rate"] = involvement_rate
            with open('src/data.json', 'r+') as FILE:
                DATA = json.load(FILE)
                DATA["users"] = users
            with open('src/data.json', 'w') as FILE:
                json.dump(DATA, FILE)

def user_stats_v1(token):
    """
    After taking in a valid token, creates a user dictionary containing the number of channels the user is a part of, the number of DMs the user is
    a part of, The number of messages the user has sent, The user's involvement, as defined by this pseudocode:
    sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_dreams_channels, num_dreams_dms, num_dreams_msgs)

    Arguments:
        token (string) - the token of the user who is requesting this function.

    Exceptions:
        None

    Return Value:
        Returns the user stats dicitonary in the format:
        {
            "channels_part": <int>,
            "dms_part": <int>,
            'messages_sent': <int>,
            'involvement': <float>           
        }
    """
    u_id = token_invalid_id_AccessError(token)

    users = access_json("users")
    for user in users:
        if user["u_id"] == u_id:
            temp_user = user

    return {"user_stats": temp_user["user_stats"]}
