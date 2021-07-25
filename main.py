import glob
glob.setglob()
from custom_func import *
from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY']=os.getenv("PASS_KEY")

client=MongoClient(glob.conn_str,tlsCAFile=certifi.where())
#Domain Name in explore functions

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token=None
       if 'x-access-tokens' in request.cookies:
           token=request.cookies['x-access-tokens']
       if not token:
            return render_template('login.html',error="Token not provided, login to get your token.")
            #return jsonify({"Message":"Token not provided."})
       try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
       except:
           return render_template('login.html',error="Token is invalid, login to get your token.")

       return f(*args, **kwargs)
   return decorator

@app.route("/monitor")
def gather():
    action=request.args.get('action')
    rdp=request.args.get('rdp')
    user=request.args.get('user')
    device=request.args.get('pc')
    d_time=request.args.get('time')
    dom=request.args.get('domain')
    username=user+"@"+dom
    cname=device+"."+dom
    username=username.lower()
    cname=cname.lower()

    print(rdp,user,device)
    if(int(action)==1 and int(rdp)==1):
        ip=request.args.get('ip')
        mac=request.args.get('mac')
        update_comp(1,device,user,d_time,cname,ip,mac)
        update_user(1,device,user,d_time,username)
    elif(int(action)==1 and int(rdp)==0):
        update_comp(1,device,user,d_time,cname)
        update_user(1,device,user,d_time,username)
    elif(int(action)==0):
        update_comp(0,device,user,d_time,cname)
        update_user(0,device,user,d_time,username)
    return "OK"

@app.route('/github',methods=['GET'])
@token_required
def github():
    db=client.db
    all_github=db.github
    temp_list=[]
    for all in all_github.find():
        del all['_id']
        if 'container' in all:
            continue
        temp_list.append(all)
    return render_template('github.html',data=temp_list)

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

    return render_template('sites.html',data=temp_list)

@app.route("/settings/interval/change",methods=['POST'])
@token_required
def change():
    global rt
    t=int(request.form["gap"])
    db=client.db
    conn=db.github
    temp_array=conn.find_one({'container':True})['keywords']
    if(rt.is_running):
        rt.interval=t
        return redirect(url_for('settings',code=306))
    return redirect(url_for('settings',code=307))


@app.route('/delete_github',methods=["POST"])
@token_required
def delete_github():
    url=request.form['url']
    #url=data['url']
    #print(url)
    db=client.db
    all_github=db.github
    all_github.find_one_and_delete({"url":url})
    #print(all_github)
    return redirect('/github')

#container=true ki saari keys return krne ke lie
@app.route('/get_keys',methods=["GET"])
@token_required
def get_keys():
    db=client.db
    all_github=db.github
    temp_array=all_github.find_one({'container':True})['keywords']
    #print(type(temp_array))
    return render_template('.html',data=temp_array)

#frontend se user credentials lene ke lie
@app.route('/get_credentials',methods=["POST"]) 
@token_required
def get_credentials():
    dc_name=request.form['dc_name']
    user=request.form['username']
    passw=request.form['password']
    dc1=dc_name.split('.')[1]
    if(request.form['ssh_user'] is not None):
        ssh_user=request.form['ssh_user']
        ssh_pass=request.form['ssh_pass']
        port=int(request.form['port'])
        ssh=request.form['ssh']
        try:
            tunnel = sshtunnel.SSHTunnelForwarder(
                (ssh,port),
                ssh_username=ssh_user,
                ssh_password=ssh_pass,
                remote_bind_address=(dc_name.lower(), 389),
            )
            tunnel.start()
            server= Server('127.0.0.1',port=tunnel.local_bind_port,get_info=ALL)
            query=Connection(server,dc1+'\\'+user,passw,auto_bind=True)
            tunnel.stop() 
        except:
            return render_template('credentials.html',error="Credentials did not match.")
        glob.ldap_servers.append(dc_name)
        glob.username.append(user)
        glob.password.append(passw)
        glob.ssh_server.append(ssh),glob.ssh_password.append(ssh_pass),glob.ssh_username.append(ssh_user),glob.ssh_port.append(port)       
    
    else:
        try:
            server= Server(dc_name.lower(),port=389,get_info=ALL)
            query=Connection(server,dc1+'\\'+user,passw,auto_bind=True)
        except:
            return render_template('credentials.html',error="Credentials did not match.")
        glob.ldap_servers.append(dc_name)
        glob.username.append(user)
        glob.password.append(passw)
        glob.ssh_server.append(""),glob.ssh_password.append(""),glob.ssh_username.append(""),glob.ssh_port.append("")
    if(glob.ide==0):
        db=client.db
        conn=db.github
        s=str(datetime.today().date())
        print(s)
        keywords=["accesstoken","secretkey","passkey","api_token"]
        conn.insert_one({"last":s,"container":True,"org":"None","keywords":keywords})
        glob.ide=1
        start()
    return redirect(url_for('dashboard'))

#Add GitHub Keywords
@app.route('/add_keyword',methods=["POST"])
@token_required
def add_keyword():
    keyword_to_add=request.form['keyword']
    db=client.db
    all_github=db.github
    all_github.update_one({'container':True},{'$push': {'keywords': keyword_to_add}},True)
    return redirect('/settings')

#Delete GitHub Keyword
@app.route('/remove_keyword',methods=["POST"])
@token_required
def delete_keyword():
    keyword_to_delete=request.form['keyword']
    db=client.db
    all_github=db.github
    all_github.update_one({'container':True},{'$pull': {'keywords': keyword_to_delete}},True)
    return redirect('/settings')

# Login
@app.route('/login',methods=["POST", "GET"])
def login():
    if request.method=="GET":
        return render_template('login.html')
    password=request.form['password']
    db=client.db
    to_check=db.first
    for all_p in to_check.find():
        stored_password=all_p['password']
    chck=verify_password(stored_password,password)
    if chck==False:
        return render_template('login.html',error="Incorrect password provided.")
    all_chars=string.ascii_letters+string.digits
    random_string=''.join(random.choices(all_chars, k=20))
    token = jwt.encode({'random': random_string, 'exp' : datetime.utcnow() + timedelta(minutes=300)}, app.config['SECRET_KEY'])
    resp=make_response(render_template('credentials.html'))
    resp.set_cookie('x-access-tokens',token)
    return resp

#Change Password
@app.route('/change_password',methods=["POST"])
@token_required
def change_password():
    old_password=request.form['old_password']
    new_password=request.form['new_password']
    cnf_new_password=request.form['cnf_new_password']
    if new_password != cnf_new_password:
        return render_template('.html',error="Passwords do not match.")
    db=client.db
    to_check=db.first
    for all_p in to_check.find():
        stored_password=all_p['password']
    chck=verify_password(stored_password,old_password)
    if chck==False:
        return render_template('changepassword.html',error="Incorrect old password.")
    hash_password(new_password)
    return redirect(url_for('logout'))

#Get the List of all AD Networks for Computers
@app.route('/get_dnshostname',methods=["GET"])
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
    return render_template('dnshostselect.html',data=temp_list)

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
    return render_template('user_dnshostselect.html',data=temp_list)

@app.route('/get_users/<string:userprincipalname>',methods=["GET","POST"]) 
@token_required
def get_users(userprincipalname):
    #userprincipalname=request.form['userprincipalname']
    if request.method=="GET":

        db=client.db
        all_users=db.users
        temp_list=[]
        member_list=[]
        for all in all_users.find():
            del all['_id']
            #print(type(all['memberof']))
            #print(all['memberof'])
            temp_char_list=all['memberof'].split(',')
            new_temp_list=[]
            for word in temp_char_list:
                #print(word)
                if '=' in word:
                    ind=word.index('=')
                    if word[ind-1]=='N':
                        if word[ind+1:] not in new_temp_list:
                            if word[ind+1:]=="Users":
                                continue
                            new_temp_list.append(word[ind+1:])
                        #print(word[ind+1:])
            del all['memberof']
            all['memberof']=new_temp_list
            for member in all['memberof']:
                if member not in member_list:
                    member_list.append(member)
            #print(all)
            if 'lastlogon' in all.keys():
                all['monitor']=True
            else:
                all['monitor']=False
            if userprincipalname in all['userprincipalname']:
                temp_list.append(all)
        #return jsonify(temp_list)
        to_get=[]
        return render_template('users.html',data=temp_list,members=member_list,host_name=userprincipalname,checked=to_get)
    else:
        db=client.db
        all_users=db.users
        member_list=[]
        for all in all_users.find():
            del all['_id']
            #print(type(all['memberof']))
            #print(all['memberof'])
            temp_char_list=all['memberof'].split(',')
            new_temp_list=[]
            for word in temp_char_list:
                #print(word)
                if '=' in word:
                    ind=word.index('=')
                    if word[ind-1]=='N':
                        if word[ind+1:] not in new_temp_list:
                            if word[ind+1:]=="Users":
                                continue
                            new_temp_list.append(word[ind+1:])
                        #print(word[ind+1:])
            del all['memberof']
            all['memberof']=new_temp_list
            for member in all['memberof']:
                if member not in member_list:
                    member_list.append(member)

        to_get=request.form.getlist("hello")
        #for member in member_list:
            #if request.form[member]==True:
                #to_get.append(member)

        #userprincipalname=request.form['userprincipalname']
        temp_list=[]
        for all in all_users.find():
            del all['_id']
            if userprincipalname in all['userprincipalname']:
                temp_char_list=all['memberof'].split(',')
                new_temp_list=[]
                for word in temp_char_list:
                    #print(word)
                    if '=' in word:
                        ind=word.index('=')
                        if word[ind-1]=='N':
                            if word[ind+1:] not in new_temp_list:
                                if word[ind+1:]=="Users":
                                    continue
                                new_temp_list.append(word[ind+1:])
                            #print(word[ind+1:])
                del all['memberof']
                all['memberof']=new_temp_list
                if len(to_get)==0:
                    temp_list.append(all)
                for word in to_get:
                    #print(word)
                    if word in all['memberof']:
                        temp_list.append(all)
                        break

        return render_template('users.html',data=temp_list,members=member_list,host_name=userprincipalname,checked=to_get)

## NEW ROUTES ADDED AFTER MERGING
@app.route('/get_computers_os/<string:dnshostname>', methods=["GET"]) ## /computers aur get_computers waali use nhi krenge then
@token_required
def get_computers_os(dnshostname):
    #dnshostname=request.form['dnshostname']
    if request.method=="GET":

        db=client.db
        all_computers=db.computers
        temp_list={}
        member_list=[]
        for all in all_computers.find():
            del all['_id']
            temp_char_list=[]
            temp_char_list=all['memberof'].split(',')
            new_temp_list=[]
            for word in temp_char_list:
                #print(word)
                if '=' in word:
                    ind=word.index('=')
                    if word[ind-1]=='N':
                        if word[ind+1:] not in new_temp_list:
                            if word[ind+1:]=="Computer":
                                continue
                            new_temp_list.append(word[ind+1:])
                        #print(word[ind+1:])
            del all['memberof']
            all['memberof']=new_temp_list
            for member in all['memberof']:
                if member not in member_list:
                    member_list.append(member)
            if(dnshostname in all['dnshostname']):
                if all['operatingsystem'] in temp_list.keys():
                    temp_list[all['operatingsystem']].append(all)
                else:
                    new_temp_list=[]
                    new_temp_list.append(all)
                    temp_list[all['operatingsystem']]=new_temp_list
        #print(temp_list)
        #print(members)
        to_get=[]
        return render_template('computers.html',data=temp_list,members=member_list,host_name=dnshostname,checked=to_get)
    else:
        db=client.db
        all_computers=db.computers
        member_list=[]
        for all in all_computers.find():
            del all['_id']
            temp_char_list=[]
            temp_char_list=all['memberof'].split(',')
            new_temp_list=[]
            for word in temp_char_list:
                #print(word)
                if '=' in word:
                    ind=word.index('=')
                    if word[ind-1]=='N':
                        if word[ind+1:] not in new_temp_list:
                            if word[ind+1:]=="Computer":
                                continue
                            new_temp_list.append(word[ind+1:])
                        #print(word[ind+1:])
            del all['memberof']
            all['memberof']=new_temp_list
            for member in all['memberof']:
                if member not in member_list:
                    member_list.append(member)

        to_get=request.form.getlist("hello")
        #for member in member_list:
        #   if request.form[member]==True:
        #      to_get.append(member)
        #dnshostname=request.form['dnshostname']
        temp_list=[]

        for all in all_computers.find():
            del all['_id']
            if dnshostname in all['dnshostname']:
                temp_char_list=[]
                temp_char_list=all['memberof'].split(',')
                new_temp_list=[]
                for word in temp_char_list:
                    #print(word)
                    if '=' in word:
                        ind=word.index('=')
                        if word[ind-1]=='N':
                            if word[ind+1:] not in new_temp_list:
                                if word[ind+1:]=="Computer":
                                    continue
                                new_temp_list.append(word[ind+1:])
                            #print(word[ind+1:])
                del all['memberof']
                all['memberof']=new_temp_list
                if len(to_get)==0:
                    temp_list.append(all)
                for word in to_get:
                    if word in all['memberof']:
                        temp_list.append(all)
                        break
        return render_template('computers.html',data=temp_list,host_name=dnshostname,checked=to_get,members=member_list)

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
            #print(word)
            if '=' in word:
                ind=word.index('=')
                if word[ind-1]=='N':
                    if word[ind+1:] not in temp_list:
                        temp_list.append(word[ind+1:])
                    #print(word[ind+1:])
    return render_template('users.html',data=temp_list)

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
                    #print(word[ind+1:])
    return render_template('.html',data=temp_list)

@app.route('/filter_members_computers/<string:dnshostname>',methods=["POST","GET"])
@token_required
def filter_members_computers(dnshostname):
    to_get=request.form['list']
    #dnshostname=request.form['dnshostname']
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
    return render_template('users.html',data=temp_list)

@app.route('/filter_members_users/<string:userprincipalname>',methods=["POST","GET"])
@token_required
def filter_members_users(userprincipalname):
    to_get=request.form['list']
    #userprincipalname=request.form['userprincipalname']
    temp_list=[]
    db=client.db
    all_users=db.users
    for all in all_users.find():
        del all['_id']
        if userprincipalname in all['userprincipalname']:
            if len(to_get)==0:
                temp_list.append(all)
            for word in to_get:
                #print(word)
                if word in all['memberof']:
                    temp_list.append(all)
                    break

    return render_template('users.html',data=temp_list)

@app.route('/dashboard',methods=['GET'])
@token_required
def dashboard():
    all_graphs=[]
    os_piechart=get_os_piechart()
    hist_users=get_hist_users()
    hist_computers=get_hist_computers()
    all_graphs.append(os_piechart)
    all_graphs.append(hist_users)
    all_graphs.append(hist_computers)
    return render_template('dashboard.html', graph=all_graphs)

@app.route('/',methods=['GET'])
def default():
    if 'x-access-tokens' in request.cookies:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/logout',methods=['GET'])
@token_required
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('x-access-tokens')
    return resp

@app.route('/hide_vuln/<string:subdomain>/<string:name_of_vuln>', methods=['GET'])
@token_required
def delete_vuln(subdomain,name_of_vuln):
    db=client.db
    all_sites=db.sites
    temp_var=all_sites.update({"subdomain":subdomain, 'vulns.name':name_of_vuln},{'$set':{'vulns.$.hide':True}},True)
    return redirect(url_for('sites'))

@app.route('/settings',methods=['GET'])
@token_required
def settings():
    db=client.db
    all_github=db.github
    temp_array=all_github.find_one({'container':True})['keywords']
    return render_template('settings.html',data=temp_array)

@app.route('/settings/github/org',methods=['POST'])
@token_required
def setorg():
    org=request.form['org']
    db=client.db
    conn=db.github
    conn.update_one({"container":True},{"$set":{"org":org}},True)
    temp_array=conn.find_one({'container':True})['keywords']
    return redirect(url_for('settings',code=308))

def apprun():
    cwd=os.getcwd()
    app.run(debug=True, host='0.0.0.0', port=5000 , ssl_context=(cwd+'\\cert.pem', cwd+'\\key.pem'), use_reloader=False)

if __name__ == '__main__':
    cwd=os.getcwd()
    #test()
    pr=subprocess.Popen("powershell Get-NetFirewallRule -DisplayName \"AssetMonitoring\"",stdout=subprocess.PIPE)
    pr.communicate()[0]
    
    if(pr.returncode==1):
        input("The tool requires port 5000 to be open inside the domain network.A Prompt would ask for adminsitrator privileges to create a rule in firewall for the port.\nPress Enter to continue...")
        print("Creating the rule in firewall")
        subprocess.Popen("powershell -noprofile -command \"&{Start-Process powershell -Verb Runas -ArgumentList '-noprofile -executionpolicy bypass -file "+cwd+"\\create_rule.ps1'}\"",shell=True)    
    
    t=threading.Thread(target=apprun, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting")
        exit(0)
        
#netstat -n | find ":3389" | find "ESTABLISHED" => Finds the IP of source device from which user has used Remote Desktop
#arp -a lists all mac adrress of all devices in the network
#open port in firewall for local network
#Send response instantly and don't make computer wait.
#CTRL+C not stopping script
#server= Server('LAB-DC.lab01.local',get_info=ALL)
#conn=Connection(server,'LAB01\Administrator','password@1',auto_bind=True) 
#conn.search('CN=Users,DC=lab01,DC=local','(objectclass=person)',attributes=['memberof',ipv4']) 
#https://ldap3.readthedocs.io/en/latest/tutorial_searches.html
#subprocess.Popen("powershell -noprofile -command \"&{Start-Process powershell -Verb Runas -ArgumentList '-noprofile -file C:/Users/Administrator/Documents/openport.ps1'}\"",shell=True)
#setup ssh server on windows10x64 and try local then remote forwarding
#https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse