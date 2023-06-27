import json
import bcrypt

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
    print("Create password:")
    password=input()
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    hash_json = hash.decode('utf8').replace("'", '"')
    list.append(hash_json)
    write_json(list)

