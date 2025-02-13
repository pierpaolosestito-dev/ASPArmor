import os
import re
from datetime import datetime
from select import select

from alerts import WARNING_MESSAGE
from exceptions import SelectableSynthaxException, SelectableException, StructureException, CompatibilityException
from process_rules_data_structure import __process_selected_map_to_str, __process_base_perms_to_str, \
    __mix_selected_rules, __get_uncommon
from regexs import check_select_row
from users_manager import __user_exists,__is_user_in_group
from config import APPARMOR_PATH
#APPARMOR_PATH = "/etc/apparmor.d/" #TODO: pydotenv
def create_subprofiles_in_the_structure(users_list, structure_name,aliases = []):
    for user in users_list:
        user_file = os.path.join(f"{APPARMOR_PATH}{structure_name}", user)
        if not os.path.exists(user_file):
            with open(user_file,'w') as file:
                if len(aliases) != 0:
                    file.write("profile " + user + " {\n\n}")
                else:
                    select_tag = "#@+select: "
                    for a in aliases:
                        select_tag += f"{a}," #stringa[:-1]
                    file.write("profile " + user + " {\n"+select_tag[:-1]+"\n}")

def __clean_specific_subprofile(structure_name, subprofile, ignore_select=True):
    try:
        content = ""
        path = f"{APPARMOR_PATH}{structure_name}/{subprofile}"

        with open(path, 'r') as file:
            content_lines = file.readlines()
        content = ''.join(content_lines)
        cleaned_content=""
        if ignore_select:
            saved_content_lines = []
            for row in content_lines:
                if "#@+" in row: #TODO: Da cambiare con funzione check_select_row
                    saved_content_lines.append(row)

            cleaned_content = re.sub(r'\{.*?\}', '{'+'\n'+''.join(saved_content_lines)+'\n\n}', content, flags=re.DOTALL)
        else:
            cleaned_content = re.sub(r'\{.*?\}', '{\n\n}', content, flags=re.DOTALL)
        with open(path, 'w') as file:
            file.write(cleaned_content)
    except FileNotFoundError as fe:
        print(f"{fe}")

def clean_subprofiles(structure_name, subprofiles_choiced, ignore_select=True):
    try:
        path = f"{APPARMOR_PATH}{structure_name}/"
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if file_name == "mappings" or not os.path.isfile(file_path):
                continue

            if file_name in subprofiles_choiced:
                __clean_specific_subprofile(structure_name, file_name, ignore_select)

    except FileNotFoundError as fe:
        print(f"{fe}")

def get_all_subprofiles(structure_name):
    try:
        path = f"{APPARMOR_PATH}{structure_name}/"
        subprofiles = []
        for file_name in os.listdir(path):
            file_path = os.path.join(path,file_name)
            if file_name == "mappings" or not os.path.isfile(file_path):
                continue
            subprofiles.append(file_name)
        return subprofiles
    except FileNotFoundError as fe:
        print(f"{fe}")

def refactoring_check_selectsyntax_and_get_selected_aliases_by_specific_subprofile(structure_name,subprofile):
    full_subprofile_path = f"{APPARMOR_PATH}{structure_name}/{subprofile}"
    select_list = []
    with open(full_subprofile_path,'r') as file:
        lines = file.readlines()
    start_select_counter = 0 #You cannot have more than one select tag in subprofile
    for i in range(len(lines)):
        s_line = lines[i].strip()

        if start_select_counter > 1:
            raise SelectableSynthaxException(f"Line {i}: You cannot have more than one #@+select tag.")
        if s_line.startswith("#"):
            select_list = check_select_row(s_line)

            if select_list is not None:
                start_select_counter += 1
    return select_list
def check_select_synthax_and_get_aliases_selected_by_specific_subprofile(structure_name, subprofile):
    try:
        full_path_subprofile = f"{APPARMOR_PATH}{structure_name}/{subprofile}"
        #check_synthax_with_apparmor_parser(full_path_subprofile)
        select_list = []

        with open(full_path_subprofile,'r') as file:
            start_select_str_counter = 0
            for index,row in enumerate(file):
                if start_select_str_counter>1:
                    #f"Line {index}: Synthax error in selectable line." Line{index}: You cannot have more than one #@+select tag.
                    raise SelectableSynthaxException(f"Line{index}: You cannot have more than one #@+select tag.")
                if row.strip().startswith("#@+"):
                    select_list = check_select_row(row.strip())
                    if select_list != None:
                        start_select_str_counter+=1
                    else:
                        raise SelectableException(f"Line{index}: Select synthax error")

        return select_list

    except FileNotFoundError:
        print(f"{structure_name}/{subprofile} not found.")


#Probabilmente da spostare in un altro file per rimanere concettualmente divisi
def check_compatibility_subprofile(selectable_map,selected_aliases,subprofile,restrict_mode):
    alias_that_exists_for_sure = []
    skipped_aliases = {}
    print(subprofile)
    #print(selectable_map)
    subprofile = subprofile.split("::")[0] if "::" in subprofile else subprofile
    #subprofile = subprofile.replace(".bak","")
    print(subprofile)
    print(selected_aliases)
    for selected in selected_aliases:
        if selected not in selectable_map:
            if restrict_mode:
                raise CompatibilityException(f"{subprofile} is trying to select {selected} as alias but it doesn't exists")
            else:
                skipped_aliases.setdefault(selected,{'info':f"{subprofile} is trying to select {selected} as alias but it doesn't exists"})
        else:
            alias_that_exists_for_sure.append(selected)
    #Dobbiamo creare una mappa che contiene solo gli alias in sure_selected e che rispettano queste condizioni:
    #O siamo specificati nella lista users o apparteniamo a qualche gruppo specificato in groups
    selected_map = {}
    for sure_selected in alias_that_exists_for_sure:
        if selectable_map[sure_selected]['groups'] is None and selectable_map[sure_selected]['users'] is None:

            selected_map.setdefault(sure_selected,selectable_map[sure_selected])
        else:
            exists_in_users = False
            exists_in_groups = False

            if selectable_map[sure_selected]['groups'] is not None:
                groups = selectable_map[sure_selected]['groups']

                for group in groups:

                    if __is_user_in_group(subprofile,group):

                        exists_in_groups=True
                if not exists_in_groups:
                    if restrict_mode:
                        raise CompatibilityException(f"{subprofile} is trying to select {sure_selected} and it's not for his groups.")
                    else:
                        skipped_aliases.setdefault(sure_selected,{'info':f"{subprofile} is trying to select {sure_selected} and it's not for his groups."})
            if selectable_map[sure_selected]['users'] is not None:
                if not __user_exists(subprofile) or subprofile not in selectable_map[sure_selected]['users']:

                    if restrict_mode:
                        raise CompatibilityException(f"{subprofile} is trying to select {sure_selected} but is not for him")
                    else:
                        skipped_aliases.setdefault(sure_selected,f"{subprofile} is trying to select {sure_selected} but is not for him")
                else:
                    exists_in_users=True
            #print(str(exists_in_users) + " " + str(exists_in_groups))
            if exists_in_users or exists_in_groups:
                selected_map.setdefault(sure_selected,selectable_map[sure_selected])
    return selected_map,skipped_aliases



def remove_redundant_alias_from_selected_list_by_a_subprofile(selected_list):
    return list(set(selected_list))

def __get_content_sub_profile_not_already_processed(structure_name, subprofile):
    try:
        full_path_subpofile = f"{APPARMOR_PATH}{structure_name}/{subprofile}"
        with open(full_path_subpofile,'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"apparmor.d/{structure_name}/{subprofile} doesn't exists")

def __fix_indentation_in_sub_profile(subprofile_content,indentation= " " * 5):
    start_row = subprofile_content.find("{")
    end_row = subprofile_content.rfind("}")
    if start_row == -1 or end_row == -1:
        return subprofile_content
    content = subprofile_content[start_row + 1:end_row].strip()
    rows = content.splitlines()
    indented_rows = [indentation + row.strip() for row in rows if row.strip()]
    format_content = subprofile_content[:start_row +1 ] + '\n' + '\n'.join(indented_rows) + '\n' + subprofile_content[end_row:]
    return format_content

def __filter_sub_profile_content_not_already_processed(subprofile_content_not_already_processed):
    rows = subprofile_content_not_already_processed.splitlines()
    filtered_rows = [
        row.strip() for row in rows if "profile" not in row and "select" not in row and "}" not in row.strip()
    ]
    filtered_string = '\n'.join(filtered_rows)
    return filtered_string

def inject_rules_in_subprofile(mixed_str, structure_name, subprofile):
    content_sub_profile_not_already_processed = __get_content_sub_profile_not_already_processed(structure_name, subprofile)

    filtered_content_sub_profile_not_already_processed = __filter_sub_profile_content_not_already_processed(content_sub_profile_not_already_processed)
    print("Contenuto filtrato")
    print(filtered_content_sub_profile_not_already_processed)
    filtered_list = [row.strip() for row in filtered_content_sub_profile_not_already_processed.splitlines() if row.strip()]
    mixed_list = [row.strip() for row in mixed_str.splitlines() if row.strip()]
    print(filtered_list)
    print(mixed_list)
    if filtered_list == mixed_list:
        print("Sono qua")
        return -1
    else:
        uncommon_rule = __get_uncommon(mixed_list,filtered_list)
        print(uncommon_rule)
        content_sub_profile_processed = content_sub_profile_not_already_processed.replace("}", '\n'.join(
            uncommon_rule) + "\n" + "}")
        print(content_sub_profile_processed)
        content_sub_profile_processed = __fix_indentation_in_sub_profile(content_sub_profile_processed)
        print(content_sub_profile_processed)
        try:
            full_path_subprofile = f"{APPARMOR_PATH}{structure_name}/{subprofile}"
            print(subprofile)
            with open(full_path_subprofile,'w') as file:
                #print("Sto scrivendo nel file")
                file.write(content_sub_profile_processed)
            return 1
        except FileNotFoundError:
            print(f"apparmor.d/{structure_name}/{subprofile} doesn't exists")

def PROCESS_SUBPROFILES(selectable_map,permissions_base,structure_name,restrict_mode,subprofiles):
    path = f"{APPARMOR_PATH}{structure_name}/"
    profiles_with_warnings = []
    for subprofile in subprofiles:
        full_path = os.path.join(path,subprofile+".bak")
        if full_path.endswith(".bak"):
            '''os.path.isfile(full_path) and '''
            #Dobbiamo lavorare sui .bak
            print(f"SUBPROFILE A {subprofile}")
            #print(refactoring_check_selectsyntax_and_get_selected_aliases_by_specific_subprofile(structure_name, subprofile))
            #Qua lavoriamo sulla copia
            g_select_list = refactoring_check_selectsyntax_and_get_selected_aliases_by_specific_subprofile(structure_name, subprofile+".bak")
            print(f"G_SELECT_LIST {g_select_list}")
            if g_select_list is not None:
                #Qua non lavoriamo su nessun file
                select_list = remove_redundant_alias_from_selected_list_by_a_subprofile(g_select_list)
                print(f"A {select_list}")
                #Qua dobbiamo passare il nome del profilo
                selected_map,skipped_alias = check_compatibility_subprofile(selectable_map,select_list,subprofile,restrict_mode)
                if skipped_alias:
                    profiles_with_warnings.append(subprofile)
                print("Sono qua")
                selected_map_str = __process_selected_map_to_str(selected_map)
                permissions_base_str = __process_base_perms_to_str(permissions_base)
                mixed_rules = __mix_selected_rules(permissions_base_str,selected_map_str)
                print("Debug attivo:")
                print(mixed_rules)

                inject_rules_in_subprofile(mixed_rules,structure_name,subprofile+".bak")
    return profiles_with_warnings

def PROCESS_ON_SPECIFIC_SUBPROFILES(selectable_map,permissions_base,executable_sub_profiles_folder,restrict_mode,subprofiles):
    path = f"apparmor.d/{executable_sub_profiles_folder}/"
    profiles_with_warnings = []
    if not os.path.exists(path):
        raise StructureException(f"Structure for {executable_sub_profiles_folder.replace(".","/")} doesn't exists")
    for subprofile in subprofiles:
        full_path = os.path.join(path,subprofile+".bak")
        if os.path.isfile(full_path) and full_path.endswith(".bak"):
            selected_list = check_select_synthax_and_get_aliases_selected_by_specific_subprofile(
                executable_sub_profiles_folder, subprofile)
            print(selected_list)
            # if len(selected_list) == 0:
            #    continue

            selected_list = remove_redundant_alias_from_selected_list_by_a_subprofile(selected_list)

            # Se selected_list ha due elementi uguali, ne dobbiamo tenere solo uno

            selected_map, skipped_alias = check_compatibility_subprofile(selectable_map, selected_list, subprofile,
                                                                         restrict_mode)
            if skipped_alias:
                profiles_with_warnings.append(subprofile)

            selected_map_str = __process_selected_map_to_str(selected_map)
            ##print(selected_map_str)
            permission_base_str = __process_base_perms_to_str(permissions_base)
            print(permission_base_str)
            mixed_rules = __mix_selected_rules(permission_base_str, selected_map_str)
            print(mixed_rules)
            inject_rules_in_subprofile(mixed_rules, executable_sub_profiles_folder, subprofile+".bak")

        return profiles_with_warnings

def PROCESS_ON_ALL_SUBPROFILES(selectable_map,permissions_base, executable_sub_profiles_folder,restrict_mode):
    path = f"apparmor.d/{executable_sub_profiles_folder}"
    profiles_with_warnings = []
    if not os.path.exists(path):
        raise StructureException(f"Structure for {executable_sub_profiles_folder.replace(".", "/")} doesn't exists.")
    for subprofile in os.listdir(path):
        full_path = os.path.join(path, subprofile)
        if os.path.isfile(full_path) and full_path.endswith(".bak"):

            selected_list = check_select_synthax_and_get_aliases_selected_by_specific_subprofile(executable_sub_profiles_folder,subprofile)
            #if len(selected_list) == 0:
            #    continue

            selected_list = remove_redundant_alias_from_selected_list_by_a_subprofile(selected_list)

                #Se selected_list ha due elementi uguali, ne dobbiamo tenere solo uno

            selected_map,skipped_alias=check_compatibility_subprofile(selectable_map,selected_list,subprofile[:-4],restrict_mode)
            if skipped_alias:
                profiles_with_warnings.append(subprofile[:-4])

            selected_map_str = __process_selected_map_to_str(selected_map)
            ##print(selected_map_str)
            permission_base_str = __process_base_perms_to_str(permissions_base)
            #print(permission_base_str)
            mixed_rules = __mix_selected_rules(permission_base_str,selected_map_str)

            inject_rules_in_subprofile(mixed_rules,executable_sub_profiles_folder,subprofile)

    return profiles_with_warnings


