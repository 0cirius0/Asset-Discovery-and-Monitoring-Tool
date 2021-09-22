from ldap3 import Server, Connection, ALL
from datetime import datetime,time,timedelta
import sublist3r
import sshtunnel
import socket, time, requests
from functools import wraps
from bson import ObjectId
import hashlib, binascii
from werkzeug.security import generate_password_hash, check_password_hash
from nuclei.nuclei import *
import init
from timerClass import *
import string,random 
import jwt


client=MongoClient(init.conn_str,tlsCAFile=certifi.where())

def hash_password(password):
    #"""Hash a password for storing."""
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
    #"""Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def get_os_piechart():
    db=client.db
    all_computers=db.computers
    temp_list={}
    for all in all_computers.find():
        if all['operatingsystem'] in temp_list.keys():
            temp_list[all['operatingsystem']]+=1
        else:
            temp_list[all['operatingsystem']]=1
    return temp_list

def get_hist_users():
    db=client.db
    all_users=db.users
    temp_list={}
    for all in all_users.find():
        del all['_id']
        temp_char_list=all['memberof'].split(',')
        for word in temp_char_list:
            if '=' in word:
                ind=word.index('=')
                if word[ind-1]=='N':
                    if word[ind+1:] in temp_list.keys():
                        temp_list[word[ind+1:]]+=1
                    else:
                        temp_list[word[ind+1:]]=1
                    #print(word[ind+1:])
    return temp_list

def get_hist_computers():
    db=client.db
    all_computers=db.computers
    temp_list={}
    for all in all_computers.find():
        ind=all['dnshostname'].index('.')
        temp_str=all['dnshostname']
        temp_str=temp_str[ind+1:]
        if temp_str.upper() in temp_list.keys():
            temp_list[temp_str.upper()]+=1
        else:
            temp_list[temp_str.upper()]=1
    return temp_list


def exploreusers(i):
    DC1=init.ldap_servers[i].split('.')[1]
    DC2=init.ldap_servers[i].split('.')[2]
    db=client.db
    conn=db.users
    if(init.ssh_server[i]!=""):
        tunnel = sshtunnel.SSHTunnelForwarder(
            (init.ssh_server[i],init.ssh_port[i]),
            ssh_username=init.ssh_username[i],
            ssh_password=init.ssh_password[i],
            remote_bind_address=(init.ldap_servers[i], 389),
        )
        tunnel.start()
        server= Server('127.0.0.1',port=tunnel.local_bind_port,get_info=ALL)
        query=Connection(server,DC1+'\\'+init.username[i],init.password[i],auto_bind=True) 
        query.search('CN=Users,DC='+DC1+',DC='+DC2,'(objectclass=person)',attributes=["name","userprincipalname","memberof"])
        tunnel.stop()
    else:
        server= Server(init.ldap_servers[i],get_info=ALL)
        query=Connection(server,DC1+'\\'+init.username[i],init.password[i],auto_bind=True) 
        query.search('CN=Users,DC='+DC1+',DC='+DC2,'(objectclass=person)',attributes=["name","userprincipalname","memberof"])
    
    
    for entry in query.entries:
        if(str(entry["userprincipalname"])!="[]" and conn.find_one({"userprincipalname":str(entry["userprincipalname"]).lower()}) is None):
            temp={"name":str(entry["name"]),"memberof":str(entry["memberof"]),"userprincipalname":str(entry["userprincipalname"]).lower()}
            conn.insert_one(temp)
        
        
def exploredevices(i):
    DC1=init.ldap_servers[i].split('.')[1]
    DC2=init.ldap_servers[i].split('.')[2]
    db=client.db
    conn=db.computers
    
    if(init.ssh_server[i]!=""):
        tunnel = sshtunnel.SSHTunnelForwarder(
            (init.ssh_server[i],init.ssh_port[i]),
            ssh_username=init.ssh_username[i],
            ssh_password=init.ssh_password[i],
            remote_bind_address=(init.ldap_servers[i], 389),
        )
        tunnel.start()
        server= Server('127.0.0.1',port=tunnel.local_bind_port,get_info=ALL)
        query=Connection(server,DC1+'\\'+init.username[i],init.password[i],auto_bind=True) 
        query.search('CN=Computers,DC='+DC1+',DC='+DC2,'(objectclass=computer)',attributes=["dnshostname","cn","operatingsystem","operatingsystemhotfix","operatingsystemservicepack","operatingsystemversion","memberof","lastlogon"])
        tunnel.stop()
    else:   
        server= Server(init.ldap_servers[i],get_info=ALL)
        query=Connection(server,DC1+'\\'+init.username[i],init.password[i],auto_bind=True) 
        query.search('CN=Computers,DC='+DC1+',DC='+DC2,'(objectclass=computer)',attributes=["dnshostname","cn","operatingsystem","operatingsystemhotfix","operatingsystemservicepack","operatingsystemversion","memberof","lastlogon"])

      
    for entry in query.entries:
        if(conn.find_one({"dnshostname":str(entry["dnshostname"]).lower()}) is None):
            ip=socket.gethostbyname(str(entry["dnshostname"]))
            temp={"dnshostname":str(entry["dnshostname"]).lower(),"ip":ip,"memberof":str(entry["memberof"]),"lastlogon_d":datetime.strptime(str(entry["lastlogon"]).split('.')[0],"%Y-%m-%d %H:%M:%S"),"monitor":False,"cn":str(entry["cn"]),"operatingsystem":str(entry["operatingsystem"]),"operatingsystemhotfix":str(entry["operatingsystemhotfix"]),"operatingsystemversion":str(entry["operatingsystemversion"]),"operatingsystemservicepack":str(entry["operatingsystemservicepack"])}
            conn.insert_one(temp)

def clearrecords(conn,identify,query,check):
    s=datetime.today().date()
    s=s-timedelta(days=30)
    t=datetime.strptime(query["lastlogon"][0].split(':')[3],"%d-%m-%Y").date()
    if(t<=s):
        i=len(query["lastlogon"])-1
        if(check==1):
            while(i>=0):
                a=datetime.strptime(query["lastlogon"][i].split(':')[3],"%d-%m-%Y").date()
                if(a<=s):
                    query["lastlogon"].pop(i)
                    query["logoff"].pop(i)
                    query["last_user"].pop(i)
                    query["last_user_source_mac"].pop(i)
                    query["last_user_source_ip"].pop(i)
                i=i-1
            conn.update_one({'dnshostname':identify},{"$set":{"lastlogon":query["lastlogon"],"logoff":query["logoff"],"last_user":query["last_user"],"last_user_source_mac":query["last_user_source_mac"],"last_user_source_ip":query["last_user_source_ip"]}})        
        else:
            while(i>=0):
                a=datetime.strptime(query["lastlogon"][i].split(':')[3],"%d-%m-%Y").date()
                if(a<=s):
                    query["lastlogon"].pop(i)
                    query["lastdevice"].pop(i)
                i=i-1
            conn.update_one({'userprincipalname':identify},{"$set":{"lastlogon":query["lastlogon"],"lastdevice":query["lastdevice"]}})

def update_comp(check,wsname,username,d_time,identify,ip=None,mac=None):  #check=1=>signin check=0=>signout
    db=client.db
    conn=db.computers
    if(check==0):
        query=conn.find_one({'dnshostname':identify})
        if(query["currentuser"]==username):
            conn.update_one({'dnshostname':identify},{"$push":{"last_user_source_ip":query["curr_user_source_ip"],"last_user_source_mac":query["curr_user_source_mac"],"last_user":query["currentuser"],"logoff":d_time},"$set":{"currentuser":None,"curr_user_source_ip":ip,"curr_user_source_mac":mac}},upsert=True)
            query=conn.find_one({'dnshostname':identify})
            clearrecords(conn,identify,query,1)

    else:
        if(ip is not None and mac is not None):
            conn.update_one({'dnshostname':identify},{"$set":{"monitor":True,"currentuser":username,"curr_user_source_ip":ip,"curr_user_source_mac":mac},"$push":{"lastlogon":d_time}},True)
        else:
            conn.update_one({'dnshostname':identify},{"$set":{"monitor":True,"currentuser":username,"curr_user_source_ip":"default","curr_user_source_mac":"default"},"$push":{"lastlogon":d_time}},True)

def update_user(check,wsname,username,d_time,uname):
    db=client.db
    conn=db.users
    if(check==0):
        query=conn.find_one({'userprincipalname':uname})
        conn.update_one({'userprincipalname':uname},{"$push":{"last_device":query["current_device"]},"$set":{"current_device":"null"}},upsert=True)
        query=conn.find_one({"userprincipalname":uname})
        clearrecords(conn,uname,query,0)
    else:
        conn.update_one({"userprincipalname":uname},{"$set":{"current_device":wsname},"$push":{"lastlogon":d_time}},upsert=True)

def subdomains(org):
    print("Working")
    subs=sublist3r.main(org, 40, False,ports=None,silent=True, verbose= False, enable_bruteforce= False, engines=None)
    db=client.db
    conn=db.sites
    print("Updating")
    for i in range(len(subs)):
        if(conn.find_one({"subdomain":subs[i]}) is None):
            conn.insert_one({"subdomain":subs[i]})

def github_dork(org):
    db=client.db
    conn=db.github
    s=datetime.today().date()
    search_url="https://api.github.com/search/code?per_page=500"
    location_url="https://api.github.com/repos/"
    token=os.getenv("GITHUB")

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

def initiator():
    time.sleep(5)   
    db=client.db
    conn=db.github
    query=conn.find_one({"container":True})
    org=query["org"]
    nuclei()
    if(org is not None or org != "None"):
        github_dork(org)         #Release the chains
    print("Exploring the Network")
    for i in range(len(init.username)):
        exploredevices(i)
        exploreusers(i)
    #function to start all discovery

def start():
    time.sleep(2)
    t=43200
    global rt
    print("Started")
    rt=RepeatedTimer(2,initiator)
    time.sleep(2)
    rt.interval=t
