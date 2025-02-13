from operator import index

from apparmor_utilities_integration import check_syntax_with_apparmor_parser
from exceptions import SelectableException, SelectableSynthaxException, SynthaxException
import os
from regexs import check_selectable_row, parse_rlimit_string
from config import APPARMOR_PATH
#HARDCODED_APPARMOR_PATH = "/etc/apparmor.d/" #TODO: pydotenv
def check_rlimit_rules_and_mapout(executable_path,generic_apparmor_profile):
    rlimit_rules = []
    with open(generic_apparmor_profile,'r') as file:
        lines = file.readlines()
    first_block_start_index = -1
    for i, line in enumerate(lines):
        s_line = line.strip()
        if executable_path in s_line and not s_line.startswith("#") and s_line.endswith(" {"):
            first_block_start_index = i
            break
    for i in range(first_block_start_index + 1, len(lines) - 1):
        s_line = lines[i].strip()
        if "#@+ignore" in s_line or "#@" and "+" and "ignore" in s_line:
            continue
        if s_line != "" and s_line != " " and s_line != "\n":
            if parse_rlimit_string(s_line) is not None:
                rlimit_rules.append(parse_rlimit_string(s_line))

    #Andrei a
    return rlimit_rules

def refactoring_checkselectablesynthax_and_mapout_basepermissions_selectablerule(executable_path,executable_name,generic_apparmor_profile):
    base_permissions = []
    selectable_map = {}
    index_to_skip = []
    with open(generic_apparmor_profile,'r') as file:
        lines = file.readlines()
    first_block_start_index = -1
    for i, line in enumerate(lines):
        s_line = line.strip()
        if executable_path in s_line and not s_line.startswith("#") and s_line.endswith(" {"):
            first_block_start_index = i
            break
    #print(first_block_start_index)
    for i in range(first_block_start_index+1,len(lines)-1):
        s_line = lines[i].strip()
        if "#@+ignore" in s_line or "#@" and "+" and "ignore" in s_line:
            continue
        if s_line != "" and s_line!=" " and s_line != "\n":
            if i not in index_to_skip and check_selectable_row(s_line) is not None:
                if not s_line.endswith(","):
                    raise SelectableSynthaxException(f"Line {i}: Rule must end with ,.")
                info_s_line = check_selectable_row(s_line)
                if info_s_line['alias'] in selectable_map:
                    raise SelectableException(f"Line {i}: More than one rule with same alias.")
                selectable_map[info_s_line['alias']] = info_s_line
            elif i not in index_to_skip and check_selectable_row(s_line,False) is not None:
                info_block = check_selectable_row(s_line,False)
                if info_block['alias'] in selectable_map:
                    raise SelectableException(f"Line {i}: More than one rule with same alias.")
                eff_rule=""
                for index_inside_selectable_box in range(i+1,len(lines)-1):
                    if "#@end" in lines[index_inside_selectable_box]:
                        break
                    if not lines[index_inside_selectable_box].strip().startswith("#"):
                        raise SelectableSynthaxException(f"Line {index_inside_selectable_box}: Rule inside selectable box must starts with #")
                    eff_rule += lines[index_inside_selectable_box].strip()[1:] + "\n"
                selectable_map[info_block['alias']] = {"rule": eff_rule.strip(), "groups": info_block['groups'], "users": info_block['users']}
            elif s_line.startswith("profile") or s_line.startswith("^"):
                index_to_skip.append(i)
                for index_inside_profile in range(i+1,len(lines)-1):
                    if lines[index_inside_profile].strip().endswith("}") or lines[index_inside_profile].strip() == "}":
                        index_to_skip.append(index_inside_profile)
                        break
                    index_to_skip.append(index_inside_profile)
                    #print(lines[index_inside_profile].strip())
            elif i not in index_to_skip and not s_line.startswith("#") or s_line.startswith("#include") or s_line.startswith("# include"):
                base_permissions.append(s_line)

    return base_permissions,selectable_map
def check_selectablesynthax_and_get_basepermissions_and_mapout_selectablerule(executable_name,file_path,only_check_syntax=False):
    try:
        basepermissions = []
        selectable_map = {}
        rows = None
        with open(file_path,'r') as file:
            rows = file.readlines()
        with open(file_path,'r') as file:
            inside_curly_braces = False
            for index,row in enumerate(file):
                row = row.strip()
                if row.endswith("{"):
                    inside_curly_braces=True

                if inside_curly_braces:
                    # Permessi base
                    if not row.startswith("#") and executable_name not in row and row!="}" and row!="" and row!=" " and "#@+ignore" not in row:
                        basepermissions.append(row)
                    #Selectable inline
                    if row.startswith("#@+"):
                        info_extracted_from_selectable_row = check_selectable_row(row)
                        if info_extracted_from_selectable_row is not None:
                            if info_extracted_from_selectable_row['alias'] in selectable_map:
                                raise SelectableException(f"Line {index}: More than one rule with same alias.")
                            selectable_map[info_extracted_from_selectable_row['alias']] = info_extracted_from_selectable_row
                        else:
                            raise SelectableSynthaxException(f"Line {index}: Synthax error in selectable line.")
                    #TODO: Selectable boxes, IDEA -> Prendo tutto quello che è tra selectable_inline without plus_delimiter e #@end e costruisco una stringa togliendo il # iniziale
                    if row.startswith("#@") and not row.startswith("#@+") and "end" not in row:

                        info_extracted_from_first_row_selectable_box = check_selectable_row(row, False)
                        if info_extracted_from_first_row_selectable_box is None:
                            raise SelectableSynthaxException(f"Line {index}: Synthax error in selectable line.")
                        else:
                            index_box_starts = index
                            alias, groups, users = "", "", ""
                            find_end = False
                            rules = ""

                            if info_extracted_from_first_row_selectable_box['alias'] in selectable_map:
                                raise SelectableException(f"Line {index}: More than one rule with same alias.")
                            else:
                                alias = info_extracted_from_first_row_selectable_box['alias']
                                groups = info_extracted_from_first_row_selectable_box['groups']
                                users = info_extracted_from_first_row_selectable_box['users']
                                for index_inside_box in range(index_box_starts+1,len(rows)):
                                    if rows[index_inside_box].strip() == "#@end":
                                        find_end=True
                                        break
                                    if not rows[index_inside_box].strip().startswith("#"):
                                        raise SelectableSynthaxException(f"Line {index}: Rule inside selectable box must starts with #")
                                    else:
                                        rules+=rows[index_inside_box].strip()[1:]+"\n"
                                       #selectable_map[alias]['rule']+=rows[index_inside_box].strip()[1:]
                                if not find_end:
                                    raise SelectableSynthaxException(f"Line {index_box_starts}: You must terminate selectable boxes with #@end")
                                else:
                                    selectable_map[alias] = {"rule":rules,"groups":groups,"users":users}




                        for index_inside_box in range(index_box_starts,len(rows)):
                            pass

        return basepermissions,selectable_map
    except FileNotFoundError as fe:
        print(f"{fe}")

def extract_executablename_and_path_linked_to_apparmor_profile_from_generic_profile(file_path):
    try:
        with open(file_path,'r') as file:
            for riga in file:
                riga = riga.strip()
                if not riga.startswith("#") and riga.endswith("{"):
                    executable = riga.split("{")[0].strip()
                    if "profile" in executable:
                        return executable.split(" ")[1],os.path.basename(executable.split(" ")[1])
                    return executable,os.path.basename(executable)
    except FileNotFoundError:
        print(f"{file_path} not found.")
    except Exception as e:
        print(f"Error {e}")
#print(check_selectablesynthax_and_get_basepermissions_and_mapout_selectablerule("forse.sh","apparmor.d/second_prototype"))


#Casi
#Casi contiene la direttiva:
    #La dobbiamo commentare
#Casi non contiene la direttiva:
    #La inseriamo commentata
#Non contiene la direttiva e deve ritornare False e se non contiene la direttiva lanciamo un StructureException


#TODO: Ci dobbiamo preoccupare se è presente ignore alla fine
def manipulate_directive_include_structure_directory_mappings(path_to_generic_profile, executable_path, structure_directory):
    original_content = ""
    with open(path_to_generic_profile,'r') as file:
        original_content = file.readlines()

    print(structure_directory)
    index_directive = -1
    index_start_profile = -1
    for line in original_content:
        if structure_directory+"/mappings" in line:
            index_directive = original_content.index(line)
            break
        if executable_path in line and line.strip().endswith("{"):
            index_start_profile = original_content.index(line)
    print(index_start_profile)

    if index_directive==-1:
        original_content.insert(index_start_profile+1,f"##include <{structure_directory}/mappings> #@+ignore\n")
        print("Non esiste la direttiva")
    else:
        print(index_directive)
        directive = original_content[index_directive]
        manipulated_directive = ""
        print(directive.strip())
        if not directive.strip().startswith("##"):
            print("Non è commentata correttamente potrebbe iniziare con un commento solo")
            if directive.strip().startswith("#"):
                print("Dobbiamo inserire solo un altro #")
                manipulated_directive = directive.replace("#include","##include")
            else:
                print("Ne dobbiamo inserire 2")
                manipulated_directive = directive.replace("include","##include")
            print(manipulated_directive)
        else:
            print("Direttiva già corretta")
            return index_directive

        print(original_content[index_directive])
        original_content[index_directive] = manipulated_directive
        print(original_content[index_directive])
    with open(path_to_generic_profile,'w') as file:
        file.write("".join(original_content))
    return index_directive


def uncomment_directive_include_structure_directory_mappings(path_to_generic_profile, structure_name, index_directive=-1):
    original_content = ""
    with open(path_to_generic_profile,'r') as file:
        original_content = file.readlines()

    if index_directive == -1:
        index_directive_new = -1
        for line in original_content:
            if "##include <"+structure_name+ "/mappings" in line:
                index_directive_new = original_content.index(line)
                break

        index_directive = index_directive_new
    original_content[index_directive] = original_content[index_directive].replace("##include","include")
    with open(path_to_generic_profile,'w') as file2:
        file2.write(''.join(original_content))


def delete_file(path_file):
    try:
        # Controlla se il file esiste
        if os.path.exists(path_file):
            # Elimina il file
            os.remove(path_file)
            print(f"File eliminato: {path_file}")
            return True
        else:
            print(f"File non trovato: {path_file}")
            return False
    except Exception as e:
        # Gestisce eventuali errori e li stampa
        print(f"Errore durante l'eliminazione del file {path_file}: {e}")
        raise

#TODO: Faccio una funzione che crea un file .bak temporaneo con la copia del profilo originale e va a togliere i selectable e tutto il resto e lo rende pulito.
def copy_and_check_syntax(path_file):
    with open(path_file,'r') as file:
        lines = file.readlines()

    #print(lines)
    cleaned_lines = []
    inside_block = False
    for i in range(len(lines)):
        line = lines[i].strip()
        info_extracted_from_selectableplus_row = check_selectable_row(line)
        info_extracted_from_selectableblock_row = check_selectable_row(line, False)
        if info_extracted_from_selectableplus_row is not None:
            cleaned_lines.append(info_extracted_from_selectableplus_row['rule'])
        elif info_extracted_from_selectableblock_row is not None:
            inside_block = True
        elif "#@end" in line or "#@" in line and "end" in line:
           inside_block = False
        elif inside_block and info_extracted_from_selectableblock_row is None:
            cleaned_lines.append(line.lstrip("#"))
        else:
            cleaned_lines.append(line)

    #print('\n'.join(cleaned_lines))
    path = f"{APPARMOR_PATH}var/"
    if not os.path.exists(path):
        os.makedirs(path)
    copy_file_path = os.path.join(path,f"{os.path.basename(path_file)}-copy")
    with open(copy_file_path,'w') as w:
        w.write('\n'.join(cleaned_lines))

    try:
        check_syntax_with_apparmor_parser(copy_file_path)
        delete_file(copy_file_path)
        return True
    except SynthaxException as e:
        delete_file(copy_file_path)
        raise SynthaxException(e)
#copy_and_check_syntax("apparmor.d/second_prototype")