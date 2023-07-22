import json
import bcrypt
import os
import getpass
import subprocess

list=[]
list_data=[]
prompt=0
#loading config.json into local array
with open("database/config.json", "r") as f:
    list=json.load(f)

f=open("database/data.json")
data=json.load(f)
for i in data:
    list_data.append(tuple((i[0],i[1],i[2],i[3])))

#write specified data to json
def write_json(arg1, arg2):
    json_object=json.dumps(arg1, indent=4)
    with open(arg2, "w") as file:
        file.write(json_object)

def hash_password(arg):
    bytes = arg.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    hash_json = hash.decode('utf8').replace("'", '"')
    return hash_json

#first time setup
def first_time_setup():
    os.system("clear") 
    if len(list)==0:
        #password setup
        password=input("Create password: ")
        list.append(hash_password(password)) 
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
        username=input("Set server user(leave blank for current linux user): ")
        if username=="":
            username = getpass.getuser()
        list.append(username)
        print("Server user: "+username)
        #generate secret key for flask sessions
        secret_key=os.urandom(24).hex()
        list.append(secret_key)
        #write everything to config.json
        write_json(list, "database/config.json")
        print("Setup complete!")
        enter=input("Press ENTER to continue")
        os.system("clear")
    #if everything is already setup
    else:
        print("Everything is already set up")
        enter=input("Press ENTER to continue")
        os.system("clear")

def change_password():
    os.system("clear") 
    while True:
        old_password=input("Enter current password: ")
        result=bcrypt.checkpw(old_password.encode('utf-8'), list[0].encode('utf-8'))
        if result==True:
            new_password=input("Enter new password: ")
            list[0]=hash_password(new_password)
            write_json(list, "database/config.json")
            print("password changed to: "+new_password)
            enter=input("Press ENTER to continue")
            os.system("clear")
            break
        else:
            print("Incorrect password, try again")
        
def change_storage():
    os.system("clear") 
    new_location=input("Set new storage location for repsitories: ")
    if new_location[-1]!="/":
        new_location=new_location+"/"
    list[1]=new_location
    write_json(list, "database/config.json")
    print("Storage location changed to: "+new_location)
    enter=input("Press ENTER to continue")
    os.system("clear")
    

def change_user():
    os.system("clear")
    new_user=input("Change server user(leave blank for current user): ")
    if new_user=="":
        new_user=getpass.getuser()
    list[3]=new_user
    write_json(list, "database/config.json")
    print("Server user changed to: "+new_user)
    enter=input("Press ENTER to continue")
    os.system("clear")

def delete_app_data():
    os.system("clear") 
    print("All repository data will be deleted from the application, but all the repositories stored on the server will still stay intact")
    prompt=input("Are you sure you want to continue [y/n]? ")
    if prompt=="Y" or prompt=="y":
        list_data.clear()
        write_json([],"database/data.json")
        print("Operation complete")
    enter=input("Press ENTER to continue")
    os.system("clear")


func_dict_2={
    1:change_password,
    2:change_storage,
    3:change_user,
    4:delete_app_data
}

def change_config():
    os.system("clear") 
    prompt=0
    while prompt!=5:
        try:
            print("Change configuration: ")
            print("[1] Change password")
            print("[2] Change storage location")
            print("[3] Change server user")
            print("[4] Delete app data")
            print("[5] Go back")
            prompt=int(input("Chose option: "))
            func_dict_2[prompt]()
        except (ValueError, KeyError):
            os.system("clear")
    os.system("clear")

def import_repos():
    os.system("clear")
    print("Scanning "+list[1])
    print("\n", end="")
    obj=os.scandir(list[1])
    to_import=[]
    result = [tup[0] for tup in list_data]
    for entry in obj:
        if entry.is_dir() and ".git" in entry.name and any(ele in entry.name.replace(".git","") for ele in result)==False:
            print(entry.name)
            to_import.append(entry.name)
    obj.close()
    if len(to_import)!=0:
        print("\n", end="")
        print("Listed repositories are not imported")
        prompt=input("Do you wish to import these repositories into the app [y/n]? ")
        print("\n", end="")
        if prompt=="Y" or prompt=="y":
            for i in to_import:
                name=i.replace(".git","")
                path="Path: "+list[3]+"@"+list[2]+":"+list[1]+i
                copy=list[3]+"@"+list[2]+":"+list[1]+i
                print("Repository name: "+name)
                desc=input("Create repository description(optional): ")
                if desc=="":
                    desc="No description"
                print("Repository description: "+desc)
                print("Repository path: "+copy)
                list_data.insert(0, tuple((name,path,desc,copy)))
                print("\n", end="")
            write_json(list_data, "database/data.json")
            print("All repositories are successfully imported")
    else:
        print("All repositories are already imported/no repositories were detected")
    enter=input("Press ENTER to continue")
    os.system("clear")


def display_conf():
    os.system("clear") 
    if len(list)!=0:
        print("Current configuration:")
        print("Server IP adress: "+list[2])
        print("Repositories storage location: "+list[1])
        print("Git server user: "+list[3])
    else:
        print("The app is not yet configured, run first time setup")
    enter=input("Press ENTER to continue")
    os.system("clear")

func_dict_1={
    1:first_time_setup, 
    2:change_config,
    3:import_repos,
    4:display_conf
}

os.system("clear")
while prompt!=5:
    try:
        print("Configuration options: ")
        print("[1] First time setup")
        print("[2] Change configuration")
        print("[3] Import local repositories into the app")
        print("[4] Display current configuration")
        print("[5] Exit")
        prompt=int(input("Chose option: "))
        func_dict_1[prompt]()
    except (ValueError, KeyError):
        os.system("clear")
