# not very MVCish, but much more reliable and stable (to rely on flask-pymongo)
from api import flask_pymongo


def exists_once_or_not(cmp_dict, collection_name):
    resp = find_one(cmp_dict, collection_name)
    if resp is None:
        return False
    else:
        return True


def exists_or_not(cmp_dict, collection_name):
    resp = find(cmp_dict, collection_name)
    if resp is None:
        return False
    elif resp.count() == 0:
        return False
    else:
        return True


def find_one_if_exists(cmp_dict, collection_name, projection=None):
    return find_one(cmp_dict, collection_name, projection)


def update_one_document_values(cmp_dict, value_dict, collection_name):
    return update_one_document(cmp_dict, {'$set': value_dict}, collection_name)


def add_to_list_param(cmp_dict, param_name, to_push, collection_name):
    return update_one_document(cmp_dict, {'$push': {param_name: to_push}}, collection_name)


def remove_from_list_param(cmp_dict, param_name, param_cmp_dict, collection_name):
    return update_one_document(cmp_dict, {"$pull": {param_name: param_cmp_dict}}, collection_name)


def find(cmp_dict, collection_name):
    return getattr(flask_pymongo.db, collection_name).find(cmp_dict)


def find_one(cmp_dict, collection_name, projection=None):
    if projection:
        return getattr(flask_pymongo.db, collection_name).find_one(cmp_dict, projection)
    else:
        return getattr(flask_pymongo.db, collection_name).find_one(cmp_dict)


def create_document(doc_dict, collection_name):
    db_response = getattr(flask_pymongo.db, collection_name).insert_one(doc_dict)
    if not db_response.acknowledged:
        return False
    return True


def update_one_document(cmp_dict, update_dict, collection_name):
    db_response = getattr(flask_pymongo.db, collection_name).update_one(cmp_dict, update_dict)
    if not db_response.acknowledged:
        return False
    return True


def delete_one_document(cmp_dict, collection_name):
    db_response = getattr(flask_pymongo.db, collection_name).delete_one(cmp_dict)
    if not db_response.acknowledged:
        return False
    return True
