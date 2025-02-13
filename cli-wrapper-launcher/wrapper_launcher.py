from sys import executable

import typer
import os
import pwd
import subprocess
import shutil


from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt,Confirm
from rich.rule import Rule

from my_shared_library.alerts import ERROR_MESSAGE, WARNING_MESSAGE, INFO_MESSAGE, SUCCESS_MESSAGE
from my_shared_library.database_connection import DatabaseConnection
from my_shared_library.kcontent_dao import KContentDAO,KContent
from my_shared_library.aa_utilities import get_kernel_content_for_db_content,get_infos_to_add_in_database,get_enforce_mode_profiles
from my_shared_library.users_utilities import users_list,get_logged_user
from my_shared_library.info_dao import InfoDAO,Info


def preprocessing():
    db_connection = DatabaseConnection()
    k_dao = KContentDAO(db_connection.get_cursor())
    info_dao = InfoDAO(db_connection.get_cursor())
    md5_content = get_kernel_content_for_db_content()
    #print(md5_content)
    u_list = users_list()
    kcontent = k_dao.read_last_record()
    #print(kcontent)
    k_dao.delete_all()
    info_dao.delete_all()
    if kcontent is not None:
        if md5_content != kcontent.content:
            #print("Dobbiamo modificare")
            #TODO: Posso fare una versione pro che mi prendo da kcontent.lastrow, se il last_row attuale del kernel è maggiore, leggo da kcontent.last_row altrimenti cancello tutto e riempio il database
            k_dao.delete_all()
            info_dao.delete_all()
            filtered_profiles_info,last_row = get_infos_to_add_in_database(u_list)
            [info_dao.create(filt) for filt in filtered_profiles_info]
            k_dao.create(md5_content, last_row)
            #print("Database updated")
            #get_infos_to_add_in_database()
        else:
            pass
            #print(info_dao.read_all())
            #print("Database already updated.")
    else:
        #Dobbiamo inizializzare il database
        filtered_profiles_info,last_row = get_infos_to_add_in_database(u_list)
        [info_dao.create(filt) for filt in filtered_profiles_info]
        k_dao.create(md5_content,last_row)
        #print(k_dao.read_all())
        #print(info_dao.read_all())
        #print("Database inizializzato")



app = typer.Typer()
c = Console()

'''def get_logged_user():
    uid = os.geteuid()
    current_user = pwd.getpwuid(uid).pw_name
    return current_user
'''
def which(script_to_launch):
    try:
        return shutil.which(script_to_launch)
    except Exception:
        return None

def aa_exec(executable_path,user_profile):
    #try:
        #result = subprocess.run(['sudo','aa-exec','-p',user_profile,executable_path,r'''"Task done\";echo 'Some_bad_stuff' >> /tmp/mario-alviano.txt;#'''+"'"],capture_output=True,text=True)#,capture_output=True,text=True,check=True)
        result = subprocess.run(['sudo', 'aa-exec', '-p', user_profile, executable_path,],
                            capture_output=True, text=True)  # ,capture_output=True,text=True,check=True)
        print(f"Standard output {result.stdout}")
        if result.stderr != "":
            print(f"Standard error {result.stderr}")
        #if result.stderr != "":
            #raise subprocess.CalledProcessError(result.stderr)
    #except subprocess.CalledProcessError as e:
        #c.print(ERROR_MESSAGE(e))


def is_path_or_name(script_name_or_path: str):
    # If it contains directory separators and is absolute, it's a path
    if os.path.isabs(script_name_or_path):
        if os.path.exists(script_name_or_path):
            return "path"
        else:
            return "invalid_path"  # Absolute path but does not exist
    else:
        return "name"

def check_is_a_valid_abs_path(executable_path):
    if not os.path.isabs(executable_path):
        return "Error: Is not an absolute path."

    if not os.path.exists(executable_path):
        return "Error: Executable doesn't exists."

    if not os.access(executable_path, os.X_OK):
        return "Error: Is not an executable."

    return True
from typing import Optional
@app.command(help="Execute with the right AppArmor profile")
def launch(
    script_name_or_path: str = typer.Argument(
        ...,  # Required argument
        help=(
            "The name of a script (e.g., 'myscript.py') or an absolute path "
            "(e.g., '/usr/bin/myscript.py')."
        )
    ),
flags: Optional[str] = typer.Option(
        None,  # Optional argument
        help="A custom message, e.g., 'Pinuccio lancia la palla'."
    )
):
    #print(custom_message)
    #print(custom_message.split(" "))
    if flags:
        print(flags)
        print(flags.split(" "))
        return

    db_connection = DatabaseConnection()
    info_dao = InfoDAO(db_connection.get_cursor())
    result = is_path_or_name(script_name_or_path)
    executable_path = " "
    if result == "name":
        executable_path = which(script_name_or_path)
        if executable_path is None:
            c.print(ERROR_MESSAGE("Executable path doesn't found"))
            executable_path = Prompt.ask("Insert absolute path of the executable")
            check_valid_path = check_is_a_valid_abs_path(executable_path)

            if check_valid_path != True:
                c.print(ERROR_MESSAGE(check_valid_path))
                return
    elif result == "path":
        executable_path = script_name_or_path
    else:
        c.print(ERROR_MESSAGE("Absolute path or right script name."))
        return
    #current_user = get_logged_user()
    current_user = "pierpaolo-sestito"
    profiles = info_dao.get_profiles_by_username_by_executable(current_user,executable_path)
    #print(profiles)
    #profiles = ['/usr/bin/networkscript.sh//pierpaolo-sestito', '/usr/bin/networkscript.sh//pierpaolo-sestito']
    profiles = ['/usr/bin/bashnetworkversion.sh']
    if len(profiles) == 0:
        c.print(ERROR_MESSAGE(f"You do not have profile for this {executable_path}"))
        #TODO: Potremmo esegure lo script ugualmente
        return
    elif len(profiles) > 1:
        c.print(WARNING_MESSAGE(f"You have more than one profile for {executable_path}"))
        users_m = {index: value for index, value in enumerate(profiles)}
        options = ", ".join([f"{k}: {v}" for k, v in users_m.items()])
        c.print(f"Available users : {options}")
            #Voglio che continui qua la funzione: L'utente deve inserire
        selected_profile = ""
        while True:
            index_choice = Prompt.ask("Choose a single index")
            try:
                    # Controlla se l'input è un numero valido
                if not index_choice.strip().isdigit():
                    raise ValueError("Formato errore: devi inserire un solo numero.")

                user_index_choice = int(index_choice.strip())

                # Verifica se l'indice esiste nella mappatura
                if user_index_choice not in users_m:
                    raise ValueError("Indice non valido. Riprova.")

                selected_profile = users_m[user_index_choice]

                # Conferma selezione
                c.print(f"Hai scelto il valore: {selected_profile}")
                break  # Esci dal ciclo se tutto è corrett
            except ValueError as e:
                        #c.print(ERROR_MESSAGE("Inserisci solo numeri separati da virgola"))
                    c.print(ERROR_MESSAGE(f"{e}.\nRiprova di nuovo."))
        c.print(SUCCESS_MESSAGE(f"We are running {script_name_or_path} with {selected_profile}"))
        aa_exec(executable_path,selected_profile)
        return

    else:
        c.print(SUCCESS_MESSAGE(f"We are running {script_name_or_path} with {profiles[0]}"))
        aa_exec(executable_path,profiles[0])

def view_all_executables_confined_by_a_profile(current_user,executables,occurrences):
    t = Table(title = f"Executables where {current_user} has a profile")
    t.add_column("#")
    t.add_column("Profile")
    t.add_column("Num of profiles")
    print(f"A {executables}")
    for i in range(len(executables)):
        t.add_row(str(i+1),executables[i],str(occurrences[executables[i]]))
    c.print(t)
def view_profiles_by_logged_user_by_executable(script_name,executable_path,profiles,suggest_launch=False):
    if len(profiles) == 0:
        c.print(ERROR_MESSAGE("You do not have profiles."))
        return
    if len(profiles) == 1:
        c.print(INFO_MESSAGE(f"This is your unique profile {profiles[0]}"))
        if suggest_launch:
            is_confirmed = Confirm.ask(f"Do you want run {script_name} with {profiles[0]}?")
            if is_confirmed:
                aa_exec(executable_path,profiles[0])
            else:
                return
    else:
        t = Table(title = script_name)
        t.add_column("#")
        t.add_column("Profile")
        for i in range(len(profiles)):
            t.add_row(str(i + 1), profiles[i])
        c.print(t)
        if suggest_launch:
            indexes = [str(i + 1) for i in range(len(profiles))]

            index = Prompt.ask("Which profile do you want run?", choices=indexes)
            is_confirmed = Confirm.ask(f"Do you want run {script_name} with {profiles[int(index)-1]}?")
            if is_confirmed:
                aa_exec(executable_path,profiles[int(index)-1])
            else:
                return


@app.command(help="Read your AppArmor profiles")
def get_my_profiles(
    script_name_or_path: str = typer.Argument(
        None,  # Optional argument with default None
        help=(
            "The name of a script (e.g., 'myscript.py') or an absolute path "
            "(e.g., '/usr/bin/myscript.py'). If not provided, a default behavior will be applied."
        )
    ),
    suggest_launch: bool = typer.Option(False, help="Suggest launch configurations")
):
    if script_name_or_path:
        db_connection = DatabaseConnection()
        info_dao = InfoDAO(db_connection.get_cursor())
        current_user = get_logged_user()
        result = is_path_or_name(script_name_or_path)
        executable_path = " "
        if result == "name":
            executable_path = which(script_name_or_path)
            if executable_path is None:
                c.print(ERROR_MESSAGE("Executable path doesn't found"))
                executable_path = Prompt.ask("Insert absolute path of the executable")
                check_valid_path = check_is_a_valid_abs_path(executable_path)
                if check_valid_path != True:
                    c.print(ERROR_MESSAGE(check_valid_path))
                    return
        elif result == "path":
            executable_path = script_name_or_path
            script_name_or_path  = os.path.basename(script_name_or_path)
        else:
            c.print(ERROR_MESSAGE("Absolute path or right script name."))
            return

        print(executable_path)

        current_user = "pierpaolo-sestito"
        print(current_user)
        profiles = info_dao.get_profiles_by_username_by_executable(current_user,executable_path)
        print(profiles)
        profiles = ['/usr/bin/networkscript.sh//pierpaolo-sestito','/usr/bin/networkscript.sh//pierpaolo-sestito']

        #profiles = ['a','b','c']
        view_profiles_by_logged_user_by_executable(script_name_or_path,executable_path, profiles, suggest_launch)
    else:
        current_user = "pierpaolo-sestito"
        db_connection = DatabaseConnection()
        info_dao = InfoDAO(db_connection.get_cursor())
        lista = info_dao.read_all()
        executables = []
        for l in lista:
            print(f"L {l[1]}")
            if l[1] == current_user:
                print(f"L {l[2]}")
                executables.append(l[2])
        occurrences = {}
        for exec in executables:
            occurrences.setdefault(exec,0)
            occurrences[exec] = executables.count(exec)
            executables.count(exec)
        print(occurrences)
        view_all_executables_confined_by_a_profile(current_user,list(set(executables)),occurrences)
if __name__ == "__main__":
    preprocessing()
    app()