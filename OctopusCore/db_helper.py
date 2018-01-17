import database_mongodb as mongo_db
import os
import sys
ROOT_PATH = os.path.dirname(__file__)
sys.path.append(os.path.join(ROOT_PATH, '..'))
from constants import *


def _determine_collection_name(is_temp_user):
    if is_temp_user:
        return TMP_USERS_COLLECTION_NAME
    else:
        return USERS_COLLECTION_NAME


def check_if_user_exists_email(email, is_temp_user=False):
    return mongo_db.exists_once_or_not({EMAIL_KEY: email}, _determine_collection_name(is_temp_user))


def create_user(user_dict, is_temp_user=False):
    return mongo_db.create_document(user_dict, _determine_collection_name(is_temp_user))


def find_temp_user_email_key(email_key):
    return mongo_db.find_one_if_exists({EMAIL_KEY_KEY: email_key}, _determine_collection_name(is_temp_user=True))


def delete_temp_user_email_key(email_key):
    return mongo_db.delete_one_document({EMAIL_KEY_KEY: email_key}, _determine_collection_name(is_temp_user=True))


def find_user_email(email, is_temp_user=False):
    return mongo_db.find_one_if_exists({EMAIL_KEY: email}, _determine_collection_name(is_temp_user))


def find_user_id(user_id, is_temp_user=False):
    return mongo_db.find_one_if_exists({DB_ID_KEY: user_id}, _determine_collection_name(is_temp_user))


def create_server(user_id, server_dict):
    return mongo_db.add_to_list_param({DB_ID_KEY: user_id}, SERVERS_KEY, server_dict,
                                      _determine_collection_name(is_temp_user=False))


def find_server_id_provider(user_id, server_id, provider):
    user, does_exist = mongo_db.find_one_if_exists(
        {
            DB_ID_KEY: user_id,
            # SERVERS_KEY: {
            #     ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: provider
            # }
        }, _determine_collection_name(is_temp_user=False),
        {
            SERVERS_KEY: {
                '$elemMatch': {
                    ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: provider
                }
            }
        })
    if user.get(SERVERS_KEY) is None:
        return user, False
    else:
        return user, does_exist


def set_server_values(user_id, server_id, provider, value_dict):
    mongo_dict = {}
    for key_name, value in value_dict.items():
        mongo_dict["{}.$.{}".format(SERVERS_KEY, key_name)] = value
    return mongo_db.update_one_document_values({
        DB_ID_KEY: user_id,
        SERVERS_KEY: {
            '$elemMatch': {
                ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: provider
            }
        }
    }, mongo_dict, _determine_collection_name(is_temp_user=False))


def set_server_status_id_provider(user_id, server_id, provider, status):
    return set_server_values(user_id, server_id, provider, {"{}.$.{}".format(SERVERS_KEY, STATUS_EXP_KEY): status})


def delete_server_id_provider(user_id, server_id, provider):
    return mongo_db.remove_from_list_param(
        {DB_ID_KEY: user_id},
        SERVERS_KEY,
        {ID_EXP_KEY: server_id, PROVIDER_EXP_KEY: provider},
        _determine_collection_name(is_temp_user=False)
    )