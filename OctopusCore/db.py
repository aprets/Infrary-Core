from api import flask_pymongo


# not very MVCish, but much more reliable and stable (to rely on flask-pymongo)


def exists_once_or_not(cmp_dict, db_name):
    resp = find_one(cmp_dict, db_name)
    if resp is None:
        return False
    else:
        return True

def exists_or_not(cmp_dict, db_name):
    resp = find(cmp_dict, db_name)
    if resp is None:
        return False
    elif resp.count() == 0:
        return False
    else:
        return True


def find_one_if_exists(cmp_dict, db_name):
    found = find_one(cmp_dict, db_name)
    if found is not None:
        return found, True
    else:
        return None, False


def add_to_list_param(cmp_dict, param_name, to_push, db_name):
    return update_one_document(cmp_dict, {'$push': {param_name: to_push}}, db_name)


def remove_from_list_param(cmp_dict, param_name, param_cmp_dict, db_name):
    return update_one_document(cmp_dict, {"$pull": {param_name: param_cmp_dict}}, db_name)


def find(cmp_dict, db_name):
    return getattr(flask_pymongo.db, db_name).find(cmp_dict)

def find_one(cmp_dict, db_name):
    return getattr(flask_pymongo.db, db_name).find_one(cmp_dict)


def create_document(doc_dict, db_name):
    db_response = getattr(flask_pymongo.db, db_name).insert_one(doc_dict)
    if not db_response.acknowledged:
        raise SystemError('dbWriteFail')
    return db_response


def update_one_document(cmp_dict, update_dict, db_name):
    db_response = getattr(flask_pymongo.db, db_name).update_one(cmp_dict, update_dict)
    if not db_response.acknowledged:
        raise SystemError('dbWriteFail')
    return db_response


def delete_one_document(cmp_dict, db_name):
    db_response = getattr(flask_pymongo.db, db_name).delete_one(cmp_dict)
    if not db_response.acknowledged:
        raise SystemError('dbWriteFail')
    return db_response
