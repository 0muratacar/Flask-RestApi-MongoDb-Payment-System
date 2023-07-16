import os
from dotenv import load_dotenv
from flask import Flask,request,jsonify
from pymongo import ASCENDING, MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS
from dto.card_dto import CardDto
from dto.payment_dto import PaymentDto
from dto.refund_dto import RefundDto
from dto.user_dto import UserDTO
from services.card_service import insert_card_data, user_cards
from services.payment_service import get_payments, pay, get_refund
from services.user_service import insert_user_data, verify_header, verify_user_authentication


app = Flask(__name__)
load_dotenv()
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME")] 
collection = db["users"]
collection.create_index([("userNo", ASCENDING)], unique=True)
collection.create_index([("authCode", ASCENDING)], unique=True)

CORS(app)

@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        user_data = UserDTO(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    inserted_user = insert_user_data(user_data)
    if inserted_user is None:
        return jsonify({"error": "userNo or authCode should be unique."}), 500

    return jsonify(inserted_user), 201

@app.route('/api/storage-card', methods=['POST','GET'])
def storage_card():
    if(request.method=='POST'):
        try:
            card_data = CardDto(**request.json)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        
        userNo = request.headers['userNo']
        inserted_card = insert_card_data(card_data,userNo)
        if inserted_card is None:
            return jsonify({"error": "kk_no should be unique."}), 500
        return jsonify(inserted_card), 201
    else:
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        
        userNo = request.headers['userNo']
        return user_cards(userNo)

@app.route('/api/payment', methods=['POST','GET'])
def payment():
    if request.method=='POST':
        try:
            paymentData = PaymentDto(**request.json)
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        
        userNo = request.headers['userNo']
        ip_address = request.remote_addr
        return pay(paymentData,userNo,ip_address)
    else:
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        userNo = request.headers['userNo']
        return get_payments(userNo)

@app.route('/api/refund', methods=['POST'])
def refund():
    try:
        refundData = RefundDto(**request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if verify_header(request.headers)!=1:
        return verify_header(request.headers) 
    userNo = request.headers['userNo'] 
    ip_address = request.remote_addr

    return get_refund(userNo,refundData,ip_address)



if __name__=='__main__':
    app.debug=True
    app.run()