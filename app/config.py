import json
import bcrypt
import os
import getpass
import subprocess
import shutil

# init variables
prompt = 0


# function that returns contents of a specified json file
def load_json(file):
    with open(file, "r") as f:
        return json.load(f)


# load contents of json files into local dictionaries
config_dict = load_json("database/config.json")
data_dict = load_json("database/data.json")


# function that writes specified data to a specified json file
def write_json(value, file):
    json_object = json.dumps(value, indent=4)
    with open(file, "w") as f:
        f.write(json_object)


# function that hashes a specified password and returns it in a format compatable with json
def hash_password(password):
    # encode into bytes and hash password and add salt
    bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    # decode into string and convert to json compatable format
    hash_json = hash.decode("utf8").replace("'", '"')
    return hash_json


# function that changes specified values of all repositories in data.json
def change_data(location, user):
    for key in data_dict:
        # change path value in local dict
        data_dict[key][0] = f"{user}@{config_dict['storage_path']}:{location}{key}.git"


# first time setup
def first_time_setup():
    os.system("clear")
    # if app isnt configured yet
    if len(config_dict) == 0:
        # password setup and hash
        password = input("Create password: ")
        config_dict["password"] = hash_password(password)
        print(f"Password set to {password}")
        # storage location setup
        path = input("Set storage location for your repositories: ")
        # add the / at the end of the path if the user hadnt already added it
        if path[-1] != "/":
            path = path + "/"
        # store path into local dict
        config_dict["storage_path"] = path
        print(f"Storage path set to: {path}")
        # print host ip adress
        # decode command output into a string
        output = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        # remove \n from the end of the command output
        host_ip = output.strip()
        # store path into local dict
        config_dict["server_IP"] = host_ip
        print(f"Server IP adress: {host_ip}")
        # user which will use the git server
        username = input("Set server user(leave blank for current linux user): ")
        # get current linux user if user didnt specify a user
        if username == "":
            username = getpass.getuser()
        # store username into local dict
        config_dict["server_user"] = username
        print(f"Server user: {username}")
        # generate secret key for flask sessions and store it into local dict
        secret_key = os.urandom(24).hex()
        config_dict["app_secret_key"] = secret_key
        # write everything to config.json
        write_json(config_dict, "database/config.json")
        print("Setup complete!")
        print("\n", end="")
        enter = input("Press ENTER to continue")
        os.system("clear")
    # if everything is already setup
    else:
        print("Everything is already set up")
        print("\n", end="")
        enter = input("Press ENTER to continue")
        os.system("clear")


# function that changes the password
def change_password():
    os.system("clear")
    while True:
        # if old password is entered correctly
        old_password = input("Enter current password: ")
        result = bcrypt.checkpw(
            old_password.encode("utf-8"), config_dict["password"].encode("utf-8")
        )
        if result == True:
            new_password = input("Enter new password: ")
            # change password in local array and write changes to config.json
            config_dict["password"] = hash_password(new_password)
            write_json(config_dict, "database/config.json")
            print(f"password changed to: {new_password}")
            print("\n", end="")
            enter = input("Press ENTER to continue")
            os.system("clear")
            break
        else:
            print("Incorrect password, try again")


# function that changes storage location for all repositories
def change_storage():
    os.system("clear")
    new_location = input("Set new storage location for repositories: ")
    # add / to the end of path if user hadnt already
    if new_location[-1] != "/":
        new_location = new_location + "/"
    prompt = input(
        f"All of your repositories will be moved from {config_dict['storage_path']} to {new_location} do you want to continue[y/n]? "
    )
    if prompt == "Y" or prompt == "y":
        # scan repository storage location and move all repositories from old path to new path
        obj = os.scandir(config_dict["storage_path"])
        print("\n", end="")
        for entry in obj:
            if entry.is_dir() and ".git" in entry.name:
                # get current repository location
                old = config_dict["storage_path"] + entry.name
                # move repository to new location
                new = new_location + entry.name
                shutil.move(old, new)
                print(
                    f"Moved {entry.name} from {config_dict['storage_path']} to {new_location}"
                )
        obj.close()
        # change vaules locally and write changes to data.json and config.json
        config_dict["storage_path"] = new_location
        change_data(new_location, config_dict["server_user"])
        print(f"Storage location changed to: {new_location}")
        write_json(config_dict, "database/config.json")
        write_json(data_dict, "database/data.json")
    print("\n", end="")
    enter = input("Press ENTER to continue")
    os.system("clear")


# function that changes git server user
def change_user():
    os.system("clear")
    new_user = input("Change server user(leave blank for current user): ")
    # get current linux user, get current username if user didnt specify
    if new_user == "":
        new_user = getpass.getuser()
    # change values locally and write changes to json
    config_dict["server_user"] = new_user
    change_data(config_dict["storage_path"], new_user)
    write_json(config_dict, "database/config.json")
    write_json(data_dict, "database/data.json")
    print(f"Server user changed to: {new_user}")
    print("\n", end="")
    enter = input("Press ENTER to continue")
    os.system("clear")


# function that deletes all repository data
def delete_app_data():
    os.system("clear")
    print(
        "All repository data will be deleted from the application, but all the repositories stored on the server will still stay intact"
    )
    prompt = input("Are you sure you want to continue [y/n]? ")
    if prompt == "Y" or prompt == "y":
        # clear local repo dictionary and overwrite all data with an empty dictionary in data.json
        data_dict.clear()
        write_json(data_dict, "database/data.json")
        print("Operation complete")
    print("\n", end="")
    enter = input("Press ENTER to continue")
    os.system("clear")


# assign a specific function to every option for change configuration screen
func_dict_2 = {
    1: change_password,
    2: change_storage,
    3: change_user,
    4: delete_app_data,
}


# function that changes the app configuration
def change_config():
    os.system("clear")
    prompt = 0
    while prompt != 5:
        try:
            print("Change configuration: ")
            print("\n", end="")
            print("[1] Change password")
            print("[2] Change storage location")
            print("[3] Change server user")
            print("[4] Delete app data")
            print("[5] Go back")
            print("\n", end="")
            prompt = int(input("Chose an option: "))
            # run the function assigned to a specified option
            func_dict_2[prompt]()
        # invalid input
        except (ValueError, KeyError):
            os.system("clear")
    os.system("clear")


# function that imports local repositories into the app (into data.json)
def import_repos():
    os.system("clear")
    print("Scanning " + config_dict["storage_path"])
    print("\n", end="")
    # scan the storage location
    obj = os.scandir(config_dict["storage_path"])
    to_import = []
    for entry in obj:
        # if folder ends with .git and doesent already exist in the app
        if (
            entry.is_dir()
            and ".git" in entry.name
            and entry.name.replace(".git", "") not in data_dict
        ):
            print(entry.name)
            # create an array of repositories to import
            to_import.append(entry.name)
    obj.close()
    # if there are repositories to import
    if len(to_import) != 0:
        print("\n", end="")
        print("Listed repositories are not imported")
        prompt = input("Do you wish to import these repositories into the app [y/n]? ")
        print("\n", end="")
        if prompt == "Y" or prompt == "y":
            # add repository data into local repo dict
            for i in to_import:
                name = i.replace(".git", "")
                path = f"{config_dict['server_user']}@{config_dict['server_IP']}:{config_dict['storage_path']}{i}"
                print(f"Repository name: {name}")
                # let the user create repository description which will be displayed in the app
                desc = input("Create repository description(optional): ")
                # set default description
                if desc == "":
                    desc = "No description"
                print(f"Repository description: {desc}")
                print(f"Repository path: {path}")
                # add repo info to local dict
                data_dict[name] = [path, desc]
                print("\n", end="")
            # write new repository data into data.json
            write_json(data_dict, "database/data.json")
            print("All repositories are successfully imported")
    else:
        print("All repositories are already imported/no repositories were detected")
    print("\n", end="")
    enter = input("Press ENTER to continue")
    os.system("clear")


# function that prints out current app configuration
def display_conf():
    os.system("clear")
    # if user ran first time setup
    if len(config_dict) != 0:
        print("Current configuration:")
        print("\n", end="")
        print(f"Server IP adress: {config_dict['server_IP']}")
        print(f"Repositories storage location: {config_dict['storage_path']}")
        print(f"Git server user: {config_dict['server_user']}")
    # if app isnt configured yet
    else:
        print("The app is not yet configured, run first time setup")
    print("\n", end="")
    enter = input("Press ENTER to continue")
    os.system("clear")


# assign every function to the specified option in the main config screen
func_dict_1 = {1: first_time_setup, 2: change_config, 3: import_repos, 4: display_conf}

# main app screen
os.system("clear")
while prompt != 5:
    try:
        print("Configuration options: ")
        print("\n", end="")
        print("[1] First time setup")
        print("[2] Change configuration")
        print("[3] Import local repositories into the app")
        print("[4] Display current configuration")
        print("[5] Exit")
        print("\n", end="")
        prompt = int(input("Chose an option: "))
        # run function assigned to the specified option
        func_dict_1[prompt]()
    # invalid input
    except (ValueError, KeyError):
        os.system("clear")
