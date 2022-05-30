from flask import Flask, jsonify, request
import pymongo
import re
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Connecting MongoDB database
myclient = pymongo.MongoClient(
    "mongodb+srv://admin:admin@cluster0.cnochr3.mongodb.net/?retryWrites=true&w=majority")

mydb = myclient["invoice-tejas"]
mycol = mydb["users"]


# For Signup
@app.route("/api/register", methods=['POST'])
def signup():

    # get data from user
    user_data = request.json

    # if data will be null
    if any(i[1] in [None,''] for i in user_data.items()):
        return jsonify({"error": "Missing values"}), 401

    # check data is present in database
    existing_email = mycol.find_one({'email': user_data['email']})

    # Validation for email
    EMAIL_REGEX = re.match(
        r'^[a-z0-9\.\+_-]+@[a-z0-9\._-]+\.[a-z]*$', user_data['email'])

    if existing_email is None:
        if not EMAIL_REGEX:
            return jsonify({
                "error": "Email is not valid. Please use valid email"
            }), 401

        # inserting data in database
        user = mycol.insert_one(user_data)
        # User(username, generate_password_hash(password)).save_to_db()

        email = user_data['email']
        mycol.update_one({"email": email}, {"$set": {"password": generate_password_hash(user_data['password'])}})

        return jsonify({
            "message": "User Created Successfully.",
            "status": True,
            "user": {
                "_id": str(user_data['_id']),
                "username": user_data['username'],
                "email": user_data['email'],
                "phone": user_data['phone']
            }
        }), 201
    else:
        return jsonify({
            "message": "User is already registered with this email"
        }), 200


# For login
@app.route('/api/login', methods=['POST'])
def login():
    user_data = request.json

    if any(i[1].strip() in [None,''] for i in user_data.items()):
        return jsonify({"error": "Missing values"}), 401

    # data = {k:v if k!="password" else generate_password_hash(v) for k,v in user_data.items()}
    # print(data)

    user = mycol.find({'email': user_data['email']})
    paswrd = [i for i in list(user)][0]['password']

    # print([i for i in list(user)][0]['password'])

    # pswrd = mycol.find_one(user_data['email'], {"_id": 0, 'password': 1})
    # print(pswrd)

    hash_pass = check_password_hash(paswrd, user_data['password'])
    
    if hash_pass:
        return jsonify({
            "message": "Login Successfully"
        })
   
    # pswrd = mycol.find_one(user_data[''], {"_id": 0, 'password': 1})
    # print(pswrd)
    # # hash_pass = check_password_hash(pswrd, user_pswrd)
    # # print(check_password_hash(pswrd, user_pswrd))

    EMAIL_REGEX = re.match(
        r'^[a-z0-9\.\+_-]+@[a-z0-9\._-]+\.[a-z]*$', user_data['email'])
    
        
    if not EMAIL_REGEX:

        return jsonify({
                    "error": "Email is not valid. Please use valid email"
                }), 401
    elif user_data != user:
        return jsonify({
            "error": "Login failed. Please check e-mail and password"
        }), 401
    elif user_data == user:
            return jsonify({
                "message": "You are logged in successfully" 
            }), 200
    else:
        return jsonify({
            "error": "User is not registered."
        }), 401

    

# For Updating the data
@app.route('/api/update', methods=['PATCH'])
def update():
    user_data = request.json
    email = user_data['email']
    user = mycol.update_one({"email": email}, {"$set": {{"phone": user_data['phone']}, {
                            "username": user_data['username']}, {"password": user_data['password']}}})

    return jsonify({
        "message": "Your data is updated."
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
