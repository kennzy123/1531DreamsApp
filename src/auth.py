from src.error import InputError, AccessError
from src.secret import token_encode, token_decode
from src.json_edit import access_json, add_to_json, remove_from_json
from src.auth_code import reset
from src.user import users_stats_update
from src import config
import src.exceptions
import yagmail
import re
import uuid
import json
import hashlib
from datetime import datetime, timezone

def add_or_remove_session_to_user(session_id, u_id, add):
    """
    Adds/removes a session_id to the user's session_id list. This is so that
    users can have multiple sessions on different devices.

    Arguments:
        session_id (integer) - the session_id provided through UUID.
        u_id (integer) - the user_id that the session_id is being added to.
        add (boolean) - if True, adds a session_id to the user's session ids, otherwise removes a session from session ids.
    """
    with open('src/data.json', 'r') as FILE:
        DATA = json.load(FILE)
        for idx, user in enumerate(DATA['users']):
            if user['u_id'] == u_id:
                user_index = idx
        
        if add:
            DATA['users'][user_index]["session_id"].append(session_id)
        else:
            DATA['users'][user_index]["session_id"].remove(session_id)
    
    with open('src/data.json', 'w') as FILE:
        json.dump(DATA, FILE)

def auth_login_v2(email, password):
    """
    Returns the registered user's auth_user_id and new token, given they 
    provide the correct email and password, adds their new login as a 
    session_id to the user.

    Arguments:
        email (string) - an email used to login which should be in the database.
        password (string) - the password corresponding to the email address of a user in the database.
    
    Exceptions:
        InputError - Occurs when the email entered is not valid as specified, when the email entered does not belong to a user, when the password entered does not correspond to the email provided.
    
    Return Value:
        Returns a dictionary containing token and auth_user_id in the format
        {
            'auth_user_id': 1,
            'token': <token_string>
        }
    """
    # Checks the exceptions for auth/login/v2
    src.exceptions.email_invalid_InputError(email)
    email_user_id = src.exceptions.email_not_belonging_user_InputError(email)
    src.exceptions.password_incorrect_InputError(email_user_id, password)
    
    session_id = int(str(uuid.uuid1().int)[0:15])
    token = token_encode({
        'auth_user_id': email_user_id,
        'session_id': session_id,
    })

    add_or_remove_session_to_user(session_id, email_user_id, True)


    return {
        'token': token,
        'auth_user_id': email_user_id,
    }

def auth_create_handle(name_first, name_last):
    """
    Create a handle for the new user and shortens it if greater than 20 
    characters. If the handle is already taken then adds a number to the 
    end of it.

    Arguments:
        name_first (string) - the user's first name for registering and generating a handle.
        name_last (string) - the user's last name for registering and generating a handle.

    Return Value:
        Returns handle which is a string to be stored for the new user.
    """
    # Creates a handle for the user by combining name_first and name_last.
    # If it is greater than 20 characters then shortens it and removes 
    # whitespace and makes it all lowercase.
    users = access_json("users")
    handle = name_first + name_last
    handle = handle.lower()
    handle = handle.replace(" ", "")
    handle = handle.replace("@", "")
    if len(handle) > 20:
        remove_characters = (len(handle) - 20) * (-1)
        handle = handle[:remove_characters]
    
    # If the handle is already taken, then adds a number to the end of it starting from 0.
    concat_num = 0
    temp_handle = handle
    for user in users:
        if user["handle_str"] == handle:
            handle = temp_handle + str(concat_num)
            concat_num += 1
    
    return handle

def auth_register_v2(email, password, name_first, name_last):
    """
    auth_register_v2 registers a new user for UNSW Dreams with certain criteria fulfilled and adds 
    them to the users database.

    Arguments:
        email (string) - an email used to register for Dreams.
        password (string) - a password used in the process for registering for Dreams.
        name_first (string) - the user's first name for registering and generating a handle.
        name_last (string) - the user's last name for registering and generating a handle.

    Exceptions:
        InputError - Occurs when the email entered is not valid, the email address is already in use, 
        password entered is less than 6 characters long, name_first and/or name_last is not between 1 and 50 characters.

    Return Value:
        Returns a dictionary containing the auth_user_id and token of the new registered user in the format:
        {
            'auth_user_id' : 0,
            'token': <token_string>
        }
    """
    # Checks the exceptions for auth/register/v2
    src.exceptions.email_invalid_InputError(email)
    src.exceptions.email_repeat_InputError(email)
    src.exceptions.password_length_incorrect_InputError(password)
    src.exceptions.name_length_incorrect_InputError(name_first, name_last)
    
    # Creates a handle for the new user.
    handle = auth_create_handle(name_first, name_last)

    # Creates an encrypted password to store.
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()

    # Checks if the user is the first one added, if so they are a Dreams Owner.
    if not access_json("users"):
        permission_id = 1
    else:
        permission_id = 2

    dt = datetime.now(timezone.utc)
    time_created = dt.replace(tzinfo=timezone.utc).timestamp()

    # Adds user information to user database of dictionaries in the data.json.
    id_num = int(str(uuid.uuid1().int)[0:15])
    session_id = int(str(uuid.uuid1().int)[0:15])
    new_user = {
        "u_id" : id_num,
        "email" : email,
        "password" : encrypted_password,
        "name_first" : name_first,
        "name_last" : name_last,
        "handle_str" : handle,
        "session_id" : [session_id],
        "permission_id": permission_id,
        "notifications": [],
        "profile_img_url": str(f"{config.url}static/default_pic.jpg"),
        "user_stats": {
            "channels_joined": [{"num_channels_joined": 0, "time_stamp": time_created}],
            "dms_joined": [{"num_dms_joined": 0, "time_stamp": time_created}],
            'messages_sent': [{"num_messages_sent": 0, "time_stamp": time_created}],
            'involvement_rate': 0.0
        }
    }
    add_to_json("users", new_user)

    token = token_encode({
        'auth_user_id': id_num,
        'session_id': session_id,
    })

    users_stats_update()
    return {
        'token' : token,
        'auth_user_id' : id_num,
    }

def auth_logout_v1(token):
    """
    auth_logout_v1 logs the user out of their current session, by removing
    their session_id from the list of them.

    Arguments:
        token (string) - an encoded string that when decoded contains a dictionary with auth_user_id and session_id.

    Exceptions:
        AccessError - the token passed in does not contain a valid u_id or session_id.

    Return Values:
        {is_success: True} if the user's token was successfully removed and invalidated.
    """
    # Checks the exceptions for auth/logout/v1
    src.exceptions.token_invalid_id_AccessError(token)

    decoded_token = token_decode(token)
    
    add_or_remove_session_to_user(decoded_token["session_id"], decoded_token["auth_user_id"], False)
    
    return {
        "is_success": True
    }

def auth_passwordreset_request_v1(email):
    """
    auth_passwordreset_request_v1 generates a reset_code and sends the code into a registered email
    given by the user.

    Arguments:
        email (string) - an email address registered in Dreams user to send a reset_code.

    Exceptions:
        N/A

    Return Values:
        {}
    """

    # Assume user is not registered
    user_is_registered = False

    # Access users list from json
    users = access_json('users')

    # Iterate through each user to check email is valid
    for user in users:
        if user['email'] == email:
            user_is_registered = True
    
    if user_is_registered:
        # Generate reset_code
        reset['reset_code'] = str(uuid.uuid4())[0:6].upper()
        reset['email'] = email
        
        # Send an email
        yag = yagmail.SMTP('cactuscomp1531', 'ilovecomp')
        contents = [
            f"Enter the following code to reset your password: {reset['reset_code']}"
        ]
        yag.send(email, 'UNSW Dreams Password Reset', contents)

    return {}
        
def auth_passwordreset_reset_v1(reset_code, new_password):
    """
    auth_passwordreset_reset_v1 changes a users password by checking reset_code is valid and
    changing the users data in json to reflect the new password.

    Arguments:
        reset_code (string) - a random string used to verify user requesting reset.
        new_password (string) - a string given by the user as their new password.

    Exceptions:
        InputError - the reset_code is not a valid code or the password is less than 6 characters.

    Return Values:
        {}
    """

    if not reset_code == reset['reset_code']:
        raise InputError('reset code is not valid')

    if len(new_password) < 6:
        raise InputError('new password is too short')

    email = reset['email']
    dict_select = {}

    # Creates an encrypted password to store.
    encrypted_password = hashlib.sha256(new_password.encode()).hexdigest()

    users = access_json('users')
    for user in users:
        if user['email'] == email:
            dict_select = user
    
    # Remove user from json if user is found
    if bool(dict_select):
        remove_from_json('users', dict_select)

    # Change password in dictionary
    dict_select['password'] = encrypted_password

    # Add new dictionary to json for user
    add_to_json('users', dict_select)

    return {}