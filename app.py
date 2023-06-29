from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import bcrypt

#Storing values locally
list=[]
config_list=[]
#charecters not allowed in repo names
ilegal_charecters=[" ","#","<",">","$","+","%","!","`","&","*","|","{","}","[","]","@",":","/","\"","\\","\'","\(","\)","=","?","€",";",".",",","§","¤","ß","Ł","ł","÷","×","¸","¨","~","ˇ","^","˘","°","˛","˙","´","˝"]
#get current working path 
current_path=os.path.abspath(os.getcwd())

#load json values into the local array every time the program starts
#chdir to project working folder to avoid loading database from wrong path when the working dir changes
os.chdir(current_path)
f=open("database/data.json")
data=json.load(f)
for i in data:
    list.append(tuple((i[0],i[1],i[2],i[3])))

#load program config from json into local array
with open("database/config.json", "r") as f:
    config_data=json.load(f)

#useful variables
config_password=config_data[0]
config_path=config_data[1]
config_ip=config_data[2]
config_user=config_data[3]

#app init
app = Flask(__name__)
app.secret_key=config_data[4]
#function that writes all the repo data to data.json
def write_json(arg):
    json_object=json.dumps(arg, indent=4)
    os.chdir(current_path)
    with open("database/data.json", "w") as file:
        file.write(json_object)

#creating repos
@app.route('/', methods=['POST'])
def create_repo():
    #collecting info
    text = request.form['text']
    desc = request.form['desc']
    #checking info
    if text!="" and any(ele in text for ele in ilegal_charecters)==False:
        #set default description
        if desc=="":
            desc="No description"

        #full path to the repo
        copy_text=config_user+"@"+config_ip+":"+config_path+text+".git"

        #create the repo on the server
        dir_name=text+".git"
        os.chdir(config_path)
        os.mkdir(dir_name)
        os.chdir(dir_name)
        os.system("git init --bare")
        
        #add all the data to list and write it to data.json
        list.insert(0,tuple((text,"Path: "+copy_text,desc,copy_text)))
        write_json(list)

    #refresh the website after form is submitted
    return redirect(url_for('create_repo'))

#render the homepage
@app.route("/")
def index_render():
    #redirect to login page if the user isnt logged in
    if "logged-in" in session:
        return render_template('index.html', my_list=list)
    else:
        return redirect(url_for('login_render'))

#render more options
@app.route("/more")
def more_render():
    #redirect to login page if user isnt logged in
    if "logged-in" in session:
        return render_template('more.html')
    else:
        return redirect(url_for('login_render'))

#render login page
@app.route("/login")
def login_render():
    return render_template('login.html')

#login page functionality
@app.route("/login", methods=['POST'])
def login():
    #get the entered password and compare it to stored hashed password
    password=request.form['password']
    result = bcrypt.checkpw(password.encode('utf-8'), config_password.encode('utf-8'))
    #log in if password is correct and display an error if not
    if result==True:
        session["logged-in"]=True
        return redirect(url_for('index_render')) 
    else:
        return render_template('login.html', error="Incorrect password")


# more options page functionality
@app.route("/more", methods=['POST'])
def more():
    #renaming repos
    #check if the "rename" button is clicked
    if 'rename' in request.form:
        #get all the data
        old_name = request.form['old_name']
        new_name = request.form['new_name']
        #check data
        if old_name!=new_name and new_name!="" and old_name!="" and any(ele in new_name for ele in ilegal_charecters)==False:
            #rename repo on server
            os.chdir(config_path)
            os.rename(old_name+".git",new_name+".git")

            #get index of the tuple containing the old name
            result = [tup[0] for tup in list].index(old_name)            
            #get description that wont change
            desc = list[result][2]
            #change all the necessary data
            path="Path: "+config_user+"@"+config_ip+":"+config_path+new_name+".git"
            copy=config_user+"@"+config_ip+":"+config_path+new_name+".git" 
            list[result]=tuple((new_name,path,desc,copy))
            #write data to data.json
            write_json(list)

    #deleting repos
    #check if "delete" button is pressed
    elif 'remove' in request.form:
        #get all the data
        delete_name = request.form['name_1']
        delete_name_confirm = request.form['name_2']
        #check data
        if delete_name==delete_name_confirm and delete_name!="":
            #get index of the tuple that needs to be deleted
            result = [tup[0] for tup in list].index(delete_name)
            #delete the tuple from the list
            del list[result] 
            #write data to data.json
            write_json(list)

    #changing repo description
    #check if "confirm" button is clicked
    elif 'confirm' in request.form:
        #get all the data
        repo_name = request.form['repo_name']
        new_desc = request.form['new_desc']
        #check data
        if repo_name!="" and new_desc!="":
            #get the index of the tuple that contains the repo name
            result = [tup[0] for tup in list].index(repo_name)
            #get the values that wont change
            name=list[result][0]
            path=list[result][1]
            copy=list[result][3]
            #write new values
            list[result] = tuple((name,path,new_desc,copy))
            #write data to data.json
            write_json(list)
    
    #logout
    #check if "Log out" button is clicked
    elif 'logout' in request.form:    
        #log out the user and redirect back to login.html
        session.pop("logged-in", None)
        return redirect(url_for('login_render'))
    
    #refresh the website after form is submitted
    return render_template('more.html')


#run the program(debug only!)
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
