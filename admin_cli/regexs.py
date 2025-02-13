import re

def is_valid_include_pattern(string):
    """
    Verifica se una stringa rispetta il pattern specificato.

    Pattern validi:
    - #include <path/filename>
    - #include <filename>
    - include <path/filename>
    - include <filename>
    - Combinazioni di #include e include separati da spazi, con numero arbitrario di occorrenze.

    Args:
        string (str): La stringa da verificare.

    Returns:
        bool: True se la stringa rispetta il pattern, False altrimenti.
    """
    pattern = r"^((#include|include) <[a-zA-Z0-9_/]+>(\s+)?)+$"
    return bool(re.match(pattern, string))

def extract_include_statements(string):
    """
    Estrae una lista di dichiarazioni include valide da una stringa.

    Args:
        string (str): La stringa contenente dichiarazioni include.

    Returns:
        list: Una lista di dichiarazioni include valide.
    """
    pattern = r"((#include|include) <[a-zA-Z0-9_/]+>)"
    return [match.group() for match in re.finditer(pattern, string)]

def check_selectable_row(selectable_row, with_plus_as_delimiter=True):
    pattern = ""
    if with_plus_as_delimiter:
        pattern = r"^#@\+\s*selectable\s*\{\s*(?:groups=\[\s*(?P<groups>'[^']*'(?:,\s*'[^']*')*|\"[^\"]*\"(?:,\s*\"[^\"]*\")*)?\s*\],?)?\s*(?:users=\[\s*(?P<users>'[^']*'(?:,\s*'[^']*')*|\"[^\"]*\"(?:,\s*\"[^\"]*\")*)?\s*\],?)?\s*(?:alias=[\"'](?P<alias>[^\"']+)[\"'])?\s*(?:,groups=\[\s*(?P<groups2>'[^']*'(?:,\s*'[^']*')*|\"[^\"]*\"(?:,\s*\"[^\"]*\")*)?\s*\])?\s*(?:,users=\[\s*(?P<users2>'[^']*'(?:,\s*'[^']*')*|\"[^\"]*\"(?:,\s*\"[^\"]*\")*)?\s*\])?\s*\}\s*(?P<resto>.+)$"

    else:
        pattern = r"^#@\s*selectable\s*\{\s*(?:groups=\[\s*(?P<groups>[^\]]*)\s*\],?)?\s*(?:users=\[\s*(?P<users>[^\]]*)\s*\],?)?\s*(?:alias=[\"'](?P<alias>[^\"']+)[\"'])?\s*(?:,groups=\[\s*(?P<groups2>[^\]]*)\s*\])?\s*(?:,users=\[\s*(?P<users2>[^\]]*)\s*\])?\s*\}$"
    # Ricerca della regex nella stringa

    match = re.search(pattern, selectable_row)

    if match:
        alias = match.group('alias')

        groups = match.group('groups') if match.group('groups') else match.group('groups2')
        users = match.group('users') if match.group('users') else match.group('users2')
        groups = groups.replace("'","") if groups != None else groups
        groups = groups.replace('"',"") if groups != None else groups
        users = users.replace("'", "") if users != None else users
        users = users.replace('"', "") if users != None else users
        groups_list = [item.strip().strip("'") for item in groups.split(",")] if groups != None else groups
        users_list = [item.strip().strip("'") for item in users.split(",")] if users != None else users

        resto = ""
        if with_plus_as_delimiter:
            resto = match.group('resto')


            return {
                'rule': resto,
                'alias': alias,
                'groups': groups_list,#groups.replace("'","") if groups != None else groups,
                'users': users_list,#users.replace("'","") if users != None else users,
                #'rule': resto,  # Cattura qualsiasi cosa segua la parentesi graffa
            }
        else:
            return {
                'alias': alias,
                'groups': groups_list,#groups.replace("'", "") if groups != None else groups,
                'users': users_list#users.replace("'", "") if users != None else users,
                # 'rule': resto,  # Cattura qualsiasi cosa segua la parentesi graffa
            }
    else:
        return None

def check_select_row(select_row):
    pattern = r"^#@\+\s*select\s*:\s*(?P<args>.+)$"
    match = re.search(pattern, select_row)
    if match:
        args = match.group('args')
        # Dividiamo la stringa sugli spazi e rimuoviamo gli spazi extra da ciascun elemento
        return [element.strip() for element in args.split(',') if element.strip()]
    return None

test1 = "#@+select: a, y,    z"
test2 = "#@+select:a, y, z"
test3 = '#@+select : a,y,z'
test4 = '#@+select : a,y'


def parse_rlimit_string(input_string):
    pattern = r"#@\s*RLIMIT\s+([A-Z]+)\s+(\d+)"
    match = re.search(pattern, input_string)

    if match:
        resource = match.group(1)  # Campo (es. MEMORY, CPU, FILED)
        value = int(match.group(2))  # Numero (es. 100, 125)
        return (resource, value)  # Restituisce la coppia
    else:
        return None  # Restituisce None se la stringa non rispetta la regex

