from dotenv import load_dotenv
import os

def setglob():
    load_dotenv()
    global conn_str,org,ide,ldap_servers,username,password,ssh_password,ssh_username,ssh_server,ssh_port
    org=""
    conn_str=os.getenv("MONGODB")
    ide=0
    ldap_servers=[]
    username=[]
    password=[]
    ssh_server=[]
    ssh_username=[]
    ssh_password=[]
    ssh_port=[]