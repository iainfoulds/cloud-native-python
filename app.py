from flask import Flask, request, jsonify

from flask import abort
from flask import make_response, url_for

from pymongo import MongoClient

import random
import json
import sqlite3

app = Flask(__name__)

# Connection for MongoDB in separate container
connection = MongoClient("mongodb://cloud-native-python-mongodb-service:27017/")

# Initialize and populate MongoDB if needed
def create_mongodatabase():
    try:
        dbnames = connection.list_database_names()
        if 'cloud_native' not in dbnames:
            db = connection.cloud_native.users
            db_api = connection.cloud_native.apirelease

            db.insert_one({
            "email": "i_foulds@live.com",
            "id": 1,
            "name": "Iain Foulds",
            "password": "cloud-native",
            "username": "ifoulds"
            })

            db_api.insert_one( {
              "buildtime": "2017-01-01 10:00:00",
              "links": "/api/v1/users",
              "methods": "get, post, put, delete",
              "version": "v1"
            })
  
            print ("Database Initialize completed!")
        else:
            print ("Database already Initialized!")
    except:
        print ("Database creation failed!!")

# Set up route for displaying the REST API info
@app.route("/api/v1/info")
def home_index():
    api_list=[]
    db = connection.cloud_native.apirelease
    for row in db.find():
        api_list.append(str(row))
    return jsonify({'api_version': api_list}), 200

# Definition to list users from MongoDB
def list_users():
    api_list=[]
    db = connection.cloud_native.users
    
    for row in db.find():
        api_list.append(str(row))
    
    return jsonify({'user_list': api_list})

# Definition to list a specific user from MongoDB
def list_user(user_id):
    api_list=[]
    db = connection.cloud_native.users

    for i in db.find({'id':user_id}):
        api_list.append(str(i))

    if api_list == []:
        abort(404)
    return jsonify({'user_details':api_list})

# Definition to add a user to the MongoDB
def add_user(new_user):
    api_list=[]
    print (new_user)
    db = connection.cloud_native.users
    user = db.find({'$or':[{"username":new_user['username']} ,{"email":new_user['email']}]})
    for i in user:
        print (str(i))
        api_list.append(str(i))

    # print (api_list)
    if api_list == []:
    #    print(new_user)
       db.insert(new_user)
       return "Success"
    else :
       abort(409)

# Definition to delete a specific user
def del_user(del_user):
    db = connection.cloud_native.users
    api_list=[]
    for i in db.find({'username':del_user}):
        api_list.append(str(i))

    if api_list == []:
        abort(404)
    else:
       db.remove({"username":del_user})
       return "Success"

# Definition to update a specific user
def upd_user(user):
    api_list=[]
    print (user)
    db_user = connection.cloud_native.users
    users = db_user.find_one({"id":user['id']})
    for i in users:
        api_list.append(str(i))
    if api_list == []:
       abort(409)
    else:
        db_user.update({'id':user['id']},{'$set': user}, upsert=False )
        return "Success"

# Route to list users
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()

# Route to get a specific user
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return list_user(user_id)

# Route to add users via POST
@app.route('/api/v1/users', methods=['POST'])
def create_user():
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'email': request.json['email'],
        'name': request.json.get('name',""),
        'password': request.json['password'],
        'id': random.randint(1,1000)
    }
    return jsonify({'status': add_user(user)}), 201

# Route to delete a specific user
@app.route('/api/v1/users', methods=['DELETE'])
def delete_user():
    if not request.json or not 'username' in request.json:
        abort(400)
    user=request.json['username']
    return jsonify({'status': del_user(user)}), 200

# Route to update a specific user via PUT
@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = {}
    if not request.json:
        abort(400)
    user['id']=user_id
    key_list = request.json.keys()

    for i in key_list:
        user[i] = request.json[i]
    print (user)
    return jsonify({'status': upd_user(user)}), 200

# Error handlers
@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)

@app.errorhandler(409)
def user_found(error):
    return make_response(jsonify({'error': 'Conflict! Record exist'}), 409)

# Start up the web server and serve traffic
if __name__ == "__main__":
    create_mongodatabase()
    app.run(host='0.0.0.0', port=5000, debug=True)