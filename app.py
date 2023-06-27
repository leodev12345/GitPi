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
config=open("database/config.json")
config_data=json.load(config)
for i in data:
    list.append(tuple((i[0],i[1],i[2],i[3])))

for j in config_data:
    config_list.append(j[0])

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
        copy_text="pi@192.168.1.116:/home/pi/git/"+text+".git"

        #create the repo on the server
        #os.system('cd /home/pi/git')
        #os.system('mkdir '+text+'.git')
        #os.system('cd '+text+'.git')
        #os.system('git init --bare')
        print("--------Commands simulation--------")
        print('cd /home/pi/git')
        print('mkdir '+text+'.git')
        print('cd '+text+'.git')
        print('git init --bare')
        print("-----------------------------------")

        #add info to list
        list.insert(0,tuple((text,"Path: pi@192.168.1.116:/home/pi/git/"+text+".git",desc,copy_text)))
        write_json(list)

    #refresh
    return redirect(url_for('my_form_post'))

#show index.html
@app.route("/")
def template_test():
    if logged_in==True:
        return render_template('index.html', my_list=list)
    elif logged_in==False:
        return redirect(url_for('login_render'))

#show more.html
@app.route("/more")
def more_render():
    return render_template('more.html')

#show login
@app.route("/login")
def login_render():
    return render_template('login.html')

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
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    delete_name = request.form['name_1']
    delete_name_confirm = request.form['name_2']
    repo_name = request.form['repo_name']
    new_desc = request.form['new_desc']

    #renaming repos
    if old_name!=new_name and new_name!="" and old_name!="" and " " not in old_name and " " not in new_name and any(ele in new_name for ele in ilegal_charecters)==False:
        print("--------Commands simulation--------")
        print('cd /home/pi/git')
        print('mv '+old_name+'.git'+' '+new_name+'.git')
        print("-----------------------------------")
        result = [tup[0] for tup in list].index(old_name) #index of the tuple containing the old name
        #change values
        desc = list[result][2]
        path="Path: pi@192.168.1.116:/home/pi/git/"+new_name+".git"
        copy="pi@192.168.1.116:/home/pi/git/"+new_name+".git"
        #write new values
        list[result]=tuple((new_name,path,desc,copy))
        write_json(list)

    #deleting repos
    if delete_name==delete_name_confirm and delete_name!="":
        result = [tup[0] for tup in list].index(delete_name) #get index of the tuple that needs to be deleted
        del list[result] #delete from list
        write_json(list)

    #changing repo description
    if repo_name!="" and new_desc!="":
        result = [tup[0] for tup in list].index(repo_name) #get the index of the tuple that contains the repo name
        #get values that wont change
        name=list[result][0]
        path=list[result][1]
        copy=list[result][3]
        #write new values
        list[result] = tuple((name,path,new_desc,copy))
        write_json(list)
    if request.form['log_out'] == "Log out":
        global logged_in
        logged_in=False
        return redirect(url_for('template_test'))
    return render_template('more.html')


#run
if __name__ == '__main__':
    app.run(debug=False, port=80, host='0.0.0.0')
