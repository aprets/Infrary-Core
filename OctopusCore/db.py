from api import flask_pymongo

def existsOnceOrNot(cmpDict, dbName):
    return findOne(cmpDict,dbName).count() == 1


def existsOrNot(cmpDict, dbName):
    return findOne(cmpDict,dbName).count() > 0

def findOneIfExists(cmpDict, dbName):
    objList = findOne(cmpDict, dbName)
    if objList.count() == 1:
        return objList[0], True
    else:
        return None, False

def addToListParam(cmpDict, paramName, toPush, dbName):
    return updateDocument(cmpDict, {'$push': {paramName: toPush}}, dbName)

def removeFromListParam(cmpDict, paramName, paramCmpDict, dbName):
    return updateDocument(cmpDict, {"$pull": {paramName: paramCmpDict}}, dbName)

def findOne(cmpDict, dbName):
    return getattr(flask_pymongo.db, dbName).find(cmpDict, limit=1)

def createDocument(docDict, dbName):
    return getattr(flask_pymongo.db, dbName).insert_one(docDict)

def updateDocument(cmpDict, updateDict, dbName):
    return getattr(flask_pymongo.db, dbName).update(cmpDict, updateDict)

def removeDocument(cmpDict, dbName):
    return getattr(flask_pymongo.db, dbName).remove(cmpDict)