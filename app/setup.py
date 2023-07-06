import json
import bcrypt
import os
import socket
import getpass
import subprocess

#loading config.json into local array
f=open("database/config.json")
data=json.load(f)
list=[]
for i in data:
    list.append(i[0])

#write specified data to config.json
def write_json(arg):
    json_object=json.dumps(arg, indent=4)
    with open("database/config.json", "w") as file:
        file.write(json_object)

#first time setup
if len(list)==0:
    #password setup
    password=input("Create password: ")
    #password hashing
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    hash_json = hash.decode('utf8').replace("'", '"')
    list.append(hash_json) 
    print("Password set to "+password)
    #storage location setup
    path=input("Set storage location for your repositories: ")
    #add the / at the end of the path if the user didnt already add it
    if path[-1]!="/":
        path=path+"/"
    list.append(path)
    print("Storage path set to: "+path)
    #print host ip adress
    output=subprocess.check_output(['hostname', '-I']).decode('utf-8')
    host_ip=output.strip()
    list.append(host_ip)
    print("Server IP adress: "+host_ip)
    #user which will use the git server
    username=input("Set server linux user(leave blank for current user): ")
    if username=="":
        username = getpass.getuser()
    list.append(username)
    print("Server user: "+username)
    #generate secret key for flask sessions
    secret_key=os.urandom(24).hex()
    list.append(secret_key)
    #write everything to config.json
    write_json(list)
    print("Setup complete!")
#if everything is already setup
else:
    print("Everything is already set up")

