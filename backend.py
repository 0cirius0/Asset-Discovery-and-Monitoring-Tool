from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import datetime
import hashlib, binascii, os
import random,string

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
app.config['SECRET_KEY']='Th1s1ss3cr3t' # isko hide krna hai

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


# computers data ko fetch karne ke lie (subject to be removed in case koi zrurat na padi to)
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

@app.route('/get_computers',methods=['POST'])
@token_required
def get_computers():
    dnshostname=request.json['dnshostname']
    db=client.db
    all_computers=db.computers
    temp_list=[]
    for all in all_computers.find():
        del all['_id']
        if(dnshostname in all['dnshostname']):
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
    all_chars=string.ascii_letters+string.digits
    random_string=''.join(random.choices(all_chars, k=20))
    print(random_string)
    token = jwt.encode({'random': random_string, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=300)}, app.config['SECRET_KEY'])
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

#get dnshostname from computers table
@app.route('/get_dnshostname',methods=['GET'])
@token_required
def get_dnshostname():
    db=client.db
    all_computers=db.computers
    temp_list=[]
    for all in all_computers.find():
        ind=all['dnshostname'].index('.')
        temp_str=all['dnshostname']
        temp_str=temp_str[ind+1:]
        if temp_str in temp_list:
            continue
        temp_list.append(temp_str)
    return jsonify(temp_list)

#get dnshostname from users table
@app.route('/get_dnshostname_users',methods=['GET'])
@token_required
def get_dnshostname_users():
    db=client.db
    all_users=db.users
    temp_list=[]
    for all in all_users.find():
        ind=all['userprincipalname'].index('@')
        temp_str=all['userprincipalname']
        temp_str=temp_str[ind+1:]
        if temp_str in temp_list:
            continue
        temp_list.append(temp_str)
    return jsonify(temp_list)

@app.route('/get_users',methods=['POST']) # THODA CHANGE KIA HAI MERGING KE BAAD (Monitor waala field add kia hai)
@token_required
def get_users():
    userprincipalname=request.json['userprincipalname']
    db=client.db
    all_users=db.users
    temp_list=[]
    for all in all_users.find():
        del all['_id']
        #print(type(all['memberof']))
        #print(all['memberof'])
        temp_char_list=all['memberof'].split(',')
        print(temp_char_list)
        if 'lastlogon' in all.keys():
            all['monitor']=True
        else:
            all['monitor']=False
        if userprincipalname in all['userprincipalname']:
            temp_list.append(all)
    return jsonify(temp_list)

## NEW ROUTES ADDED AFTER MERGING
@app.route('/get_computers_os', methods=["POST"]) ## /computers aur get_computers waali use nhi krenge then
@token_required
def get_computers_os():
    dnshostname=request.json['dnshostname']
    db=client.db
    all_computers=db.computers
    temp_list={}
    for all in all_computers.find():
        del all['_id']
        if(dnshostname in all['dnshostname']):
            if all['operatingsystem'] in temp_list.keys():
                print("HERE")
                temp_list[all['operatingsystem']].append(all)
            else:
                #print(dict(all))
                new_temp_list=[]
                new_temp_list.append(all)
                temp_list[all['operatingsystem']]=new_temp_list
                print(temp_list)
    return jsonify(temp_list)

@app.route('/get_memberof_users',methods=['GET'])
@token_required
def get_memberof_users():
    db=client.db
    all_users=db.users
    temp_list=[]
    for all in all_users.find():
        del all['_id']
        temp_char_list=all['memberof'].split(',')
        for word in temp_char_list:
            print(word)
            if '=' in word:
                ind=word.index('=')
                if word[ind-1]=='N':
                    if word[ind+1:] not in temp_list:
                        temp_list.append(word[ind+1:])
                    print(word[ind+1:])
    return jsonify(temp_list)

@app.route('/get_memberof_computers',methods=['GET'])
@token_required
def get_memberof_computers():
    db=client.db
    all_computers=db.computers
    temp_list=[]
    for all in all_computers.find():
        del all['_id']
        temp_char_list=all['memberof'].split(',')
        for word in temp_char_list:
            if '=' in word:
                ind=word.index('=')
                if word[ind-1]=='N':
                    if word[ind+1:] not in temp_list:
                        temp_list.append(word[ind+1:])
                    print(word[ind+1:])
    return jsonify(temp_list)

@app.route('/filter_members_computers',methods=["POST"])
@token_required
def filter_members_computers():
    to_get=request.json['list']
    dnshostname=request.json['dnshostname']
    temp_list=[]
    db=client.db
    all_computers=db.computers
    for all in all_computers.find():
        del all['_id']
        if dnshostname in all['dnshostname']:
            if len(to_get)==0:
                temp_list.append(all)
            for word in to_get:
                if word in all['memberof']:
                    temp_list.append(all)
                    break

    return jsonify(temp_list)

@app.route('/filter_members_users',methods=["POST"])
@token_required
def filter_members_users():
    to_get=request.json['list']
    userprincipalname=request.json['userprincipalname']
    temp_list=[]
    db=client.db
    all_users=db.users
    for all in all_users.find():
        del all['_id']
        if userprincipalname in all['userprincipalname']:
            if len(to_get)==0:
                temp_list.append(all)
            for word in to_get:
                print(word)
                if word in all['memberof']:
                    temp_list.append(all)
                    break

    return jsonify(temp_list)


if __name__=='__main__':
    app.run(debug=True,ssl_context=('cert.pem', 'key.pem'))