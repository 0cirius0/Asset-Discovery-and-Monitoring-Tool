from pyad import *
import flask
from pymongo import MongoClient
import certifi
import json
import socket
from flask import Flask, request
from datetime import datetime,time,timedelta
import sublist3r
import threading
from signal import signal, SIGINT
import time
import requests

app = Flask(__name__)

client=MongoClient('mongodb+srv://cirius:MVA1IzOr8GCYoSv8@cluster0.53e13.mongodb.net/?retryWrites=true&w=majority',tlsCAFile=certifi.where())

#Domain Name in explore functions

def exploreusers(ide):
    q = adquery.ADQuery()
    db=client.db
    conn=db.users
    q.execute_query(
        attributes = ["name","userprincipalname","memberof"],
        where_clause = "objectClass = '*'",
        base_dn = "CN=Users, DC=lab01, DC=local"
    )
    if(ide!=1):
        for row in q.get_results():
            if(row["userprincipalname"] is not None):
                a=[]
                if(row["memberof"] is not None):
                    for i in row["memberof"]:
                        a.append(i)
                a=json.dumps(a)
                row["memberof"]=a
                if(conn.find_one(row["userprincipalname"]) is None):
                    conn.insert_one(row)
    else:
        up=[]
        for row in q.get_results():
            if(row["userprincipalname"] is not None):
                a=[]
                if(row["memberof"] is not None):
                    for i in row["memberof"]:
                        a.append(i)
                a=json.dumps(a)
                row["memberof"]=a
                up.append(row)
        conn.insert_many(up)        
        
def exploredevices(ide):
    q = adquery.ADQuery()
    db=client.db
    conn=db.computers
    q.execute_query(
        attributes = ["dnshostname","cn","operatingsystem","operatingsystemhotfix","operatingsystemservicepack","operatingsystemversion","memberof"],
        where_clause = "objectClass = '*'",
        base_dn = "CN=Computers, DC=lab01, DC=local"
    )
    if(ide!=1):
        data=q.get_results()
        for row in data:
            if(row["dnshostname"] is None):
                continue
            print(type(row))
            a=[]
            if(row["memberof"] is not None):
                for i in row["memberof"]:
                    a.append(i)
            a=json.dumps(a)
            row["memberof"]=a
            ip=""
            if(row["dnshostname"] is not None):
                ip=socket.gethostbyname(row["dnshostname"])
            row["ip"]=ip
            if(conn.find(row["dnshostname"]) is None):
                conn.insert_one(row)
    else:  
        up=[]
        data=q.get_results()
        for row in data:
            if(row["dnshostname"] is None):
                continue
            print(type(row))
            a=[]
            if(row["memberof"] is not None):
                for i in row["memberof"]:
                    a.append(i)
            a=json.dumps(a)
            row["memberof"]=a
            ip=""
            if(row["dnshostname"] is not None):
                ip=socket.gethostbyname(row["dnshostname"])
            row["ip"]=ip
            up.append(row)
            print(row["ip"],row["operatingsystem"])
        conn.insert_many(up)

def clearrecords(conn,wsname,query):
    print("Clearing")
    s=datetime.today().date()
    s=s-timedelta(days=30)
    i=len(query["lastlogon"])-1
    while(i>=0):
        a=datetime.strptime(query["lastlogon"][i].split(':')[3],"%d-%m-%Y").date()
        if(a<=s):
            query["lastlogon"].pop(i)
            query["logoff"].pop(i)
            query["last_user"].pop(i)
            query["last_user_source_mac"].pop(i)
            query["last_user_source_ip"].pop(i)
        i=i-1
    conn.update_one({'cn':wsname},{"$set":{"lastlogon":query["lastlogon"],"logoff":query["logoff"],"last_user":query["last_user"],"last_user_source_mac":query["last_user_source_mac"],"last_user_source_ip":query["last_user_source_ip"]}})        
  

def update(check,wsname,username,d_time,ip=None,mac=None):  #check=1=>signin check=0=>signout
    db=client.db
    conn=db.computers
    if(check==0):
        query=conn.find_one({'cn':wsname})
        if(query["currentuser"]==username):
            conn.update_one({'cn':wsname},{"$push":{"last_user_source_ip":query["curr_user_source_ip"],"last_user_source_mac":query["curr_user_source_mac"],"last_user":query["currentuser"],"logoff":d_time},"$set":{"currentuser":None,"curr_user_source_ip":ip,"curr_user_source_mac":mac}},True)
            clearrecords(conn,wsname,query)

    else:
        if(ip is not None and mac is not None):
            conn.update_one({'cn':wsname},{"$set":{"currentuser":username,"curr_user_source_ip":ip,"curr_user_source_mac":mac},"$push":{"lastlogon":d_time}},True)
        else:
            conn.update_one({'cn':wsname},{"$set":{"currentuser":username,"curr_user_source_ip":"default","curr_user_source_mac":"default"},"$push":{"lastlogon":d_time}},True)

def subdomains(org):
    print("Working")
    subs=sublist3r.main(org, 40, False,ports=None,silent=True, verbose= False, enable_bruteforce= False, engines=None)
    db=client.db
    conn=db.sites
    print("Updating")
    for i in range(len(subs)):
        if(conn.find_one({"subdomain":subs[i]}) is None):
            conn.insert_one({"subdomain":subs[i]})


@app.route("/monitor")
def gather():
    action=request.args.get('action')
    rdp=request.args.get('rdp')
    user=request.args.get('user')
    device=request.args.get('pc')
    d_time=request.args.get('time')
    print(rdp,user,device)
    if(int(action)==1 and int(rdp)==1):
        ip=request.args.get('ip')
        mac=request.args.get('mac')
        print(ip,mac)
        update(1,device,user,d_time,ip,mac)
    elif(int(action)==1 and int(rdp)==0):
        update(1,device,user,d_time)
    elif(int(action)==0):
        update(0,device,user,d_time)
    return "OK"

def apprun():
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

def github_dork(org):
    db=client.db
    conn=db.github
    s=datetime.today().date()
    search_url="https://api.github.com/search/code?per_page=500"
    location_url="https://api.github.com/repos/"
    token="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"

    query=conn.find_one({"container":True})
    conn.update_one({"container":True},{"$set":{"last":str(s)}},True)
    if(query["last"]==""):
        s=s-timedelta(days=30)
    else:
        s=datetime.strptime(query["last"],"%Y-%m-%d").date()
    
    for keyword in query["keywords"]:
        dork='&q=org:'+org+'%20"'+keyword+'"'
        headers={ "Authorization":"token "+token }
        url=search_url+dork
        try:
            r = requests.get( url, headers=headers, timeout=5 )
            jsn = json.dumps(r.json())
            data=json.loads(jsn)
        except Exception as e:
            return "Error"
        for d in data["items"]:
            path=d["path"]
            repo=d["repository"]["full_name"]
            fetch_url=location_url+repo+"/commits?path="+path
            try:
                r = requests.get( fetch_url, headers=headers, timeout=5 )
                jsn = json.dumps(r.json())
                details=json.loads(jsn)
            except Exception as e:
                return "Error"
            for det in details:
                dt=det["commit"]["committer"]["date"]
                dt=datetime.strptime(datetime.strftime(datetime.strptime(dt.split('T')[0],"%Y-%m-%d").date(),"%d-%m-%Y"),"%d-%m-%Y").date()
                if(dt>s):
                    conn.insert_one({"url":det["html_url"],"keyword_found":keyword})
        
if __name__ == '__main__':
    t=threading.Thread(target=apprun, daemon=True).start()
    subdomains(org)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("exiting")
        exit(0)
        
#netstat -n | find ":3389" | find "ESTABLISHED" => Finds the IP of source device from which user has used Remote Desktop
#arp -a lists all mac adrress of all devices in the network
#open port in firewall for local network
#Send response instantly and don't make computer wait.
#CTRL+C not stopping script