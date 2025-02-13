import subprocess
import time

from my_shared_library.aa_utilities import get_kernel_content_for_db_content, get_infos_to_add_in_database
from my_shared_library.database_connection import DatabaseConnection
from my_shared_library.info_dao import Info,InfoDAO
from my_shared_library.alerts import *
from my_shared_library.exceptions import StructureException, SynthaxException, SelectableException, RedundException, SelectException
from my_shared_library.kcontent_dao import KContentDAO

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import prompt
import typer
import os
from rich.console import Console
from rich.prompt import Confirm,Prompt
import xattr

from RlimitRecord import RlimitRecord
from apparmor_utilities_integration import check_syntax_with_apparmor_parser, aa_disable_with_apparmor, \
    get_enforce_mode_profiles, aa_enforce_with_apparmor, get_disabled_mode_profiles, apparmor_parser_active_profile, \
    get_complain_mode_profiles, aa_complain_with_apparmor
from bak_manager import delete_all_backup_for_each_subprofile, \
    create_backup_for_each_subprofile_in_order_to_work_on_copy_and_not_on_original, \
    copy_from_backup_file_to_original_after_process

from kernel_reader import template_method_to_read_kernel_and_process
from mappings_manager import clean_mappings_file, is_empty_mappings_file, generate_mappings_file
from profile_manager import extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile, \
    manipulate_directive_include_structure_directory_mappings, copy_and_check_syntax, \
    check_selectablesynthax_and_get_basepermissions_and_mapout_selectablerule, \
    refactoring_checkselectablesynthax_and_mapout_basepermissions_selectablerule, \
    uncomment_directive_include_structure_directory_mappings, check_rlimit_rules_and_mapout
from regexs import check_selectable_row, is_valid_include_pattern, extract_include_statements
from subprofile_manager import get_all_subprofiles, clean_subprofiles, create_subprofiles_in_the_structure, \
    check_select_synthax_and_get_aliases_selected_by_specific_subprofile, \
    refactoring_check_selectsyntax_and_get_selected_aliases_by_specific_subprofile, PROCESS_SUBPROFILES
from users_manager import users_list, users_without_files, __user_exists

c = Console()
app = typer.Typer(help="Admin Command Line Interface")
from config import APPARMOR_PATH

#APPARMOR_PATH = "/etc/apparmor.d/" #TODO: pydotenv

class DynamicProfileCompleter(Completer):
    def __init__(self, profiles):
        self.profiles = profiles

    def get_completions(self, document, complete_event):
        word = document.text
        for profile in self.profiles:
            if profile.startswith(word):
                yield Completion(profile, start_position=-len(word))

@app.command(help="Check the syntax of a generic AppArmor profile and ensure it complies with AppArmor standards.")
def aa_check_syntax(path_to_generic_profile:str): #Usiamo apparmor_parser -Q e poi check_syntax già creato che usiamo in altre funzioni
    try:
        check_syntax_with_apparmor_parser(path_to_generic_profile)
        copy_and_check_syntax(path_to_generic_profile)
        executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(path_to_generic_profile)
        (check_selectablesynthax_and_get_basepermissions_and_mapout_selectablerule(executable_name,
                                                                                   path_to_generic_profile))
        c.print(SUCCESS_MESSAGE("OK"))

    except SynthaxException as syntax_exception:
        c.print(ERROR_MESSAGE(syntax_exception))
    except SelectableException as selectable_exception:
        c.print(ERROR_MESSAGE(selectable_exception))
@app.command(help="Move an AppArmor profile to complain mode. Profiles in complain mode allow operations but log violations.")
def aa_complain(
    profile: str = typer.Argument(
        None,
        help="Nome del profilo da disabilitare"
    ),
    contains: str = typer.Option(
        None,
        "--contains",
        "-c",
        help="Filtra i profili che contengono una determinata stringa"
    )
):
    if profile:
        if os.path.exists(profile):
            if os.path.isfile(profile):
                c.print(INFO_MESSAGE(f"Trying to complain {profile}"))
                aa_complain_with_apparmor(profile)
            else:
                disabled_profiles = get_disabled_mode_profiles()
                enforce_profiles = get_enforce_mode_profiles()
                if profile in disabled_profiles or profile in enforce_profiles:
                    c.print(f"[green]Complainando il profilo:[/green] {profile}")
                    aa_complain_with_apparmor(profile)
                else:
                    c.print(f"[red]Errore:[/red] Il profilo '{profile}' non esiste.")
    else:
        e_or_d = Prompt.ask("Choose between 'enforce mode profiles'[0] or 'disabled mode profiles'[1]",choices=["0","1"])
        if e_or_d == 1:
            c.print("List all the disabled profiles...")
            disabled_profiles,leng = get_disabled_mode_profiles(contains)
            if len(disabled_profiles) == 0:
                c.print(ERROR_MESSAGE("There's no disable mode profiles in the system"))
                return

            if len(disabled_profiles) == 1:
                confirm = Confirm.ask(f"Do you want to enable {disabled_profiles[0]}")
                if confirm:
                    c.print(f"[green]Abilitiamo il profilo:[/green] {disabled_profiles[0]}")
                    aa_complain_with_apparmor(disabled_profiles[0])
                else:
                    return
            if len(disabled_profiles) > 1:
                # Visualizzazione elenco puntato
                c.print("[bold yellow]Elenco Puntato:[/bold yellow]")
                for item in disabled_profiles:
                    c.print(f"• {item}")

                # Prompt interattivo con autocompletamento dinamico
                profile_completer = DynamicProfileCompleter(disabled_profiles)
                response = None

                while response not in disabled_profiles:
                    response = prompt("Which profile do you want to enable? ", completer=profile_completer)

                    if response not in disabled_profiles:
                        c.print(f"[red]Errore:[/red] Il profilo '{response}' non è valido. Riprova.")

                c.print(f"[green]Complainando il profilo:[/green] {response}")
                aa_complain_with_apparmor(response)
        else:
            c.print("List all the enforce profiles...")
            enforce_profiles,leng = get_enforce_mode_profiles(contains)
            if len(enforce_profiles) == 0:
                c.print(ERROR_MESSAGE("There's no complain mode profiles in the system"))
                return

            if len(enforce_profiles) == 1:
                confirm = Confirm.ask(f"Do you want to enable {enforce_profiles[0]}")
                if confirm:
                    c.print(f"[green]Abilitiamo il profilo:[/green] {enforce_profiles[0]}")
                    aa_complain_with_apparmor(enforce_profiles[0])
                else:
                    return
            if len(enforce_profiles) > 1:
                # Visualizzazione elenco puntato
                c.print("[bold yellow]Elenco Puntato:[/bold yellow]")
                for item in enforce_profiles:
                    c.print(f"• {item}")

                # Prompt interattivo con autocompletamento dinamico
                profile_completer = DynamicProfileCompleter(enforce_profiles)
                response = None

                while response not in enforce_profiles:
                    response = prompt("Which profile do you want to enable? ", completer=profile_completer)

                    if response not in enforce_profiles:
                        c.print(f"[red]Errore:[/red] Il profilo '{response}' non è valido. Riprova.")

                c.print(f"[green]Abilitiamo il profilo:[/green] {response}")
                aa_complain_with_apparmor(response)
@app.command(help="Disable an AppArmor profile, stopping it from enforcing any restrictions.")
def aa_disable(
    profile: str = typer.Argument(
        None,
        help="Nome del profilo da disabilitare"
    ),
    contains: str = typer.Option(
        None,
        "--contains",
        "-c",
        help="Filtra i profili che contengono una determinata stringa"
    )
):
    if profile:
        if os.path.exists(profile):
            if os.path.isfile(profile):
                c.print(INFO_MESSAGE(f"Trying to disable {profile}"))
                aa_disable_with_apparmor(profile)
            else:
                enforce_profiles = get_enforce_mode_profiles()
                complain_profiles = get_complain_mode_profiles()
                if profile in enforce_profiles or profile in complain_profiles:
                    c.print(f"[green]Disabilitando il profilo:[/green] {profile}")
                    aa_disable_with_apparmor(profile)
                else:
                    c.print(f"[red]Errore:[/red] Il profilo '{profile}' non esiste.")
    else:
        e_or_c = Prompt.ask("Choose between 'complain mode profiles'[0] or 'enforce mode profiles'[1]",
                            choices=["0", "1"])
        if e_or_c == "1":
            c.print("List all the active profiles in enforce mode...")
            enforce_profiles,leng= get_enforce_mode_profiles(contains)
            if len(enforce_profiles) == 0:
                c.print(ERROR_MESSAGE("There's no enforce mode profiles in the system"))
                return

            if len(enforce_profiles) == 1:
                confirm = Confirm.ask(f"Do you want to disable {enforce_profiles[0]}")
                if confirm:
                    c.print(f"[green]Disabilitiamo il profilo:[/green] {enforce_profiles[0]}")
                    aa_disable_with_apparmor(enforce_profiles[0])
                else:
                    return
            if len(enforce_profiles) > 1:
                # Visualizzazione elenco puntato
                c.print("[bold yellow]Elenco Puntato:[/bold yellow]")
                for item in enforce_profiles:
                    c.print(f"• {item}")

                # Prompt interattivo con autocompletamento dinamico
                profile_completer = DynamicProfileCompleter(enforce_profiles)
                response = None

                while response not in enforce_profiles:
                    response = prompt("Which profile do you want to disable? ", completer=profile_completer)

                    if response not in enforce_profiles:
                        c.print(f"[red]Errore:[/red] Il profilo '{response}' non è valido. Riprova.")

                c.print(f"[green]Disabilitiamo il profilo:[/green] {response}")
                aa_disable_with_apparmor(response)
        else:
            c.print("List all the complain profiles...")
            complain_profiles,leng = get_complain_mode_profiles(contains)
            if len(complain_profiles) == 0:
                c.print(ERROR_MESSAGE("There's no complain mode profiles in the system"))
                return

            if len(complain_profiles) == 1:
                confirm = Confirm.ask(f"Do you want to disable {complain_profiles[0]}")
                if confirm:
                    c.print(f"[green]Disabilitiamo il profilo:[/green] {complain_profiles[0]}")
                    aa_disable_with_apparmor(complain_profiles[0])
                else:
                    return
            if len(complain_profiles) > 1:
                # Visualizzazione elenco puntato
                c.print("[bold yellow]Elenco Puntato:[/bold yellow]")
                for item in complain_profiles:
                    c.print(f"• {item}")

                # Prompt interattivo con autocompletamento dinamico
                profile_completer = DynamicProfileCompleter(complain_profiles)
                response = None

                while response not in complain_profiles:
                    response = prompt("Which profile do you want to disable? ", completer=profile_completer)

                    if response not in complain_profiles:
                        c.print(f"[red]Errore:[/red] Il profilo '{response}' non è valido. Riprova.")

                c.print(f"[green]Disabilitiamo il profilo:[/green] {response}")
                aa_disable_with_apparmor(response)


@app.command(help="Enable an AppArmor profile by switching it to enforce mode. Profiles in enforce mode actively enforce restrictions.")
def aa_enable(
    profile: str = typer.Argument(
        None,
        help="Nome del profilo da disabilitare"
    ),
    contains: str = typer.Option(
        None,
        "--contains",
        "-c",
        help="Filtra i profili che contengono una determinata stringa"
    )
):
    if profile:
        if os.path.exists(profile):
            if os.path.isfile(profile):
                c.print(INFO_MESSAGE(f"Trying to enable {profile}"))
                aa_enforce_with_apparmor(profile)
            else:
                disabled_profiles = get_disabled_mode_profiles()
                complain_profiles = get_complain_mode_profiles()
                if profile in disabled_profiles or profile in complain_profiles:
                    c.print(f"[green]Abilitando il profilo:[/green] {profile}")
                    aa_enforce_with_apparmor(profile)
                else:
                    c.print(f"[red]Errore:[/red] Il profilo '{profile}' non esiste.")
    else:
        c_or_d = Prompt.ask("Choose between 'complain mode profiles'[0] or 'disabled mode profiles'[1]",choices=["0","1"])
        if c_or_d == 1:
            c.print("List all the disabled profiles...")
            disabled_profiles,leng = get_disabled_mode_profiles(contains)
            if len(disabled_profiles) == 0:
                c.print(ERROR_MESSAGE("There's no disable mode profiles in the system"))
                return

            if len(disabled_profiles) == 1:
                confirm = Confirm.ask(f"Do you want to enable {disabled_profiles[0]}")
                if confirm:
                    c.print(f"[green]Abilitiamo il profilo:[/green] {disabled_profiles[0]}")
                    aa_enforce_with_apparmor(disabled_profiles[0])
                else:
                    return
            if len(disabled_profiles) > 1:
                # Visualizzazione elenco puntato
                c.print("[bold yellow]Elenco Puntato:[/bold yellow]")
                for item in disabled_profiles:
                    c.print(f"• {item}")

                # Prompt interattivo con autocompletamento dinamico
                profile_completer = DynamicProfileCompleter(disabled_profiles)
                response = None

                while response not in disabled_profiles:
                    response = prompt("Which profile do you want to enable? ", completer=profile_completer)

                    if response not in disabled_profiles:
                        c.print(f"[red]Errore:[/red] Il profilo '{response}' non è valido. Riprova.")

            c.print(f"[green]Abilitiamo il profilo:[/green] {response}")
            aa_enforce_with_apparmor(response)
        else:
            c.print("List all the complain profiles...")
            complain_profiles,leng = get_complain_mode_profiles(contains)
            if len(complain_profiles) == 0:
                c.print(ERROR_MESSAGE("There's no complain mode profiles in the system"))
                return

            if len(complain_profiles) == 1:
                confirm = Confirm.ask(f"Do you want to enable {complain_profiles[0]}")
                if confirm:
                    c.print(f"[green]Abilitiamo il profilo:[/green] {complain_profiles[0]}")
                    aa_enforce_with_apparmor(complain_profiles[0])
                else:
                    return
            if len(complain_profiles) > 1:
                # Visualizzazione elenco puntato
                c.print("[bold yellow]Elenco Puntato:[/bold yellow]")
                for item in complain_profiles:
                    c.print(f"• {item}")

                # Prompt interattivo con autocompletamento dinamico
                profile_completer = DynamicProfileCompleter(complain_profiles)
                response = None

                while response not in complain_profiles:
                    response = prompt("Which profile do you want to enable? ", completer=profile_completer)

                    if response not in complain_profiles:
                        c.print(f"[red]Errore:[/red] Il profilo '{response}' non è valido. Riprova.")

                c.print(f"[green]Abilitiamo il profilo:[/green] {response}")
                aa_enforce_with_apparmor(response)
@app.command(help="Run the apparmor_parser utility to load, unload, or test AppArmor profiles. Use this to directly interact with AppArmor profiles for operations like syntax checking, profile loading, or unloading.")
def aa_parser():
    pass
@app.command(help="Tidy an AppArmor profile by fixing indentation and removing redundancies. Helps maintain clean and readable profiles.")
def aa_tidy(
    apparmor_profile:str,
    indent: bool = typer.Option(False, help="Formatta il codice aggiungendo rientri coerenti."),
    redund: bool = typer.Option(False, help="Rimuove elementi ridondanti dal codice."),

):
    executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(
        apparmor_profile)
    #check_synthax_with_apparmor_parser("second_prototype")
    if indent:
        fix_indent(executable_path,apparmor_profile)
    if redund:
        refactoring_redund(executable_path,apparmor_profile)

#Nota : generic_apparmor_profile può essere dove vuole, la struttura obbligatoriaamente in /etc/apparmor.d/ altrimenti non funzionano gli include
@app.command(help="Clean the structure of a generic AppArmor profile, including mappings and optionally subprofiles. Useful for resetting the structure.")
def clean_structure(
    generic_apparmor_profile : str,
    directory: str = typer.Option(
        None,
        "--directory",

        help="If created a directory x with a custom name manually you can specify it, if you want to clean-up the structure, with --directory x",
        show_default=False
    ),
    include_subprofiles: bool = typer.Option(
        False, "--include-subprofiles", help="Include subprofiles in the cleanup process."
    ),
    ignore_select: bool = typer.Option(
        True, "--ignore-select", help="By default #@+select tags will not be cleaned, if you specify this flag also the tags will be included in the clean-up process"
    )
):
    try:
        if not os.path.exists(generic_apparmor_profile):
            raise StructureException(f"{generic_apparmor_profile} doesn't exists.")

        executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(generic_apparmor_profile)
        structure_name = ""


        structure_name = directory if directory else executable_path.replace("/", ".")

        #Prima di andare a pulire la struttura ci accertiamo che esista
        if not os.path.exists(f"{APPARMOR_PATH}{structure_name}"):
            raise StructureException(f"Structure doesn't found for {generic_apparmor_profile}.\nHint: Use generate-structure {generic_apparmor_profile}.")

        if len(os.listdir(f"{APPARMOR_PATH}{structure_name}")) == 0:
            raise StructureException("Structure is empty.")

        #Nei pyxattr troviamo il path assoluto
        try:
            abs_path = os.path.abspath(os.path.realpath(generic_apparmor_profile))

            attribute_value = xattr.getxattr(f"{APPARMOR_PATH}{structure_name}", "user.structure_owner")
            attribute_value_str = attribute_value.decode('utf-8')  # Decodifica il valore in una stringa

            print(attribute_value_str)
            print(abs_path)

            if attribute_value_str.strip() != abs_path.strip():  # Confronta le stringhe direttamente
                raise StructureException("This structure is linked to another generic profile file.")
        except OSError:
            c.print(WARNING_MESSAGE(
                "This structure doesn't contain our metadata, maybe it is created by hand by the administrator"))

        if include_subprofiles:
            all_structure_subprofiles = get_all_subprofiles(structure_name)
            clean_all_confirm = Confirm.ask(f"Do you want to clean each subprofile")
            #TODO: Consider if is better to see the list of the subprofiles or not"
            if clean_all_confirm:
                c.print(INFO_MESSAGE("Cleaning all structure, subprofiles included."))
                clean_subprofiles(structure_name,all_structure_subprofiles,ignore_select)
                clean_mappings_file(structure_name)
            else:
                users_m = {index: value for index, value in enumerate(all_structure_subprofiles)}
                options = ", ".join([f"{k}: {v}" for k, v in users_m.items()])
                c.print(f"Available users : {options}")
                indexes_choice = Prompt.ask("Choice one or more index (delimiter , eg : 0,2)")
                try:
                    if not all(part.strip().isdigit() for part in indexes_choice.split(",")):
                        raise ValueError("Format error: you must use ',' as delimiter")
                    users_indexes_choice = [int(i.strip()) for i in indexes_choice.split(",") if i.strip().isdigit()]
                    selected_users = [users_m[i] for i in users_indexes_choice if i in users_m]
                    print(f"You chose: {selected_users}")
                    clean_subprofiles(structure_name, selected_users, ignore_select)
                    clean_mappings_file(structure_name)
                    c.print(SUCCESS_MESSAGE(f"Clean up {structure_name}/mappings and selected {selected_users} subprofiles done."))

                except:
                    c.print(ERROR_MESSAGE("Inserisci solo numeri separati da virgola"))
                    return
        else:
            c.print(INFO_MESSAGE("Cleaning only mappings."))
            clean_mappings_file(structure_name)
            c.print(SUCCESS_MESSAGE(f"Clean up {structure_name}/mappings"))
    except Exception as e:
        c.print(ERROR_MESSAGE(e))
@app.command(help="Create a custom subprofile for a user linked to a generic AppArmor profile. Optionally specify aliases to include.")
def custom_subprofile(generic_apparmor_profile, user, custom_subprofile_name, aliases: str = typer.Option(
        None,
        "--subprofiles",

        help="Specify one or more subprofiles to include in mappings, e.g., --subprofiles element1,element2,element3.",
        show_default=False
    ),directory: str = typer.Option(
        None,
        "--directory",

        help="If created a directory x with a custom name manually you can specify it, if you want to clean-up the structure, with --directory x",
        show_default=False
    ), ):

    if not __user_exists(user):
        raise ValueError(f"{user} Doesn't exists as user in the system.")
    #Dobbiamo prevedere directory
    executable_path,executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(generic_apparmor_profile)
    structure_name = directory if directory else executable_path.replace("/", ".")
    if not os.path.exists(f"{APPARMOR_PATH}{structure_name}"):
        raise StructureException(f"Structure doesn't found for {generic_apparmor_profile}.\nHint: Use generate-structure {generic_apparmor_profile}.")
    if os.path.exists(f"{APPARMOR_PATH}{structure_name}/{user}::{custom_subprofile_name}"):
        raise StructureException("This custom subprofile already exists")
    if aliases:
        aliases = aliases.split(",")
        aliases = [element.strip() for element in aliases]
        #print(aliases)
        base,selectable = refactoring_checkselectablesynthax_and_mapout_basepermissions_selectablerule(executable_path,executable_name,generic_apparmor_profile)
        for a in aliases:
            if a not in selectable:
                raise SelectException(f"{a} Doesn't exists as alias in {generic_apparmor_profile}")
        create_subprofiles_in_the_structure([f"{user}::{custom_subprofile_name}"],structure_name,aliases)
        return

    create_subprofiles_in_the_structure([f"{user}::{custom_subprofile_name}"],structure_name)

    #create_subprofiles_in_the_structure([f"{user}::{custom_subprofile_name}"],structure_name)
@app.command(help="Generate the structure for a generic AppArmor profile and its associated executable. This includes creating necessary files and directories.")
def generate_structure(
        generic_apparmor_profile:str,
        directory: str = typer.Option(
            None,
            "--directory",
            help="If you create your directory x containing the structure with a file for each user with the name of the user + mappings file, you can specify the directory with --directory x",
            show_default=False
        ),subprofiles: str = typer.Option(
            None,
            "--subprofiles",

        help="Specify one or more subprofiles, e.g., --subprofiles element1,element2,element3.",
        show_default=False
            ),
):

        print(APPARMOR_PATH)
        if not os.path.exists(generic_apparmor_profile):

            raise StructureException(f"{generic_apparmor_profile} doesn't exists.")

        executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(generic_apparmor_profile)
        structure_name = ""
        structure_name = directory if directory else executable_path.replace("/", ".")

        abs_path = os.path.abspath(os.path.realpath(generic_apparmor_profile))
        try:

            abs_path = os.path.abspath(os.path.realpath(generic_apparmor_profile))

            attribute_value = xattr.getxattr(f"{APPARMOR_PATH}{structure_name}", "user.structure_owner")
            attribute_value_str = attribute_value.decode('utf-8')  # Decodifica il valore in una stringa

            if attribute_value_str != abs_path:
                raise StructureException("This structure already exists and it is linked to another generic profile file.")
        except OSError:
            c.print(INFO_MESSAGE(
                "This structure doesn't contain our metadata, the structure doesn't exists."))

        manipulate_directive_include_structure_directory_mappings(generic_apparmor_profile,executable_path,structure_name)
        check_syntax_with_apparmor_parser(generic_apparmor_profile)

        structure_path = f"{APPARMOR_PATH}{structure_name}"
        users_l = users_list()
        os.makedirs(structure_path,exist_ok=True)
        xattr.setxattr(structure_path, 'user.structure_owner', abs_path.encode('utf-8'))


        mappings_filename = "mappings"
        mappings_path = os.path.join(structure_path,mappings_filename)
        if not os.path.exists(mappings_path):
            with open(mappings_path,'w') as mappings_write:
                mappings_write.write("")
        else:
            c.print(INFO_MESSAGE(f"{mappings_path} Already exists."))

        if subprofiles:
            subprofiles_list = subprofiles.split(',')
            subprofiles_list = [element.strip() for element in subprofiles_list]
            _subprofiles = subprofiles_list
            create_subprofiles_in_the_structure(_subprofiles, structure_name)
            c.print(SUCCESS_MESSAGE(f"Structure created."))
            return
        users_without_subprofile = users_without_files(users_l,f"{APPARMOR_PATH}{structure_name}")
        if len(users_without_subprofile) == 0:
            c.print(SUCCESS_MESSAGE(f"Every user in the system has a profile for {generic_apparmor_profile}"))
            return
        elif len(users_without_subprofile) == 1:
            confirm_single_subprofile = Confirm.ask(
                f"Do you want to create the profile for {users_without_subprofile[0]}?")
            if confirm_single_subprofile:
                create_subprofiles_in_the_structure(users_without_subprofile,structure_name)
                #subprofile_path = os.path.join(structure_path,users_without_subprofile[0])
                #if not os.path.exists(subprofile_path): #Ma già sappiamo che non esiste
                #    with open(subprofile_path,'w') as subprofile_writer:
                #        subprofile_writer.write("profile " + users_without_subprofile[0] + " {\n}")
                c.print(SUCCESS_MESSAGE(f"{structure_name}/{users_without_subprofile[0]} created."))
        elif len(users_without_subprofile) > 1:
            c.print(INFO_MESSAGE(f"There are {len(users_without_subprofile)} users without a profile, and they're:\n{users_without_subprofile}."))
            confirm_all_subprofiles = Confirm.ask("Do you want to create subprofile for each of them?")
            if confirm_all_subprofiles:
                create_subprofiles_in_the_structure(users_without_subprofile,structure_name)
                #for user in users_without_subprofile:
                #    subprofile_path = os.path.join(structure_path,user)
                #    if not os.path.exists(subprofile_path):
                #        with open(subprofile_path, 'w') as subprofile_writer:
                #            subprofile_writer.write("profile " + users_without_subprofile[0] + " {\n}")
                c.print(SUCCESS_MESSAGE(f"Structure created."))
            else:
                users_m = {index: value for index, value in enumerate(users_without_subprofile)}
                options = ", ".join([f"{k}: {v}" for k, v in users_m.items()])
                c.print(f"Available users : {options}")

                while True:
                    indexes_choice = Prompt.ask("Choice one or more index (delimiter , eg : 0,2)")
                    try:
                        if not all(part.strip().isdigit() for part in indexes_choice.split(",")):
                            raise ValueError("Formato errore")
                        users_indexes_choice = [int(i.strip()) for i in indexes_choice.split(",") if
                                                i.strip().isdigit()]
                        selected_users = [users_m[i] for i in users_indexes_choice if i in users_m]

                        # Conferma selezione
                        c.print(f"Hai scelto i valori: {selected_users}")
                        create_subprofiles_in_the_structure(selected_users,structure_name)
                        #for user in selected_users:
                        #   full_subprofile_path = os.path.join(structure_path, user)
                        #    if not os.path.exists(full_subprofile_path):
                        #        with open(full_subprofile_path, 'w') as f:
                        #            f.write("profile " + user + " {\n\n}")
                        c.print(SUCCESS_MESSAGE(f"Structure created successfully"))
                            #else:
                                #c.print(WARNING_MESSAGE(f"{full_subprofile_path} already exists"))

                        # Esci dal ciclo solo se tutto è valido
                        break
                    except ValueError:
                        c.print(ERROR_MESSAGE("Inserisci solo numeri separati da virgola"))
                        c.print(f"[red]Riprova di nuovo.[/red]")
        c.print(SUCCESS_MESSAGE("Structure generated successfully"))


@app.command(help="Generate and optionally sign a mappings file for a structure linked to a generic AppArmor profile. Required for profile functionality.")
def generate_mappings(
    generic_apparmor_profile:str,
    subprofiles: str = typer.Option(
        None,
        "--subprofiles",

        help="Specify one or more subprofiles to include in mappings, e.g., --subprofiles element1,element2,element3.",
        show_default=False
    ),
    directory: str = typer.Option(
        None,
        "--directory",

        help="If you create your directory x containing the structure with a file for each user with the name of the user + mappings file, you can specify the directory with --directory x",
        show_default=False
    )
):
    try:
        if not os.path.exists(generic_apparmor_profile):
            raise StructureException(f"{generic_apparmor_profile} doesn't exists.")


        executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(
            generic_apparmor_profile)
        structure_name = ""
        structure_name = directory if directory else executable_path.replace("/", ".")

        if not os.path.exists(f"{APPARMOR_PATH}{structure_name}"):
            raise StructureException("Structure doesn't exists.")
        if len(os.listdir(f'{APPARMOR_PATH}{structure_name}')) == 0:
            raise StructureException(f"Structure is empty.\nHint: generate-structure {generic_apparmor_profile}")
        if len(os.listdir(f'apparmor.d/{directory}')) == 1 and os.listdir(f'apparmor.d/{directory}')[0] == 'mappings':
            raise StructureException(f"Only mappings file in structure; you need at least one subprofile.\nHint: generate-structure {generic_apparmor_profile}")
        #if len(os.listdir(f'apparmor.d/{directory}')) == 1 and os.listdir(f'apparmor.d/{directory}')[0] != 'mappings':
        #    raise StructureException(f"You need also mappings file.\nHint: generate-structure {generic_apparmor_profile}")
        try:
            abs_path = os.path.abspath(os.path.realpath(generic_apparmor_profile))
            attribute_value = xattr.getxattr(f"{APPARMOR_PATH}{structure_name}", "user.structure_owner")
            print(attribute_value.decode('utf-8'))
            if attribute_value.decode('utf-8') != abs_path:
                raise StructureException("This structure is linked to another generic profile file.")
        except OSError:
            c.print(WARNING_MESSAGE(
                "This structure doesn't contain our metadata, maybe it is created by hand by the administrator"))

        subprofiles_list = get_all_subprofiles(structure_name)
        if subprofiles:
            subprofiles_list = subprofiles.split(",")
            subprofiles_list = [element.strip() for element in subprofiles_list]


        if not is_empty_mappings_file(structure_name):
            rewrite_confirm = Confirm.ask("mappings is not an empty file. Do you want to overwrite the content?")
            if rewrite_confirm:
                if subprofiles:
                    profiles_to_upload_in_kernel = generate_mappings_file(structure_name,executable_path,subprofiles_list)
                    #TODO: If process allora abilitiamo i profili, vediamo se sign è necessario
                else:
                    profiles_to_upload_in_kernel = generate_mappings_file(structure_name, executable_path)
            return
    except Exception as e:
        pass



def fix_indent(executable_path:str, apparmor_profile:str, indent:int=4):
    with open(apparmor_profile, 'r') as file:
        lines = file.readlines()
    #L'ultima parentesi si trova qua
    #print(lines[len(lines)-1].strip())
    formatted_lines = {}
    first_block_start_index = -1
    for i,line in enumerate(lines):
        s_line = line.strip()
        formatted_lines[i] = s_line
        if executable_path in s_line and not s_line.startswith("#") and s_line.endswith(" {"):
            first_block_start_index = i
            break

    for i in range(first_block_start_index+1,len(lines)-1):
        #print(lines[i].strip())
        s_line = lines[i].strip()
        if (s_line.startswith("profile") or s_line.startswith("^")) and s_line.endswith(" {"):
            #print(f"Inizio profilo a indice {i}")
            #print(s_line)
            print(s_line)
            formatted_lines[i] = f'{" "*indent}{s_line}'
            for j in range(i+1,len(lines)-1):
                s_line_j = lines[j].strip()

                if s_line_j.endswith(",}") or s_line_j == "}":
                    print(f"Fine blocco indice {j}")
                    formatted_lines[j] = f'{" "*indent}{s_line_j}'

                    break
                if s_line_j != "\n":
                    formatted_lines[j] = f'{" "*indent*2}{s_line_j}'
                #print(lines[j].strip())
        else:
            if i not in formatted_lines:
                formatted_lines[i] = f'{" " * indent}{s_line}'

    formatted_lines[len(lines)-1] = "}"
    #print(formatted_lines)

    #for chiave, valore in formatted_lines.items():
    #    print(f"{chiave}: {valore}")
    with open(apparmor_profile, 'w') as wr:
        wr.write('\n'.join(list(formatted_lines.values())))
    #print('\n'.join(list(formatted_lines.values())))
def sanify_rule(rule,selectable_box=False):
    rule = rule.strip()
    if rule.endswith(","):
        rule = rule[:-1]
    if rule.startswith(",") or (rule.startswith("#") and selectable_box):
        rule = rule[1:]
    return rule

#TODO: Da sistemare find_redund, forse si potrebbe usare ASP?
def refactoring_redund(executable_path,apparmor_profile):
    with open(apparmor_profile, 'r') as file:
        lines = file.readlines()
    first_block_start_index = -1
    header_rules = []
    for i, line in enumerate(lines):
        s_line = line.strip()
        if not s_line.startswith("#") and not s_line.endswith(" {"):
            if s_line in header_rules and s_line != "\n" and s_line != "" and not s_line.startswith("#"):
                print(s_line)
                print(header_rules)
                raise RedundException("Redund in header")
            if s_line != "\n" and s_line != "" and not s_line.startswith("#"):
                for rule in header_rules:
                    if not rule.startswith("#"):
                        if sanify_rule(s_line) in rule or sanify_rule(rule) in s_line:
                            raise RedundException("Redund in header")
            if s_line != "\n" and s_line != "":
                header_rules.append(s_line)
        if executable_path in s_line and not s_line.startswith("#") and s_line.endswith(" {"):
            first_block_start_index = i
            break
    main_block_rules = {}

    includes = []
    rules_inside_selectable_boxes = []
    rules_selectable_box = []
    boxes = {}
    profiles = {}
    bases = []
    index_boxes = 1
    index_profiles = 1
    selectables = {}
    #TODO: I profili innestati
    for i in range(first_block_start_index + 1, len(lines) - 1):
        s_line = lines[i].strip()
        if "#@+ignore" in s_line or "#@+ ignore" in s_line:
            main_block_rules[i] = s_line
            continue
        elif s_line == "" or s_line==" " or s_line=="\n":
            main_block_rules[i] = s_line
            continue
        #GLI INCLUDE VENGONO TRATTATI A PARTE
        elif is_valid_include_pattern(s_line):
            for include in extract_include_statements(s_line):
                includes.append(sanify_rule(include,True))
        elif check_selectable_row(s_line): #Selectable
            current_selectable_rules = []
            info_selectable = check_selectable_row(s_line)
            if info_selectable['rule'].count(",") > 1:
                testa = info_selectable['rule'].replace(",","\n").strip()
                testa = testa.split("\n")
                for t in testa:
                    rules_selectable_box.append(t)
                    current_selectable_rules.append(t)
            else:
                rules_selectable_box.append(sanify_rule(info_selectable['rule']))
                current_selectable_rules.append(sanify_rule(info_selectable['rule']))
            selectables[info_selectable['alias']] = current_selectable_rules

        elif check_selectable_row(s_line,False):
            index_inside_box = i+1
            current_selectable_box_rules = []
            for j in range(index_inside_box,len(lines)-1):
                s_line_j = lines[j].strip()
                if s_line_j.startswith("#@end") or s_line_j.startswith("#@ end"):
                    break
                if s_line_j.count(",")>1:
                    san_sline_j = sanify_rule(s_line_j,True)
                    testa = san_sline_j.replace(",", "\n").strip()
                    testa = testa.split("\n")
                    for t in testa:
                        rules_inside_selectable_boxes.append(t.strip())
                        current_selectable_box_rules.append(t.strip())
                else:
                    rules_inside_selectable_boxes.append(sanify_rule(s_line_j,True))
                    current_selectable_box_rules.append(sanify_rule(s_line_j,True))
            boxes[index_boxes] = current_selectable_box_rules
            index_boxes+=1
        elif (s_line.startswith("profile") or s_line.startswith("^")) and s_line.endswith(" {"):
            #print(f"NOME PROFILO {s_line.split(" ")[1]}")
            current_profile_rules = []
            key = s_line.split(" ")[1]
            index_inside_profile = i+1
            for k in range(index_inside_profile,len(lines)-1):
                s_line_k = lines[k].strip()
                if s_line_k.endswith(",}") or s_line_k == "}":
                    break
                if is_valid_include_pattern(s_line_k):
                    print(s_line_k)
                    for include in extract_include_statements(s_line_k):
                        current_profile_rules.append(sanify_rule(include, True))
                if not s_line_k.startswith("#"):
                    if s_line_k.count(",") > 1:
                        testa = s_line_k.replace(",", "\n").strip()
                        testa = testa.split("\n")
                        for t in testa:
                            print(t.strip())
                            current_profile_rules.append(t.strip())
                            #bases.append(t)
                    else:
                        print(sanify_rule(s_line_k))
                        current_profile_rules.append(sanify_rule(s_line_k))
                profiles[key] = current_profile_rules
                index_profiles
                        #bases.append(sanify_rule(s_line))
        else:
            if not s_line.startswith("#"):
                if s_line.count(",") > 1:
                    testa = s_line.replace(",", "\n").strip()
                    testa = testa.split("\n")
                    for t in testa:
                        bases.append(t.strip())
                else:
                    bases.append(sanify_rule(s_line))
        main_block_rules[i] = s_line

    #Ora possiamo partire con i check
    #CHECK INCLUDES:
    copy = list(set(includes))
    '''if len(includes) != len(copy):
        raise RedundException("Includes redund exception")'''
    copy_bases = list(set(bases))
    '''if len(copy_bases) != len(bases):
        raise RedundException("Base rules redund exception")'''
    #Dato che stiamo scorrendo può essere l'occasione per lanciare warning in caso ci siano regole base all'interno dei selectable box, perché le regole base vengono ereditate e basta, e potrebe esserci un redund
    #already_check = False
    '''for key, value in boxes.items():
        copy = list(set(value))
        if len(copy) != len(value):
            raise RedundException(f"Rules selectable boxes redund exception, at box {key}")
        for b in bases:
            if b in copy:
                raise RedundException(f"WARNING at box {key}")'''
    '''nested_boxes = list(boxes.values())
    flat_list_boxes = [item.strip() for sublist in nested_boxes for item in sublist]
    copy_flat_list_boxes = list(set(flat_list_boxes))
    if len(copy_flat_list_boxes) != len(flat_list_boxes):
        raise RedundException("WARNING")
    print(flat_list_boxes)

    print(selectables)'''

    '''for key, value in selectables.items():
        copy = list(set(value))
        if len(copy) != len(value):
            raise RedundException(f"Rules selectable redund exception, at selectable with alias {key}")
        for b in bases:
            if b in copy:
                raise RedundException(f"WARNING at selectable with alias {key}")'''
    '''nested_selectable = list(selectables.values())
    flat_list_selectable = [item.strip() for sublist in nested_selectable for item in sublist]
    copy_flat_list_selectable = list(set(flat_list_selectable))
    if len(copy_flat_list_selectable) != len(flat_list_selectable):
        raise RedundException("WARNING")
    print(flat_list_selectable)'''
    print(profiles)
    for key, value in profiles.items():
        copy = list(set(value))
        if len(copy) != len(value):
            raise RedundException(f"Rules profile redund exception, at profile with name {key}")


        #print(list(set(value)))
        #print(f"Chiave: {key}, Valore: {value}")


    #Check includes, include <a/b> è equivalete a include <a/b> e #include <a/b>, #include <a/b> è equivalente a #include <a/b> e include <a/b>










def find_redund(executable_path, apparmor_profile):
    with open(apparmor_profile, 'r') as file:
        lines = file.readlines()
    first_block_start_index = -1
    header_rules = []
    for i, line in enumerate(lines):
        s_line = line.strip()
        if not s_line.startswith("#") and not s_line.endswith(" {"):
            if s_line in header_rules and s_line!="\n" and s_line!="" and not s_line.startswith("#"):
                print(s_line)
                print(header_rules)
                raise RedundException("Redund in header")
            if s_line != "\n" and s_line != "" and not s_line.startswith("#"):
                for rule in header_rules:
                    if not rule.startswith("#"):
                        if s_line in rule or rule in s_line:
                            raise RedundException("Redund in header")
            if s_line != "\n" and s_line != "":
                header_rules.append(s_line)
        if executable_path in s_line and not s_line.startswith("#") and s_line.endswith(" {"):
            first_block_start_index = i
            break

    main_block_rules = {}
    for i in range(first_block_start_index+1,len(lines)-1):
        s_line = lines[i].strip()
        if (s_line.startswith("profile") or s_line.startswith("^")) and s_line.endswith(" {"):
            subprofile_block_rules = {}
            for j in range(i+1,len(lines)-1):
                print("Sono qua")
                main_block_rules[j] = []
                s_line_j = lines[j].strip()
                if s_line_j.endswith(",}") or s_line_j == "}":
                    print(f"Fine blocco indice {j}")
                    #formatted_lines[j] = f'{" "*indent}{s_line_j}'
                    break
                if s_line_j != "\n" and s_line_j!="" and not s_line_j.startswith("#") and not "selectable" in s_line_j:
                    if s_line_j in list(subprofile_block_rules.values()):
                        raise RedundException(f"Redund in sub profile at index {j}")
                    for rules in list(subprofile_block_rules.values()):
                        if s_line_j != "" and s_line_j != " " and s_line_j!= "\n":
                            if not rules.startswith("#") and rules != "" and rules != " " and rules != "\n":
                                if s_line_j in rules or rules in s_line_j:
                                    raise RedundException(f"Redund in sub profile at index {j}")


                    subprofile_block_rules[j] = s_line_j

        else:
            subprofile_block_rules = {}
            if i not in main_block_rules:

                if s_line.startswith("#include") or s_line.startswith("# include"):
                    if s_line in list(main_block_rules.values()):
                        print(s_line)
                        raise RedundException(f"Redund in main block at index {i}")
                    # Check: potrebbe essere contenuto, e non è un commento
                    for rules in list(main_block_rules.values()):
                        if s_line != "" and s_line != " " and s_line != "\n":
                            if not rules.startswith("#") and rules != "" and rules != " " and rules != "\n":
                                if s_line in rules or rules in s_line:
                                    raise RedundException(f"Redund in main block at index {i}2")
                    continue
                if s_line != "\n" and s_line!="" and not s_line.startswith("#") and not "selectable" in s_line and not "ignore" in s_line:
                    # Check: esattamente la stessa riga
                    print(list(main_block_rules.values()))
                    if s_line in list(main_block_rules.values()):
                        print(s_line)
                        raise RedundException(f"Redund in main block at index {i}")
                    # Check: potrebbe essere contenuto, e non è un commento
                    for rules in list(main_block_rules.values()):
                        if s_line != "" and s_line != " " and s_line != "\n":
                            if not rules.startswith("#") and rules != "" and rules != " " and rules != "\n":
                                if s_line in rules or rules in s_line:
                                    raise RedundException(f"Redund in main block at index {i}2")

                main_block_rules[i] = s_line





@app.command(help="Refresh the database with updated kernel content and profile information. Useful for synchronizing profiles with the database.")
def refresh_database():
    md5_content = get_kernel_content_for_db_content()
    print(md5_content)
    db_connection = DatabaseConnection()
    info_DAO = InfoDAO(db_connection.get_cursor())
    k_DAO = KContentDAO(db_connection.get_cursor())
    u_list = users_list()
    kcontent = k_DAO.read_last_record()
    print(kcontent)
    if kcontent is not None:
        #Controlliamo che siano diversi
        if kcontent.content != md5_content:
            c.print(WARNING_MESSAGE("There are some changes in the database"))
            k_DAO.delete_all()
            info_DAO.delete_all()
            filtered_profiles_info, last_row = get_infos_to_add_in_database(u_list)
            if len(filtered_profiles_info) == 0:
                c.print(ERROR_MESSAGE("There aren't information to store"))
                return
            for filt in filtered_profiles_info:
                info_DAO.create(filt)
            k_DAO.create(md5_content, last_row)
            print(k_DAO.read_all())
            print(info_DAO.read_all())
            c.print(SUCCESS_MESSAGE("Database updated."))
        else:
            c.print(INFO_MESSAGE("Database is already OK"))
    else:
        k_DAO.delete_all()
        info_DAO.delete_all()
        filtered_profiles_info, last_row = get_infos_to_add_in_database(u_list)
        for filt in filtered_profiles_info:
            info_DAO.create(filt)
        if len(filtered_profiles_info) == 0:
            c.print(ERROR_MESSAGE("There aren't information to store"))
            return
        k_DAO.create(md5_content,last_row)
        print(k_DAO.read_all())
        print(info_DAO.read_all())
        c.print(SUCCESS_MESSAGE("Database initialized."))


#TODO: Da rivedere
@app.command(help="Process a generic AppArmor profile, including managing subprofiles and generating mappings. Optional unrestrict mode for flexible alias handling.")
def process(generic_apparmor_profile,
            unrestrict_mode: bool = typer.Option(
                True, "--unrestrict-mode",
                help="By default if you try to select an alias that doesn't for you and it doesn't exists the process execution will fail. If you specify this flag you will receive only WARNING and the unexpected aliases will be ignored."
            ),subprofiles: str = typer.Option(
            None,
            "--subprofiles",

        help="Specify one or more subprofiles, e.g., --subprofiles element1,element2,element3.",
        show_default=False
            ),
            directory: str = typer.Option(
                None,
                "--directory",

                help="If you create your directory x containing the structure with a file for each user with the name of the user + mappings file, you can specify the directory with --directory x",
                show_default=False
            ),no_mappings: str = typer.Option(
        None,
        "--no-mappings",
        show_default=False
    ),
            ):
    if not os.path.exists(generic_apparmor_profile):
        raise StructureException(f"{generic_apparmor_profile} doesn't exists.")

    check_syntax_with_apparmor_parser(generic_apparmor_profile)
    executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(
        generic_apparmor_profile)

    structure_name = ""
    structure_name = directory if directory else executable_path.replace("/", ".")


    if not os.path.exists(f"{APPARMOR_PATH}{structure_name}"):
        raise StructureException("Structure doesn't exists.")
    if len(os.listdir(f'{APPARMOR_PATH}{structure_name}')) == 0:
        raise StructureException(f"Structure is empty.\nHint: generate-structure {generic_apparmor_profile}")
    if len(os.listdir(f'{APPARMOR_PATH}{structure_name}')) == 1 and os.listdir(f'{APPARMOR_PATH}{structure_name}')[0] == 'mappings':
        raise StructureException(
            f"Only mappings file in structure; you need at least one subprofile.\nHint: generate-structure {generic_apparmor_profile}")
    if len(os.listdir(f'{APPARMOR_PATH}{structure_name}')) == 1 and os.listdir(f'{APPARMOR_PATH}{structure_name}')[0] != 'mappings':
        raise StructureException(f"You need also mappings file.\nHint: generate-mappings {generic_apparmor_profile}")

    try:
        abs_path = os.path.abspath(os.path.realpath(generic_apparmor_profile))

        attribute_value = xattr.getxattr(f"{APPARMOR_PATH}{structure_name}", "user.structure_owner")
        if attribute_value.decode('utf-8') != abs_path:
            raise StructureException("This structure is linked to another generic profile file.")
    except OSError:
        c.print(WARNING_MESSAGE(
            "This structure doesn't contain our metadata, maybe it is created by hand by the administrator"))

    base_permissions,selectable_map = refactoring_checkselectablesynthax_and_mapout_basepermissions_selectablerule(executable_path, executable_name, generic_apparmor_profile)

    delete_all_backup_for_each_subprofile(structure_name)
    _subprofiles = get_all_subprofiles(structure_name)


    if subprofiles:
        subprofiles_list = subprofiles.split(',')
        subprofiles_list = [element.strip() for element in subprofiles_list]
        _subprofiles = subprofiles_list

    create_backup_for_each_subprofile_in_order_to_work_on_copy_and_not_on_original(structure_name,_subprofiles)

    print(_subprofiles)

    #PROCESS_SUBPROFILES

    try:
        profiles_with_warnings = PROCESS_SUBPROFILES(selectable_map,base_permissions,structure_name,unrestrict_mode,_subprofiles)
    except:
        print("Errore")
        delete_all_backup_for_each_subprofile(structure_name)
        return

    print("Sono qua")
    #profiles_with_warnings = PROCESS_SUBPROFILES(selectable_map,base_permissions,structure_name,_subprofiles)
    copy_from_backup_file_to_original_after_process(structure_name, _subprofiles)
    delete_all_backup_for_each_subprofile(structure_name)

    if len(profiles_with_warnings) > 0:
        c.print(WARNING_MESSAGE(f"You have warnings on these subprofiles {' '.join(profiles_with_warnings)}"))


    c.print(SUCCESS_MESSAGE("Selectable process done."))
    if no_mappings:
        c.print(WARNING_MESSAGE(f"You choose to don't generate the 'mappings' file.\nHint: Use generate-mappings {generic_apparmor_profile}."))
    else:
        profiles_to_upload_in_kernel = generate_mappings_file(structure_name,executable_path)
        #sign_mappings(structure_name)
        uncomment_directive_include_structure_directory_mappings(generic_apparmor_profile,structure_name)
        apparmor_parser_active_profile(generic_apparmor_profile)
        c.print(SUCCESS_MESSAGE(f"\n{'\n'.join(profiles_to_upload_in_kernel)}\nAre activated"))









    '''executable_path, executable_name = extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(generic_apparmor_profile)
    print(executable_path,executable_name)
    ref_base_permissions,ref_selectable_map = refactoring_checkselectablesynthax_and_mapout_basepermissions_selectablerule(executable_path, executable_name, generic_apparmor_profile)
    base_permissions,selectable_map = check_selectablesynthax_and_get_basepermissions_and_mapout_selectablerule(executable_name,generic_apparmor_profile)

    print(ref_base_permissions)


    for key,value in selectable_map.items():
        print(f"{key}->{value}")
    print("*"*10)
    for key,value in ref_selectable_map.items():
        print(f"{key}->{value}")
    refactoring_check_selectsyntax_and_get_selected_aliases_by_specific_subprofile("","ex_subprofile")
    aliases = check_select_synthax_and_get_aliases_selected_by_specific_subprofile("","ex_subprofile")
    print(aliases)
    #print(aliases)
    '''



@app.command(help="Automate the generation of an AppArmor profile using aa-genprof. Includes optional resource limitations like memory, CPU, and file descriptors.")
def secure_genprof(
    script_name: str,
    mem: int = typer.Option(None, help="Specifica la quantità di memoria (MB)."),
    cpu: int = typer.Option(None, help="Specifica il numero massimo di CPU."),
    fd: int = typer.Option(None, help="Specifica il numero massimo di file descriptor.")
):
    """
    Automatizza il processo di creazione del profilo AppArmor con aa-genprof
    per un eseguibile specifico.

    :param script_name: Nome dell'eseguibile per cui creare il profilo.
    :param mem: (opzionale) Limite di memoria in MB.
    :param cpu: (opzionale) Numero massimo di CPU.
    :param fd: (opzionale) Numero massimo di file descriptor.
    """
    absolute_path = os.path.abspath(script_name)
    print(absolute_path.replace("/",".")[1:])
    possible_apparmor_profile_path = os.path.join(APPARMOR_PATH,absolute_path.replace("/",".")[1:])
    print(possible_apparmor_profile_path)
    if os.path.exists(possible_apparmor_profile_path):
        print("Profile already exists. This can cumminar a conflict")
        #return
    # Costruisci la lista dei flag opzionali
    optional_flags = []
    if mem is not None:
        optional_flags.append(f"ulimit -v {mem}")
    if cpu is not None:
        optional_flags.append(f"ulimit -t {cpu}")
    if fd is not None:
        optional_flags.append(f"ulimit -n {fd}")

    print("Avvio di aa-genprof in un terminale interattivo...")
    #result = subprocess.run(['gnome-terminal', '--', 'aa-genprof', script_name], capture_output=True, text=True)
    print("Comando eseguito con successo")
    #print("STDOUT:", result.stdout)
    #print("STDERR:", result.stderr)


    # Informazioni per l'utente
    print("aa-genprof è stato avviato in un nuovo terminale. Ora eseguirò automaticamente i comandi necessari.")
    print("Puoi tornare a interagire manualmente con aa-genprof una volta completate le esecuzioni.")
    time.sleep(10)
    # Definisci le esecuzioni con vari flag o combinazioni
    executions = [
        f"{script_name}",
        f"{script_name}",
        f"{script_name}"
    ]
    for execution in executions:
        new = ""
        for limit in optional_flags:
            new += f"&& {limit} "
        new+=execution
        print(new)

    # Esegui i comandi specificati
    for execution in executions:
        print(f"Esecuzione: {execution}")
        try:
            subprocess.run(execution, shell=True, check=True)
            print(f"Esecuzione completata: {execution}")
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'esecuzione di: {execution}")
            print(e)

    # Informa l'utente che può tornare su aa-genprof
    print("\nTutte le esecuzioni sono state completate.")
    print("Ora puoi tornare al terminale di aa-genprof per completare la configurazione manuale.")


if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        c.print(ERROR_MESSAGE(f"{e}"))




