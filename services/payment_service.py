import os
from dotenv import load_dotenv
from flask import jsonify

from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

from services.helper_service import generate_random_string
from services.user_service import update_user_balance



load_dotenv()
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME")]
collection = db["payments"]
userCollection = db['users']
cardCollection = db['cards']
refundCollection = db['refunds']

def pay(paymentData,userNo,ip_address):
    user = userCollection.find_one({"userNo": userNo})
    payment_dict = paymentData.dict(by_alias=True)
    payment_dict['islem_id']= generate_random_string(30)

    card = cardCollection.find_one({"kk_no": payment_dict['kk_no']})
    if card is None:
        return jsonify({"error": "Card not found."}), 404
    elif payment_dict['islem_tutar']>user['balance']:
        return jsonify({"error": "Insufficient balance."}), 400
    else:
        newBalance = user['balance']-payment_dict['islem_tutar']
        update_user_balance(user_no=userNo, newBalance=newBalance)
        payment_dict['userNo']=userNo
        payment_dict['ip_address']=ip_address
        collection.insert_one(payment_dict)
        del payment_dict['_id']
        return jsonify(payment_dict),200

def get_payments(userNo):
    paynetArray = []
    payments = collection.find({"userNo": userNo})
    for payment in payments:
        del payment['_id']
        paynetArray.append(payment)
    return jsonify(paynetArray), 200

def get_refund(userNo,refundData,ip_address):
    user = userCollection.find_one({"userNo": userNo})
    refund_dict = refundData.dict(by_alias=True)
    islemId = refund_dict['islem_id']
    payment = collection.find_one({"islem_id":islemId, "userNo":userNo})

    if payment is None:
        return jsonify({"error": "Payment not found."}), 404

    didRefundBefore = refundCollection.find_one({"islem_id":islemId})
    if didRefundBefore:
        return jsonify({"error": "Refund already."}), 400
    
    newBalance = user['balance']+payment['islem_tutar']
    update_user_balance(userNo,newBalance)
    refund_dict['userNo']=userNo
    refund_dict['islem_tutar']=payment['islem_tutar']
    refund_dict['ip_address']=ip_address
    refundCollection.insert_one(refund_dict)
    del refund_dict['_id']
    return jsonify(refund_dict),200
