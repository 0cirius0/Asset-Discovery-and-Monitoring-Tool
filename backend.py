from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app=Flask(__name__)

client=MongoClient('mongodb+srv://cirius:MVA1IzOr8GCYoSv8@cluster0.53e13.mongodb.net/db?retryWrites=true&w=majority')

# computers data ko fetch karne ke lie
@app.route('/computers',methods=['GET'])
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
def add_keyword():
    keyword_to_add=request.json['keyword']
    db=client.db
    all_github=db.github
    all_github.update_one({'container':True},{'$push': {'keywords': keyword_to_add}},True)
    return "SUCCESS"

#github db mei keyword delete krne ke lie
@app.route('/remove_keyword',methods=["POST"])
def delete_keyword():
    keyword_to_delete=request.json['keyword']
    db=client.db
    all_github=db.github
    all_github.update_one({'container':True},{'$pull': {'keywords': keyword_to_delete}},True)
    return "SUCCESS"

if __name__=='__main__':
    app.run(debug=True)