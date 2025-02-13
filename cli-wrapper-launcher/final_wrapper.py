import typer
import os
import pwd
from sys import executable
import re
import subprocess
import shutil

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.rule import Rule

from alerts import ERROR_MESSAGE

app = typer.Typer()
c = Console()

def get_logged_user():
    uid = os.geteuid()
    current_user = pwd.getpwuid(uid).pw_name
    return current_user

def __distinct_executables_profiles_by_logged_user(logged_user):
    try:
        distinct_executables_profiles = {}
        with open('mockdb.txt', 'r') as file:
            for riga in file:
                splitted = riga.split(":")
                if splitted[0] == logged_user:
                    distinct_executables_profiles.setdefault(splitted[1], []).append(splitted[2])

        return distinct_executables_profiles
    except FileNotFoundError:
        c.print(ERROR_MESSAGE(f"Errore: Il file mockdb.txt non è stato trovato"))

def __profiles_by_logged_user_by_executable(logged_user,executable):
    try:
        profiles = []
        with open('mockdb.txt','r') as file:
            for riga in file:
                splitted = riga.split(":")
                if splitted[0] == logged_user and splitted[1] == executable:
                    profiles.append(splitted[2])

        return profiles
    except FileNotFoundError:
        c.print(ERROR_MESSAGE(f"Errore: Il file mockdb.txt non è stato trovato"))

#FE
def __tables_executables_profiles_by_logged_user(logged_user,suggest_launch):
    distinct_executables_profiles = __distinct_executables_profiles_by_logged_user(logged_user)
    if len(distinct_executables_profiles) > 0:
        i=1
        for chiave,valore in distinct_executables_profiles.items():
            t = Table(title=str(i) + ": " + chiave)
            t.add_column("#")
            t.add_column("Profile")
            for i in range(len(valore)):
                t.add_row(str(i+1) , valore[i])
            i+=1
            c.print(t)

        if suggest_launch:
            executables_list = list(distinct_executables_profiles.keys())
            executables_list_indexes = [str(i+1) for i in range(len(executables_list))]
            executable_index = Prompt.ask("Which exec do you want run?",choices = executables_list_indexes)
            response = Prompt.ask(f"Are you sure that you want run {executables_list[int(executable_index)-1]}",choices=['Y','N'])
            choosen_executable_profiles = distinct_executables_profiles[executables_list[int(executable_index)-1]]
            #print(f"Profiles of choosen executables {distinct_executables_profiles[executables_list[int(executable_index)-1]]}")
            choosen_executable_profiles_indexes = [str(i+1) for i in range(len(choosen_executable_profiles))]
            profile_index = Prompt.ask(f"Which profile of {executables_list[int(executable_index)-1]} do you want run?",choices=choosen_executable_profiles_indexes)
            print(choosen_executable_profiles[int(profile_index)-1])
    else:
        c.print("There aren't profile linked to you", style="bold red")

#FE
def __tables_profiles_by_logged_user_by_executable(logged_user,executable):
    profiles = __profiles_by_logged_user_by_executable(logged_user, executable)
    if len(profiles) > 0:
        t = Table(title=executable)
        t.add_column("#")
        t.add_column("Profile")
        for i in range(len(profiles)):
            t.add_row(str(i+1),profiles[i])
        c.print(t)
        if len(profiles)>1:
            indexes = [str(i+1) for i in range(len(profiles))]

            index = Prompt.ask("Which profile do you want run?",choices = indexes)
            response = Prompt.ask(f"Are you sure that {profiles[int(index)-1]} is the right profile?",choices=["Y","N"])
        else:
            response = Prompt.ask(f"Are you sure that {profiles[0]} is the right profile?",choices=["Y","N"])
    else:
        c.print("There aren't profile linked to you",style="bold red")

def read_profile_from_mock_database(username,executable):
    try:
        with open('mockdb.txt','r') as file:
            for riga in file:
                splitted = riga.split(":")
                if splitted[0] == username and splitted[1] == executable:
                    return splitted[2]
    except FileNotFoundError:
        c.print(f"Errore: Il file mockdb.txt non è stato trovato",style="bold red")

def which(script_to_launch):
    try:
        return shutil.which(script_to_launch)
    except Exception as e:
        c.print(f"Si è verificato un errore", style="bold red")

def aa_exec(executable_path,profile):
    c.print(f"Eseguendo aa-exec -p {profile} {executable_path} :smiley:",style="bold yellow")
    c.print(Rule("Output dell'eseguibile"))
    subprocess.run(['aa-exec','-p',profile,executable_path])#,capture_output=True,text=True,check=True)



#Script name e script_path
@app.command()
def get_my_profiles2(
    executable: str = typer.Option(None, help="Specify an executable name", show_default=True),
    suggest_launch: bool = typer.Option(False, help="Suggest launch configurations")
):

    current_user = get_logged_user()
    if executable:
        executable_path = which(executable)
        if executable_path is not None:
            __tables_profiles_by_logged_user_by_executable(current_user,executable_path)
        else:
            c.print(ERROR_MESSAGE("Script doesn't found"))
        return
    __tables_executables_profiles_by_logged_user(current_user,suggest_launch)

def __info_about_profiles(username,profile):
    try:
        with open('profileinfo.txt','r') as file:
            for riga in file:
                splitted = riga.split("::")
                if splitted[0].strip() == username.strip() and splitted[1].strip() == profile.strip():
                    return splitted[2]
        return "Profile doesn't exists or you are not the owner."
    except FileNotFoundError:
        c.print(ERROR_MESSAGE(f"Errore: Il file profileinfo.txt non è stato trovato"))

@app.command()
def info_about_profile(profile: str):
    current_user = get_logged_user()
    response = __info_about_profiles(current_user,profile)
    if "Doesnt' exists" not in response:
        c.print(f"[bold blue]{response}[/bold blue]")
    else:
        c.print(ERROR_MESSAGE(f"{response}"))
@app.command()
def launch(script_name:str):
    c.print(f"We are executing which on {script_name}")
    executable_path = which(script_name)
    if executable_path != None:
        c.print(f"Result {executable_path}", style="bold blue")
        c.print(Rule("Who is the user?"))
        c.print("We are checking for the logged user", style="bold blue")
        current_user = get_logged_user()
        # current_user = "pierpaolodue"
        c.print(f"We get the logged user : [underline]{current_user}[/underline] (os.getlogin())",
                      style="bold blue")
        c.print(Rule("Check the profile linked to the user for the executable"))
        c.print(
            f"SIMPLE CASE: We are searching for the profile associated to the [underline]{current_user}[/underline] for [underline]{executable_path}[/underline]",
            style="bold blue")
        profile = read_profile_from_mock_database(current_user, executable_path)
        # profile = "/usr/bin/forse.sh//pierpaolodue"
        c.print(f"Result {profile}", style="bold blue")
        c.print(Rule("Execution"))
        aa_exec(executable_path, profile)
    else:
        c.print(ERROR_MESSAGE("Script doesn't found"))



if __name__ == "__main__":
    app()