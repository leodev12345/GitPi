from flask import Flask, render_template, request, redirect, url_for
import json
import os
import bcrypt

logged_in=False
#Storing values locally
list=[]
config_list=[]
#charecters not allowed in repo names
ilegal_charecters=[" ","#","<",">","$","+","%","!","`","&","*","|","{","}","[","]","@",":","/","\"","\\","\'","\(","\)","=","?","€",";",".",",","§","¤","ß","Ł","ł","÷","×","¸","¨","~","ˇ","^","˘","°","˛","˙","´","˝"]
#load json values into the local list every time the program starts
f=open("database/data.json")
data=json.load(f)
for i in data:
    list.append(tuple((i[0],i[1],i[2],i[3])))

with open("database/config.json", "r") as f:
    config_data=json.load(f)

config_path=config_data[1]
config_ip=config_data[2]
config_user=config_data[3]

print(config_data)

app = Flask(__name__)

#write values to data.json
def write_json(arg):
    json_object=json.dumps(arg, indent=4)
    with open("database/data.json", "w") as file:
        file.write(json_object)

#if form submitted
@app.route('/', methods=['POST'])
def my_form_post():
    #collecting info
    text = request.form['text']
    desc = request.form['desc']
    #checking info
    if text!="" and any(ele in text for ele in ilegal_charecters)==False:
        if desc=="":
            desc="No description"
        copy_text=config_user+"@"+config_ip+":"+config_path+text+".git"

        #create the repo on the server
        #dir_name=text+".git"
        #os.system("cd "+config_path)
        #os.system("mkdir "+dir_name)
        #os.system("cd "+dir_name)
        #os.system("git init --bare")
        
        #add info to list
        list.insert(0,tuple((text,"Path: "+copy_text,desc,copy_text)))
        write_json(list)

    #refresh
    return redirect(url_for('my_form_post'))

#show homepage
@app.route("/")
def template_test():
    if logged_in==True:
        return render_template('index.html', my_list=list)
    elif logged_in==False:
        return redirect(url_for('login_render'))

#show more.html
@app.route("/more")
def more_render():
    if logged_in==True:
        return render_template('more.html')
    elif logged_in==False:
        return redirect(url_for('login_render'))

#show login.html
@app.route("/login")
def login_render():
    return render_template('login.html')

#check if password is correct
@app.route("/login", methods=['POST'])
def login():
    password=request.form['password']
    result = bcrypt.checkpw(password.encode('utf-8'), config_data[0].encode('utf-8'))
    if result==True:
        global logged_in
        logged_in=True
        return redirect(url_for('template_test')) 
    else:
        return redirect(url_for('login_render'))


@app.route("/more", methods=['POST'])
def more():

    #renaming repos
    if 'rename' in request.form:
        old_name = request.form['old_name']
        new_name = request.form['new_name']
        if old_name!=new_name and new_name!="" and old_name!="" and " " not in old_name and " " not in new_name and any(ele in new_name for ele in ilegal_charecters)==False:
            #rename repo on server
            #os.system("cd "+config_path)
            #os.system("mv "+old_name+".git"+" "+new_name+".git")
        
            result = [tup[0] for tup in list].index(old_name) #index of the tuple containing the old name
            #change values
            desc = list[result][2]
            path="Path: "+config_user+"@"+config_ip+":"+config_path+new_name+".git"
            copy=config_user+"@"+config_ip+":"+config_path+new_name+".git"
            #write new values
            list[result]=tuple((new_name,path,desc,copy))
            write_json(list)

    #deleting repos
    elif 'remove' in request.form:
        delete_name = request.form['name_1']
        delete_name_confirm = request.form['name_2']
        if delete_name==delete_name_confirm and delete_name!="":
            result = [tup[0] for tup in list].index(delete_name) #get index of the tuple that needs to be deleted
            del list[result] #delete from list
            #delete on device
            #os.system("cd "+config_path)
            #os.rmdir(delete_name+".git")
            write_json(list)

    #changing repo description
    elif 'confirm' in request.form:
        repo_name = request.form['repo_name']
        new_desc = request.form['new_desc']
        if 'confirm' in request.form and repo_name!="" and new_desc!="":
            result = [tup[0] for tup in list].index(repo_name) #get the index of the tuple that contains the repo name
            #get values that wont change
            name=list[result][0]
            path=list[result][1]
            copy=list[result][3]
            #write new values
            list[result] = tuple((name,path,new_desc,copy))
            write_json(list)
    
    #logout
    elif 'logout' in request.form:    
        global logged_in
        logged_in=False
        return redirect(url_for('login_render'))
    
    #to refresh website
    return render_template('more.html')


#run
if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
