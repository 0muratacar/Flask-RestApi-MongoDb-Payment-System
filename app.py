import os
from dotenv import load_dotenv
from flask import Flask,request
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
from flask_restx import Api, Resource


app = Flask(__name__)
api = Api(app,doc='/docs')

load_dotenv()
client = MongoClient(os.environ.get("MONGO_URI"))
db = client[os.environ.get("DB_NAME")] 
collection = db["users"]
collection.create_index([("userNo", ASCENDING)], unique=True)
collection.create_index([("authCode", ASCENDING)], unique=True)

CORS(app)


@api.route('/hello')
class HelloWorld(Resource):
    @api.doc(description='Returns greeting message')
    def get(self):
        return {'message': 'Hello, World!'}
    


@api.route('/api/users')
class CreateUser(Resource):
    @api.doc(description='Creating user')
    def post(self):
        try:
            user_data = UserDTO(**request.json)
        except Exception as e:
            return {"error": str(e)}, 400
        
        inserted_user = insert_user_data(user_data)


        if inserted_user is None:
            return {"error": "userNo or authCode should be unique."},500
        return inserted_user, 201

@api.route('/api/storage-card')
class StorageCard(Resource):
    @api.doc(description='Storage Card')
    def post(self):
        try:
            card_data = CardDto(**request.json)
        except Exception as e:
            return {"error": str(e)}, 400
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 

        userNo = request.headers['userNo']
        inserted_card = insert_card_data(card_data,userNo)
        if inserted_card is None:
            return {"error": "kk_no should be unique."}, 500
        return inserted_card, 201
    @api.doc(description='List Storaged Card')
    def get(self):
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 

        userNo = request.headers['userNo']
        return user_cards(userNo)

@api.route('/api/payment')
class Payment(Resource):
    @api.doc(description='Pay')
    def post(self):
        try:
            paymentData = PaymentDto(**request.json)
        except Exception as e:
            return {"error": str(e)}, 400
        
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        
        userNo = request.headers['userNo']
        ip_address = request.remote_addr
        return pay(paymentData,userNo,ip_address)
    @api.doc(description='Get payments')
    def get(self):
        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        userNo = request.headers['userNo']
        return get_payments(userNo)

@api.route('/api/refund')
class Payment(Resource):
    @api.doc(description='Get refund')
    def post(self):
        try:
            refundData = RefundDto(**request.json)
        except Exception as e:
            return {"error": str(e)}, 400

        if verify_header(request.headers)!=1:
            return verify_header(request.headers) 
        userNo = request.headers['userNo'] 
        ip_address = request.remote_addr

        return get_refund(userNo,refundData,ip_address)



if __name__=='__main__':
    app.debug=True
    app.run()