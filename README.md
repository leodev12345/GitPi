# GitPi
> A simple web ui app that gives you basic controls over your git server.

## Table of Contents
* [General Info](#general-information)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Credits](#credits)
* [Contact](#contact)


## General Information
A simple git server web app written in python using Flask, it was intended to be used on a raspberry pi but it should work on pretty much any linux machine.

Allows you to have some basic controls over your repositories inside your browser so you don't have to SSH into the server every time.

## Features

- Login page
- Creating repositories 
- Renaming repositories 
- Deleting repositories 
- Display basic repository info
   - Name 
   - Description
   - Full path that you can copy to clipboard


## Screenshots
![Login](./screenshots/login_page.png)

Login page

![Homepage](./screenshots/homepage.png)

Homepage

![more](./screenshots/more_options.png)

More options page
## Setup
Dependencies
- Python 3 (I used 3.8 and 3.9)
- Flask 
- Bcrypt

To install these run:

`sudo apt update`

`sudo apt install python3`

`pip3 install flask`

`pip3 install bcrypt`

If you dont have pip3 installed run:

`sudo apt install python3-pip`

Also if you havent already you should setup a DHCP reservation so that your servers IP adress doesent change.

After installing dependencies clone this repository with git, or you can just download it and unzip it.

`git clone https://github:com/leodev12345/gitpi`

After cloning the repository run the `setup.py` located in the root of the repository

`python3 setup.py`

The setup will ask you to create a password you will use to login into the web ui and will ask you to enter the folder path where your repositories will be stored.

After configuring the app it will print out the servers IP adress that will be used to access the web ui.

The username the program prints out is the linux user which will be used to run the server, its just setup as the current user so if you want it to be a different user you will have to login into that user and than run the setup.

NOTE: You can run the app by just running the python file but it's not the most efficient way and is only really good for debugging or testing the app, you can use tools like guincorn to run it the proper way, more info about that [here](https://flask.palletsprojects.com/en/2.3.x/deploying/).

So with that said you can run the app by running the `app.py` with python

`python3 app.py`

If you run into issues with permissions you could use authbind to allow normal user access to the port 80, There is a guide on how to do it [here](https://gist.github.com/justinmklam/f13bb53be9bb15ec182b4877c9e9958d).

After thats done just go to the specified IP adress in your browser and enter the password you just setup.

## Usage
To create repositories you have to enter the name for the repo and click create, description is optional, the app will than init a bare git repository in the storage location you specified in the setup.

You can view all the repositories you created on the homepage and copy their path with the copy button

If you want to rename, delete or change description of some repositories you can click the tree dots on the top navigation bar which will lead you to the more options page where you can also log out of the app.

If you want to reset the configuration just edit the `config.json` in the `database` folder, than delete everything and type in `[]`, after that you can run the `setup.py` again to set up new config, currently there is no way to apply new configuration to already existing repositories so you will have to manually edit the `data.json` where repository info is stored.

Currently there is no way to import already existing repositorieson the server into the app so you will have to also enter them manually into `data.json`.

Also note when you delete a repository it's only deleted from the app and not from the device, I did this for security reasons just in case.
## Project Status
I made this project for fun and it's features are very limited, I might add more features later, but probably not because I made this project to have some basic things i needed for my server.

I would also not recommend using this if your server is open to the internet, I don't know how secure this app is but I'm guessing that it's not, but if you are just using it on your private home network than it's fine.

If you need a more advanced web ui for your git server than use something like gitea or something similar, or if you want to add more feaures you can fork this repository and do whatever you want with it.

## Credits
I modified the Git logo that is created by [Jason Long](https://twitter.com/jasonlong) and licensed under the [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/) to create the icon for the app, it's downloaded from [https://git-scm.com/downloads/logos](https://git-scm.com/downloads/logos) 

Everyting else is coded and made by me. 
## Contact
Email: [pycityproject@gmail.com](mailto:pycityproject@gmail.com)

Discord: [https://dsc.gg/leogames](https://dsc.gg/leogames)




