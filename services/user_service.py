import os
from dotenv import load_dotenv
from flask import jsonify

from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

from dto.card_dto import CardDto


load_dotenv()
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME")]
collection = db["users"]
collection.create_index([("userNo", ASCENDING)], unique=True)
collection.create_index([("authCode", ASCENDING)], unique=True)


def insert_user_data(user_data):
    try:

        user_dict = user_data.dict(by_alias=True)
        # Insert the user document into the MongoDB collection
        result = collection.insert_one(user_dict)

        # Get the inserted user's ObjectId as a string
        inserted_user_id = str(result.inserted_id)

        # Update the user_dict to include the _id field as a string
        user_dict["_id"] = inserted_user_id

        return user_dict
    except DuplicateKeyError:
        return None
    
def update_user_cards(user_no,kk_no):
    user = collection.find_one({"userNo": user_no})
    if user is None:
        return jsonify({"error": "User not found."}), 404
    
    user['allCards'].append(kk_no)
    user['selectedCard']=(kk_no)

    collection.update_one({"_id": user['_id']}, {"$set": user})

def update_user_balance(user_no,newBalance):
    user = collection.find_one({"userNo": user_no})
    if user is None:
        return jsonify({"error": "User not found."}), 404
    
    user['balance']=newBalance
    collection.update_one({"_id": user['_id']}, {"$set": user})

def verify_user_authentication(user_no, auth_code):
    user = collection.find_one({"userNo": user_no, "authCode": auth_code})
    return user is not None

def verify_header(requestHeaders):
    if 'authCode' not in requestHeaders:
        return {"error": "authCode is not found in headers."}, 400
    
    if 'userNo' not in requestHeaders:
        return {"error": "userNo is not found in headers."}, 400
    
    authCode = requestHeaders['authCode']
    userNo = requestHeaders['userNo']
    user = collection.find_one({"userNo": userNo, "authCode": authCode})

    if user:
        return 1
    else:
        return {"error": "Unauthorized access."}, 401
