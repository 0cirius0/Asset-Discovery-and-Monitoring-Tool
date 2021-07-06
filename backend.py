from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app=Flask(__name__)

client=MongoClient('mongodb+srv://cirius:MVA1IzOr8GCYoSv8@cluster0.53e13.mongodb.net/db?retryWrites=true&w=majority')


@app.route('/computers',methods=['GET'])
def computers():
    db=client.db
    all_computers=db.computers
    temp_list=[]
    for all in all_computers.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

@app.route('/users',methods=['GET'])
def users():
    db=client.db
    all_users=db.users
    temp_list=[]
    for all in all_users.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

@app.route('/github',methods=['GET'])
def github():
    db=client.db
    all_github=db.github
    temp_list=[]
    for all in all_github.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

@app.route('/sites',methods=['GET'])
def sites():
    db=client.db
    all_sites=db.sites
    temp_list=[]
    for all in all_sites.find():
        del all['_id']
        temp_list.append(all)
    return jsonify(temp_list)

@app.route('/delete_github',methods=["POST"])
def delete_github():
    url=request.json['url']
    #url=data['url']
    print(url)
    db=client.db
    all_github=db.github
    print(all_github.find_one)
    all_github.find_one_and_delete({"url":url})
    print(all_github)
    return "Successful"



if __name__=='__main__':
    app.run(debug=True)