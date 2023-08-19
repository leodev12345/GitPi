from flask import Flask, render_template, request, redirect, url_for, session  
import json
import os
import bcrypt
from functools import wraps
import subprocess

#charecters not allowed in repo names
ilegal_charecters=[" ","#","<",">","$","+","%","!","`","&","*","|","{","}","[","]","@",":","/","\"","\\","\'","(",")","=","?","€",";",".",",","§","¤","ß","Ł","ł","÷","×","¸","¨","~","ˇ","^","˘","°","˛","˙","´","˝"]

#get current working path and chdir into it 
current_path=os.path.abspath(os.getcwd())
os.chdir(current_path)

#return specified json file contents
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)

#load json values into local dicts
repo_dict=load_json("database/data.json")
config_dict=load_json("database/config.json")

#app init
app = Flask(__name__)
app.secret_key=config_dict["app_secret_key"]

#decorator that redirects to login page if user is not logged in
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

def organize_files(file_list, name, branch):
    lines = file_list.strip().split('\n')
    file_structure = {}

    for line in lines:
        parts = line.split('/')
        current = file_structure

        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    def create_structure(structure, indent=""):
        result = ""
        keys = list(structure.keys())
        for index, name in enumerate(keys):
            content = structure[name]
            last_item = index == len(keys) - 1

            if content:
                result += f"{indent}{'└─ ' if last_item else '├─ '}{name}/\n"
                result += create_structure(content, indent + ('    ' if last_item else '│  '))
            else:
                result += f"{indent}{'└─ ' if last_item else '├─ '}{name}\n"
        return result

    organized_files = create_structure(file_structure)

    return f"{name}|{branch}\n"+organized_files

############################## Homepage ##############################

#render index.html and pass repo dictionary in reversed order to it (so new repositories appear on top)
@app.route("/")
@login_required
def index_render():
    return render_template('index.html', repos=dict(reversed(list(repo_dict.items()))))

#creating repositories
@app.route('/', methods=['POST'])
def create_repo():
    #collecting info on form sumit
    name = request.form['text']
    desc = request.form['desc']
    #checking info
    if name!="" and any(ele in name for ele in ilegal_charecters)==False:
        #set default description
        if desc=="":
            desc="No description"
        
        #create the bare git repo on the server
        dir_name=f"{name}.git"
        os.chdir(config_dict["storage_path"])
        os.mkdir(dir_name)
        os.chdir(dir_name)
        os.system("git init --bare")
        
        #path to the repo
        path=f"{config_dict['server_user']}@{config_dict['server_IP']}:{config_dict['storage_path']}{name}.git"
        #add all the data to local dict and write it to data.json
        repo_dict[name]=[path, desc]
        write_json(repo_dict)

    #refresh the website after form is submitted and processed
    return redirect(url_for('create_repo'))

############################## More options page ##############################

#rename repository
@app.route("/more/rename", methods=['POST'])
def rename_repo():
    #get all the data from the form
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    #check data
    if old_name!=new_name and new_name!="" and old_name!="" and any(ele in new_name for ele in ilegal_charecters)==False and new_name not in repo_dict:
        #rename git repo on the server
        os.chdir(config_dict["storage_path"])
        os.rename(f"{old_name}.git",f"{new_name}.git")
        
        #rename repo in local dict
        #create new dict key with new name and assign description from old key and and assign new path
        path = f"{config_dict['server_user']}@{config_dict['server_IP']}:{config_dict['storage_path']}{new_name}.git"
        desc = repo_dict[old_name][1]
        repo_dict[new_name]=[path, desc]
        #delete old repo key from the dict
        del repo_dict[old_name]
        #write data to data.json
        write_json(repo_dict)
    #redirect back to main more options page
    return redirect(url_for("more"))

#delete repository from app
@app.route("/more/delete", methods=['POST'])
def delete_repo():
    #get all the data from form
    delete_name = request.form['name_1']
    delete_name_confirm = request.form['name_2']
    #check data
    if delete_name==delete_name_confirm and delete_name!="":
        #delete repo key from local dict
        del repo_dict[delete_name]
        #write data to data.json
        write_json(repo_dict)
    #redirect back to more options main page
    return redirect(url_for("more"))

#change repo description
@app.route("/more/change_desc", methods=['POST'])
def change_repo_desc():
    #get all the data from the form
    repo_name = request.form['repo_name']
    new_desc = request.form['new_desc']
    #check data
    if repo_name!="" and new_desc!="":
        #change data in local repo dict
        repo_dict[repo_name][1]=new_desc
        #write data to data.json
        write_json(repo_dict)
    #redirect back to more options main page
    return redirect(url_for("more"))

#log out
@app.route("/logout", methods=['POST'])
def logout():
    #delete logged-in session to log out the user
    session.pop("logged-in", None)
    #redirect back to log in page
    return redirect(url_for('login_render'))

#a dictionary that assigns every from submit attribute value to its endpoint name
more_dict={
    "rename": "rename_repo",
    "remove": "delete_repo",
    "confirm": "change_repo_desc",
    "logout": "logout"
}

#render more.html
@app.route("/more")
@login_required
def more_render():
    return render_template('more.html')

#more options main page functionality
@app.route("/more", methods=['POST'])
def more():
    #find which name attribute request.form contains and redirect to proper page 
    for key in request.form:
        if key in more_dict:
            return redirect(url_for(more_dict[key]))

############################## Log in page ##############################

#render login.html page
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

############################## Repo info page ##############################

#endpoint with variable route containing repository name and the default branch
@app.route("/<id>", methods=['GET', 'POST'])
@login_required
def repo(id, selected_branch="master"):
    if request.method=="POST":
        selected_branch=request.form.get("branch_select")
    try:
        #get full repository path and chdir into it
        path=f"{config_dict['storage_path']}{id}.git"
        os.chdir(path)
        #get list of repository files and repository commit history
        branches = subprocess.check_output(['git', 'branch', '-a']).decode("utf-8")
        branches = branches.replace("* ", "").replace("  ", "").strip().split("\n")
        files = subprocess.check_output(['git', 'ls-tree', '--name-only', '-r', selected_branch]).decode('utf-8')
        files=organize_files(files, id, selected_branch)
        commits = subprocess.check_output(['git', 'log', '--pretty=%B', '--first-parent', selected_branch]).decode('utf-8').strip()
    #if above commands return an error(if the repository contains no files or commits)
    except subprocess.CalledProcessError:
        #set default file, branch and commit values
        files="No files are created yet"
        commits="No commits yet"
        branches=["No branches created"]
    #render page and pass all variables to it
    return render_template('repo.html', files=files, commits=commits, name=id, desc=repo_dict[id][1], path=repo_dict[id][0], branches=branches, current_branch=selected_branch)

############################################################################

#run the app(debug only!)
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

