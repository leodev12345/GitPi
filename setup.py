import json
import bcrypt
import os
import socket

f=open("database/config.json")
data=json.load(f)
list=[]
for i in data:
    list.append(i[0])

def write_json(arg):
    json_object=json.dumps(arg, indent=4)
    with open("database/config.json", "w") as file:
        file.write(json_object)

#first time setup
if len(list)==0:
    password=input("Create password: ")
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    hash_json = hash.decode('utf8').replace("'", '"')
    list.append(hash_json) 
    print("Password set to "+password)
    path=input("Set storage location for your repositories: ")
    list.append(path)
    print("Storage path set to: "+path)
    host_ip=socket.gethostbyname_ex(socket.gethostname())[-1][0]
    list.append(host_ip)
    print("Server IP adress: "+host_ip)
    username = os.getlogin()
    list.append(username)
    print("Server user: "+username)
    write_json(list)
else:
    print("Everything is already set up")
