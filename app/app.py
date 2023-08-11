from flask import Flask, render_template, request, redirect, url_for, session  
import json
import os
import bcrypt
from functools import wraps
import subprocess

#charecters not allowed in repo names
ilegal_charecters=[" ","#","<",">","$","+","%","!","`","&","*","|","{","}","[","]","@",":","/","\"","\\","\'","\(","\)","=","?","€",";",".",",","§","¤","ß","Ł","ł","÷","×","¸","¨","~","ˇ","^","˘","°","˛","˙","´","˝"]
#get current working path 
current_path=os.path.abspath(os.getcwd())
os.chdir(current_path)
#load json values into the local array every time the program starts
#chdir to project working folder to avoid loading database from wrong path when the working dir changes
#function that returns contents of a specified json file
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)
#load json into local dicts
repo_dict=load_json("database/data.json")
config_dict=load_json("database/config.json")

#app init
app = Flask(__name__)
app.secret_key=config_dict["app_secret_key"]

#decorator that redirects to login page
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "logged-in" not in session:
            return redirect(url_for("login_render"))
        return func(*args, **kwargs)
    return wrapper

#function that writes all the repo data to data.json
def write_json(value):
    json_object=json.dumps(value, indent=4)
    os.chdir(current_path)
    with open("database/data.json", "w") as file:
        file.write(json_object)

#creating repos
@app.route('/', methods=['POST'])
def create_repo():
    #collecting info
    name = request.form['text']
    desc = request.form['desc']
    #checking info
    if name!="" and any(ele in name for ele in ilegal_charecters)==False:
        #set default description
        if desc=="":
            desc="No description"
        #full path to the repo
        path=f"{config_dict['server_user']}@{config_dict['server_IP']}:{config_dict['storage_path']}{name}.git"
        
        #create the repo on the server
        dir_name=f"{name}.git"
        os.chdir(config_dict["storage_path"])
        os.mkdir(dir_name)
        os.chdir(dir_name)
        os.system("git init --bare")
        
        #add all the data to list and write it to data.json
        repo_dict[name]=[path, desc]
        write_json(repo_dict)

    #refresh the website after form is submitted
    return redirect(url_for('create_repo'))

#render the homepage
@app.route("/")
@login_required
def index_render():
    return render_template('index.html', repos=dict(reversed(list(repo_dict.items()))))

#render more options
@app.route("/more")
@login_required
def more_render():
    return render_template('more.html')

#render login page
@app.route("/login")
def login_render():
    return render_template('login.html')

#login page functionality
@app.route("/login", methods=['POST'])
def login():
    #get the entered password and compare it to stored hashed password
    password=request.form['password']
    result = bcrypt.checkpw(password.encode('utf-8'), config_dict["password"].encode('utf-8'))
    #log in if password is correct and display an error if not
    if result==True:
        session["logged-in"]=True
        return redirect(url_for('index_render')) 
    else:
        return render_template('login.html', error="Incorrect password")


# more options page functionality
def rename_repo():
    #get all the data
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    #check data
    if old_name!=new_name and new_name!="" and old_name!="" and any(ele in new_name for ele in ilegal_charecters)==False:
        #rename repo on server
        os.chdir(config_dict["storage_path"])
        os.rename(f"{old_name}.git",f"{new_name}.git")
        #rename repo in local dict
        repo_dict[new_name]=[f"{config_dict['server_user']}@{config_dict['server_IP']}:{config_dict['storage_path']}{new_name}.git", repo_dict[old_name][1]]
        del repo_dict[old_name]
        #write data to data.json
        write_json(repo_dict)
    return redirect(url_for("more"))

def delete_repo():
    #get all the data
    delete_name = request.form['name_1']
    delete_name_confirm = request.form['name_2']
    #check data
    if delete_name==delete_name_confirm and delete_name!="":
        #delete from local dict
        del repo_dict[delete_name]
        #write data to data.json
        write_json(repo_dict)
    return redirect(url_for("more"))

def change_repo_desc():
    #get all the data
    repo_name = request.form['repo_name']
    new_desc = request.form['new_desc']
    #check data
    if repo_name!="" and new_desc!="":
        #change data in local dict
        repo_dict[repo_name][1]=new_desc
        #write data to data.json
        write_json(repo_dict)
    return redirect(url_for("more"))

def logout():
    #log out the user and redirect back to login.html
    session.pop("logged-in", None)
    return redirect(url_for('login_render'))

more_dict={
    "rename": rename_repo,
    "remove": delete_repo,
    "confirm": change_repo_desc,
    "logout": logout
}

@app.route("/more", methods=['POST'])
def more():
    for key in request.form:
        if key in more_dict:
            more_dict[key]()
    return redirect(url_for("more"))

@app.route("/<id>", methods=['GET', 'POST'])
@login_required
def repo(id):
    try:
        path=f"{config_dict['storage_path']}{id}.git"
        os.chdir(path)
        files = subprocess.check_output(['git', 'ls-tree', '--name-only', '-r', 'HEAD']).decode('utf-8')
        commits = subprocess.check_output(['git', 'log', '--pretty=%B']).decode('utf-8').strip()
    except subprocess.CalledProcessError:
        files="No files are created yet"
        commits="No commits yet"
    return render_template('repo.html', files=files, commits=commits, name=id, desc=repo_dict[id][1], path=repo_dict[id][0])
#run the program(debug only!)
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
