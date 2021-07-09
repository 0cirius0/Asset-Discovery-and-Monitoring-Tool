from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import datetime
import hashlib, binascii, os

def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    to_store=(salt + pwdhash).decode('ascii')
    db=client.db
    to_update=db.first
    to_update.update({},{"$set": {'password':to_store}})
    return


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

app=Flask(__name__)
app.config['SECRET_KEY']='Th1s1ss3cr3t'

client=MongoClient('mongodb+srv://cirius:MVA1IzOr8GCYoSv8@cluster0.53e13.mongodb.net/db?retryWrites=true&w=majority')

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token=None
       if 'x-access-tokens' in request.headers:
           token=request.headers['x-access-tokens']
       if not token:
            return jsonify({"Message":"Token not provided."})
       try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
       except:
           return jsonify({'message': 'token is invalid'})

       return f(*args, **kwargs)
   return decorator


# computers data ko fetch karne ke lie
@app.route('/computers',methods=['GET'])
@token_required
def computers():

    db=client.db
    all_computers=db.computers
    temp_list=[]
    for all in all_computers.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

#users data ko fetch krne ke lie
@app.route('/users',methods=['GET'])
@token_required
def users():
    db=client.db
    all_users=db.users
    temp_list=[]
    for all in all_users.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

#github data ko fetch krne ke lie
@app.route('/github',methods=['GET'])
@token_required
def github():
    db=client.db
    all_github=db.github
    temp_list=[]
    for all in all_github.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

#sites data ko fetch krne ke lie
@app.route('/sites',methods=['GET'])
@token_required
def sites():
    db=client.db
    all_sites=db.sites
    temp_list=[]
    for all in all_sites.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

#github entries ko delete karne ke lie
@app.route('/delete_github',methods=["POST"])
@token_required
def delete_github():
    url=request.json['url']
    #url=data['url']
    print(url)
    db=client.db
    all_github=db.github
    all_github.find_one_and_delete({"url":url})
    print(all_github)
    return "Successful"

#container=true ki saari keys return krne ke lie
@app.route('/get_keys',methods=["GET"])
@token_required
def get_keys():
    db=client.db
    all_github=db.github
    temp_array=all_github.find_one({'container':True})['keywords']
    print(type(temp_array))
    return jsonify(temp_array)

#frontend se user credentials lene ke lie
@app.route('/get_credentials',methods=["POST"])
def get_credentials():
    dc1=request.json['dc1']
    dc2=request.json['dc2']
    dc_name=request.json['dc_name']
    username=request.json['username']
    password=request.json['password']

#github db mei keyword add krne ke lie
@app.route('/add_keyword',methods=["POST"])
@token_required
def add_keyword():
    keyword_to_add=request.json['keyword']
    db=client.db
    all_github=db.github
    all_github.update_one({'container':True},{'$push': {'keywords': keyword_to_add}},True)
    return "SUCCESS"

#github db mei keyword delete krne ke lie
@app.route('/remove_keyword',methods=["POST"])
@token_required
def delete_keyword():
    keyword_to_delete=request.json['keyword']
    db=client.db
    all_github=db.github
    all_github.update_one({'container':True},{'$pull': {'keywords': keyword_to_delete}},True)
    return "SUCCESS"

# sabse pehle login krne ke lie
@app.route('/login',methods=["POST"])
def login():
    password=request.json['password']
    #hash_password(password)
    #return "HI"
    # yaha tak password store krwa lia hai
    db=client.db
    to_check=db.first
    for all_p in to_check.find():
        stored_password=all_p['password']
    chck=verify_password(stored_password,password)
    if chck==False:
        return "Incorrect password provided"
    token = jwt.encode({'password': password, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})
    return "Correct Password"

# password change krne ke lie. Make sure ki jaise hi ispe request pade aur successful ho, to frontend se puraana token delete krna hai and firse login page pe redirect krna hai.
@app.route('/change_password',methods=["POST"])
@token_required
def change_password():
    old_password=request.json['old_password']
    new_password=request.json['new_password']
    cnf_new_password=request.json['cnf_new_password']
    if new_password != cnf_new_password:
        return jsonify({"Message":"Passwords do not match."})
    db=client.db
    to_check=db.first
    for all_p in to_check.find():
        stored_password=all_p['password']
    chck=verify_password(stored_password,old_password)
    if chck==False:
        return jsonify({"Message":"Incorrect old password."})
    hash_password(new_password)
    return jsonify({"Message":"Password changed successfully"})

if __name__=='__main__':
    app.run(debug=True)