import os
from dotenv import load_dotenv
from flask import jsonify

from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

from services.user_service import update_user_cards


load_dotenv()
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME")]
collection = db["cards"]
userCollection = db["users"]
collection.create_index([("kk_no",ASCENDING)], unique=True)



def insert_card_data(card_data,user_no):
    try:
        card_dict = card_data.dict(by_alias=True)
        result = collection.insert_one(card_dict)

        inserted_card_id = str(result.inserted_id)
        card_dict["_id"] = inserted_card_id

        update_user_cards(user_no=user_no,kk_no=card_dict['kk_no'])
        return card_dict
    except DuplicateKeyError:
        return None

def user_cards(userNo):
    user = userCollection.find_one({"userNo": userNo})

    # Get the kk_no values from user's allCards array
    kk_nos = user.get('allCards', [])

    cards = collection.find({"kk_no": {"$in": kk_nos}})

    card_data = []
    for card in cards:
        del card['_id']
        card_data.append(card)
  
    return card_data, 200