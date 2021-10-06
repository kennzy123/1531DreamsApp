import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config
from src.dm import dm_messages_v1, dm_remove_v1, dm_create_v1, message_send_dm_v1, dm_details_v1, dm_invite_v1, dm_leave_v1, dm_list_v1
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.other import clear_v2
from src.other import search_v2
from src.channel import channel_join_v2, channel_messages_v2, channel_addowner_v1, channel_removeowner_v1, channel_invite_v2, channel_details_v2, channel_leave_v1
from src.user import user_profile_v2, user_profile_setname_v2, user_profile_setemail_v2, user_profile_sethandle_v1, users_all_v1, users_stats_v1, user_profile_uploadphoto_v1, users_stats_update, user_stats_v1
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.admin import admin_user_permission_change_v1, admin_user_remove_v1
from src.message import message_send_v2, message_edit_v2, message_remove_v1, message_share_v1, message_pin_v1, message_unpin_v1, message_react_v1, message_unreact_v1,  message_sendlater_v1, message_sendlaterdm_v1
from src.notifications import notifications_get_v1
from src.standup import standup_active_v1, standup_start_v1, standup_send_v1

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Allows for access of files in static directory.
@APP.route('/static/<path:path>')
def send_js(path):
    return dumps(send_from_directory('', path))

@APP.before_first_request
def before_first_request_func():
    users_stats_update(channels=True, dms=True, messages=True)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# dm_messages Route
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_v1_HTTP():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    return dumps(dm_messages_v1(token, dm_id, start))

# dm_remove Route
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_v1_HTTP():
    payload = request.get_json()

    return dumps(dm_remove_v1(payload["token"], payload["dm_id"]))

# dm_create Route
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v1_HTTP():
    payload = request.get_json()

    return dumps(dm_create_v1(payload["token"], payload["u_ids"]))

# dm_message_senddm Route
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm_v1_HTTP():
    payload = request.get_json()

    return dumps(message_send_dm_v1(payload["token"], payload["dm_id"], payload["message"]))

# clear Route
@APP.route("/clear/v1", methods=['DELETE'])
def clear_v1_HTTP():
    return dumps(clear_v2())

# auth_login Route
@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2_HTTP():
    payload = request.get_json()

    return dumps(auth_login_v2(payload["email"], payload["password"]))

# auth_register Route
@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2_HTTP():
    payload = request.get_json()

    return dumps(auth_register_v2(payload["email"], payload["password"], payload["name_first"], payload["name_last"]))

#auth_logout Route
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1_HTTP():
    payload = request.get_json()

    return dumps(auth_logout_v1(payload["token"]))

# search Route
@APP.route('/search/v2', methods=['GET'])
def search_v2_HTTP():
    
    token = request.args.get('token')
    query_str = request.args.get('query_str')

    return dumps(search_v2(token, query_str))

# channel_join Route
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2_HTTP():
    payload = request.get_json()

    return dumps(channel_join_v2(payload["token"], payload["channel_id"]))

# channel_messages Route
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2_HTTP():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    return dumps(channel_messages_v2(token, channel_id, start))

# user_profile Route
@APP.route("/user/profile/v2", methods=['GET'])
def user_profile_v2_HTTP():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))

    return dumps(user_profile_v2(token, u_id))

# user_profile_setname Route
@APP.route("/user/profile/setname/v2", methods=['PUT'])
def user_profile_setname_v2_HTTP():
    payload = request.get_json()

    return dumps(user_profile_setname_v2(payload["token"], payload["name_first"], payload["name_last"]))

# user_profile_setemail Route
@APP.route("/user/profile/setemail/v2", methods=['PUT'])
def user_profile_setemail_v2_HTTP():
    payload = request.get_json()

    return dumps(user_profile_setemail_v2(payload["token"], payload["email"]))

# user_profile_sethandle Route
@APP.route("/user/profile/sethandle/v2", methods=['PUT'])
def user_profile_sethandle_v2_HTTP():
    payload = request.get_json()

    return dumps(user_profile_sethandle_v1(payload["token"], payload["handle_str"]))

# users_all Route
@APP.route("/users/all/v1", methods=['GET'])
def users_all_v1_HTTP():
    token = request.args.get('token')

    return dumps(users_all_v1(token))

# channels_create Route
@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2_HTTP():
    payload = request.get_json()

    return dumps(channels_create_v2(payload["token"], payload["name"], payload["is_public"]))

# admin_userpermission_change Route
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_user_permission_change_v1_HTTP():
    payload = request.get_json()

    return dumps(admin_user_permission_change_v1(payload["token"], payload["u_id"], payload["permission_id"]))

# message_send Route
@APP.route("/message/send/v2", methods=['POST'])
def message_send_v2_HTTP():
    payload = request.get_json()

    return dumps(message_send_v2(payload["token"], payload["channel_id"], payload["message"]))

# message_remove Route
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1_HTTP():
    payload = request.get_json()

    return dumps(message_remove_v1(payload["token"], payload["message_id"]))

# message_edit Route
@APP.route("/message/edit/v2", methods=['PUT'])
def message_edit_v2_HTTP():
    payload = request.get_json()

    return dumps(message_edit_v2(payload["token"], payload["message_id"], payload["message"]))

# channel_list Route
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2_HTTP():
    token = request.args.get('token')

    return dumps(channels_list_v2(token))

# channels_listall Route
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2_HTTP():
    token = request.args.get('token')

    return dumps(channels_listall_v2(token))

# admin_user_remove Route
@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove_v1_HTTP():
    payload = request.get_json()

    return dumps(admin_user_remove_v1(payload["token"], payload["u_id"]))

# dm_details Route
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1_HTTP():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    return dumps(dm_details_v1(token, dm_id))

# dm_details Route
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v1_HTTP():
    token = request.args.get('token')

    return dumps(dm_list_v1(token))

# dm_invite Route
@APP.route("/dm/invite/v1", methods=['POST'])
def dm_invite_v1_HTTP():
    payload = request.get_json()

    return dumps(dm_invite_v1(payload["token"], payload["dm_id"], payload["u_id"]))

# dm_leave Route
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v1_HTTP():
    payload = request.get_json()

    return dumps(dm_leave_v1(payload["token"], payload["dm_id"]))

# channel_invite Route
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2_HTTP():
    payload = request.get_json()

    return dumps(channel_invite_v2(payload["token"], payload["channel_id"], payload["u_id"]))

# channel_details Route
@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2_HTTP():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(channel_details_v2(token, channel_id))

# channel_addowner Route
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner_v1_HTTP():
    payload = request.get_json()

    return dumps(channel_addowner_v1(payload["token"], payload["channel_id"], payload["u_id"]))

# channel_removeowner Route
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner_v1_HTTP():
    payload = request.get_json()

    return dumps(channel_removeowner_v1(payload["token"], payload["channel_id"], payload["u_id"]))

# channel_leave Route
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_v1_HTTP():
    payload = request.get_json()

    return dumps(channel_leave_v1(payload["token"], payload["channel_id"]))

# message_share Route
@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1_HTTP():
    payload = request.get_json()

    return dumps(message_share_v1(payload["token"], payload["og_message_id"], payload["message"], payload["channel_id"], payload["dm_id"]))

# notifications_get Route
@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get_v1_HTTP():
    token = request.args.get('token') 

    return dumps(notifications_get_v1(token))

# auth_passwordreset_request Route
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_passwordreset_request_v1_HTTP():
    payload = request.get_json()

    return dumps(auth_passwordreset_request_v1(payload["email"]))

# auth_passwordreset_reset Route
@APP.route('/auth/passwordreset/reset/v1', methods=['POST'])
def auth_passwordreset_reset_v1_HTTP():
    payload = request.get_json()

    return dumps(auth_passwordreset_reset_v1(payload['reset_code'], payload['new_password']))

# message_pin Route
@APP.route("/message/pin/v1", methods=['POST'])
def message_pin_v1_HTTP():
    payload = request.get_json()

    return dumps(message_pin_v1(payload["token"], payload["message_id"]))

# message_unpin Route
@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin_v1_HTTP():
    payload = request.get_json()

    return dumps(message_unpin_v1(payload["token"], payload["message_id"]))

# message_react Route
@APP.route("/message/react/v1", methods=['POST'])
def message_react_v1_HTTP():
    payload = request.get_json()

    return dumps(message_react_v1(payload["token"], payload["message_id"], payload["react_id"]))

# message_unreact Route
@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact_v1_HTTP():
    payload = request.get_json()

    return dumps(message_unreact_v1(payload["token"], payload["message_id"], payload["react_id"]))

# users_stats Route
@APP.route("/users/stats/v1", methods=['GET'])
def users_stats_v1_HTTP():
    token = request.args.get('token') 

    return dumps(users_stats_v1(token))

# user_profile_uploadphoto Route
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto_v1_HTTP():
    payload = request.get_json()

    return dumps(user_profile_uploadphoto_v1(payload["token"], payload["img_url"], payload["x_start"], payload["y_start"], payload["x_end"], payload["y_end"]))

# user_stats Route
@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_v1_HTTP():
    token = request.args.get('token')

    return dumps(user_stats_v1(token))

# standup_start Route
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start_v1_HTTP():
    payload = request.get_json()

    return dumps(standup_start_v1(payload['token'], payload['channel_id'], payload['length']))

# standup_active Route
@APP.route("/standup/active/v1", methods=['GET'])
def standup_active_v1_HTTP():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(standup_active_v1(token, channel_id))

# standup_send Route
@APP.route("/standup/send/v1", methods=['POST'])
def standup_send_v1_HTTP():
    payload = request.get_json()

    return dumps(standup_send_v1(payload['token'], payload['channel_id'], payload['message']))

# message_sendlater Route
@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater_v1_HTTP():
    payload = request.get_json()
    return dumps(message_sendlater_v1(payload['token'], payload['channel_id'], payload['message'], payload['time_sent']))

# message_sendlater_dm Route
@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm_v1_HTTP():
    payload = request.get_json()
    return dumps(message_sendlaterdm_v1(payload['token'], payload['dm_id'], payload['message'], payload['time_sent']))

if __name__ == "__main__":
    APP.run(port=config.port) # Do not edit this port
