import certifi
from pymongo import MongoClient
import subprocess
import json
import os
import init


def nuclei():
    client=MongoClient(init.conn_str,tlsCAFile=certifi.where())
    db=client.db
    conn=db.sites

    cwd=os.cwd()
    query=conn.find()
    format=["http://","https://"]
    f=open(cwd+"//nuclei//subs","w")
    for sub in query:
        if(sub["subdomain"].split(':')[0]!="http" and sub["subdomain"].split(':')[0]!="https"):
            url1=format[0]+sub["subdomain"]
            url2=format[1]+sub["subdomain"]
        else:
            url=sub["subdomain"]
        print(url1)
        f.write(url1+"\n"+url2+"\n")

    print("Working")
    pr0=subprocess.Popen(cwd+"//nuclei//nuclei.exe -update-templates",shell=True)
    pr0.wait()
    pr=subprocess.Popen(cwd+"//nuclei//nuclei.exe -t "+cwd+"//nuclei//nuclei-templates/ -l "+cwd+"//nuclei//subs --json -o "+cwd+"//nuclei//output",shell=True)
    pr.wait()
    f.close()
    f=open(cwd+"//nuclei//output","r")
    data=f.readlines()
    for ele in data:
        vuln=json.loads(ele)
        host=vuln["host"]
        host=host.split('/')[2]
        count=conn.find({"subdomain":host,"vulns":{"$elemMatch":{"name":vuln["info"]["name"]}}}).count()
        if(vuln["info"]["severity"]!="info" and count == 0):
            up={"name":vuln["info"]["name"],"severity":vuln["info"]["severity"],"hide":False}
            conn.find_one_and_update({"subdomain":host},{"$push":{"vulns":up}},upsert=True)
