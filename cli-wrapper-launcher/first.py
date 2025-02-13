import os
import pwd

import re
import typer
import subprocess
import shutil

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.rule import Rule
from rich.prompt import Prompt

console = Console()
def get_logged_user():
    uid = os.geteuid()
    user = pwd.getpwuid(uid).pw_name
    return user

def __distinct_executables_profiles_by_logged_user(logged_user):
    try:
        distinct_executables_profiles = {}
        with open('mockdb.txt','r') as file:
            for riga in file:
                splitted = riga.split(":")
                if splitted[0] == logged_user:
                    distinct_executables_profiles.setdefault(splitted[1],[]).append(splitted[2])

        return distinct_executables_profiles
    except FileNotFoundError:
        console.print(f"Errore: Il file mockdb.txt non è stato trovato",style="bold red")
    except Exception as e:
        console.print(f"Si è verificato un errore: {e}",style="bold red")

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
        console.print(f"Errore: Il file mockdb.txt non è stato trovato",style="bold red")
    except Exception as e:
        console.print(f"Si è verificato un errore: {e}",style="bold red")

def __tables_executables_profiles_by_logged_user(logged_user):
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
            console.print(t)

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
        console.print("There aren't profile linked to you", style="bold red")

def __tables_profiles_by_logged_user_by_executable(logged_user,executable):
    profiles = __profiles_by_logged_user_by_executable(logged_user, executable)
    if len(profiles) > 0:
        t = Table(title=executable)
        t.add_column("#")
        t.add_column("Profile")
        for i in range(len(profiles)):
            t.add_row(str(i+1),profiles[i])
        console.print(t)
        if len(profiles)>1:
            indexes = [str(i+1) for i in range(len(profiles))]

            index = Prompt.ask("Which profile do you want run?",choices = indexes)
            response = Prompt.ask(f"Are you sure that {profiles[int(index)-1]} is the right profile?",choices=["Y","N"])
        else:
            response = Prompt.ask(f"Are you sure that {profiles[0]} is the right profile?",choices=["Y","N"])
    else:
        console.print("There aren't profile linked to you",style="bold red")

def read_profile_from_mock_database(username,executable):
    try:
        with open('mockdb.txt','r') as file:
            for riga in file:
                splitted = riga.split(":")
                if splitted[0] == username and splitted[1] == executable:
                    return splitted[2]
    except FileNotFoundError:
        console.print(f"Errore: Il file mockdb.txt non è stato trovato",style="bold red")
    except Exception as e:
        console.print(f"Si è verificato un errore: {e}",style="bold red")

def __info_about_profiles(username,profile):
    try:
        with open('profileinfo.txt','r') as file:
            for riga in file:
                splitted = riga.split("::")
                if splitted[0].strip() == username.strip() and splitted[1].strip() == profile.strip():
                    return splitted[2]
        return "Profile doesn't exists or you are not the owner."
    except FileNotFoundError:
        console.print(f"Errore: Il file profileinfo.txt non è stato trovato",style="bold red")
    except Exception as e:
        console.print(f"Si è verificato un errore: {e}",style="bold red")

def __cat_profile_file(username,profile):
    try:
        with open('profilepath.txt','r') as file:
            for riga in file:
                splitted = riga.split("::")
                if splitted[0].strip() == username.strip() and splitted[1].strip() == profile.strip():
                    print(splitted[2])
                    result = subprocess.run(['cat',splitted[2].strip()],capture_output=True,text=True)
                    if result.returncode == 0:
                        if "//" in profile: #Sottoprofilo generico
                            #regex: profile\s+pierpaolosestito\s*\{[^{}]*\}
                            #print(result.stdout)
                            regex = rf'profile\s+{profile.strip().split("//")[1]}\s*\{{[^{{}}]*\}}'
                            match = re.search(regex,result.stdout)
                            if match:
                                print(match.group())
                        else: #Profilo generico senza i sottoprofili
                            output = result.stdout
                            output = output.replace(f"profile {profile}","PLACEHOLDER")
                            print(output)
                            regex = rf'profile\s+.+\s*\{{[^{{}}]*\}}'

                            match = re.search(regex,output)
                            #print(match)
                            #print("PROFILE "  + profile)
                            while match:
                                #print(match.group())

                                output = output.replace(match.group()," ")
                                match = re.search(regex,output)
                            print(output.replace("PLACEHOLDER",f"profile {profile}"))

                    else:
                        console.print(f"Si è verificato un errore", style="bold red")
    except FileNotFoundError:
        console.print(f"Errore: Il file profilepath.txt non è stato trovato",style="bold red")
    except Exception as e:
        console.print(f"Si è verificato un errore: {e}",style="bold red")

def which(script_to_launch):
    try:
        return shutil.which(script_to_launch)
    except Exception as e:
        console.print(f"Si è verificato un errore: {e}", style="bold red")

def aa_exec(executable_path,profile):
    console.print(f"Eseguendo aa-exec -p {profile} {executable_path} :smiley:",style="bold yellow")
    console.print(Rule("Output dell'eseguibile"))
    subprocess.run(['aa-exec','-p',profile,executable_path])#,capture_output=True,text=True,check=True)

def check_is_a_valid_abs_path(executable_path):
    if not os.path.isabs(executable_path):
        return "[bold red] Error: Is not an absolute path [/bold red]"

    if not os.path.exists(executable_path):
        return "[bold red] Error: Executable doesn't exists [/bold red]"

    if not os.access(executable_path, os.X_OK):
        return "[bold red] Error: Is not an executable[/bold red]"

    return True

def main(script_to_launch: str):
    console.print(f"We are executing which on script_to_launch: [underline]{script_to_launch}[/underline] (shutil.which)",style="bold blue")
    executable_path = which(script_to_launch)
    if executable_path is None:
        console.print("[bold red]Executable path doesn't found[/bold red]")
        executable_path = Prompt.ask("Insert absolute path of the executable")
        check_valid_path = check_is_a_valid_abs_path(executable_path)
        if check_valid_path != True:
            console.print(check_valid_path)
            return
    console.print(f"Result {executable_path}",style="bold blue")
    console.print(Rule("Who is the user?"))
    console.print("We are checking for the logged user",style="bold blue")
    current_user = get_logged_user()
    #current_user = "pierpaolodue"
    console.print(f"We get the logged user : [underline]{current_user}[/underline] (os.getlogin())",style="bold blue")
    console.print(Rule("Check the profile linked to the user for the executable"))
    console.print(f"SIMPLE CASE: We are searching for the profile associated to the [underline]{current_user}[/underline] for [underline]{executable_path}[/underline]",style="bold blue")
    profile = read_profile_from_mock_database(current_user,executable_path)
    #profile = "/usr/bin/forse.sh//pierpaolodue"
    console.print(f"Result {profile}",style="bold blue")
    console.print(Rule("Execution"))
    aa_exec(executable_path,profile)


    #Other commands
    #__tables_executables_profiles_by_logged_user(current_user)
    #__cat_profile_file(current_user,profile)
    print(f"Info {__info_about_profiles(current_user,profile)}")
    #__tables_profiles_by_logged_user_by_executable(current_user,executable_path)


if __name__ == "__main__":
    typer.run(main)