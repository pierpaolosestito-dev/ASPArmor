import subprocess
import os
from exceptions import SynthaxException, AppArmorException


def check_syntax_with_apparmor_parser(path_file):
    aa_parser = ['sudo','apparmor_parser','-Q',path_file]
    try:
        result = subprocess.run(aa_parser,capture_output=True,text=True)
        if result.stderr != "":
            raise SynthaxException(f"{result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"Error {e}")


def aa_disable_with_apparmor(profile_to_disable):
    aa_disable = ['aa-disable',profile_to_disable]
    try:
        result = subprocess.run(aa_disable,capture_output=True,text=True)
        if result.stderr != "":
            raise AppArmorException(f"{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error {e}")

def aa_enforce_with_apparmor(profile_to_enable):
    aa_enable = ['aa-enforce', profile_to_enable]
    try:
        result = subprocess.run(aa_enable, capture_output=True, text=True)
        if result.stderr != "":
            raise AppArmorException(f"{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error {e}")

def aa_complain_with_apparmor(profile_to_complain):
    aa_complain = ['aa-complain', profile_to_complain]
    try:
        result = subprocess.run(aa_complain, capture_output=True, text=True)
        if result.stderr != "":
            raise AppArmorException(f"{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error {e}")

def apparmor_parser_active_profile(path_file):
    aa_parser = ['sudo','apparmor_parser','-r',path_file]
    try:
        result = subprocess.run(aa_parser,capture_output=True,text=True)
        print(result.stdout)
        if result.stderr != "":
            raise SynthaxException(f"{result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error {e}")
#aa-disable
#aa-cleanprof

def get_complain_mode_profiles(contains=None, row_to_start=-1):
    with open('/sys/kernel/security/apparmor/profiles','r') as file:
        lines = file.readlines()
    complain_records = []
    '''enforce_records = [
                line.replace(" (enforce)", "").strip()
                for line in lines if "(enforce)" in line and "//" in line
            ]'''
    if row_to_start != -1:
        if row_to_start < 0 or row_to_start >= len(lines):
            raise ValueError("Index out of range.")
        for i in range(row_to_start,len(lines)):
            s_line = lines[i].strip()
            if "complain" in s_line:
                complain_records.append(s_line.replace("(complain)","").strip())
    else:
        for i in range(len(lines)):
            s_line = lines[i].strip()
            if "complain" in s_line:
                complain_records.append(s_line.replace("(complain)", "").strip())
    if contains:
        complain_records_with_contains = []
        for complain in complain_records:
            if contains in complain:
                complain_records_with_contains.append(complain)
        return complain_records_with_contains,len(lines)-1
    return complain_records,len(lines)-1
#Devo usare questo
def get_enforce_mode_profiles(contains=None, row_to_start=-1):
    with open('/sys/kernel/security/apparmor/profiles','r') as file:
        lines = file.readlines()
    enforce_records = []
    '''enforce_records = [
                line.replace(" (enforce)", "").strip()
                for line in lines if "(enforce)" in line and "//" in line
            ]'''
    if row_to_start != -1:
        if row_to_start < 0 or row_to_start >= len(lines):
            raise ValueError("Index out of range.")
        for i in range(row_to_start,len(lines)):
            s_line = lines[i].strip()
            if "enforce" in s_line:
                enforce_records.append(s_line.replace("(enforce)","").strip())
    else:
        for i in range(len(lines)):
            s_line = lines[i].strip()
            if "enforce" in s_line:
                enforce_records.append(s_line.replace("(enforce)", "").strip())
    if contains:
        enforce_records_with_contains = []
        for enforce in enforce_records:
            if contains in enforce:
                enforce_records_with_contains.append(enforce)
        return enforce_records_with_contains,len(lines)-1
    return enforce_records,len(lines)-1


def get_disabled_mode_profiles(contains=None):
    directory = "/etc/apparmor.d/disable"
    try:
        # Controlla se la directory esiste
        if not os.path.exists(directory):
            return f"La directory {directory} non esiste."

        # Elenca tutti i file nella directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        if not files:
            return f"Nessun file trovato nella directory {directory}."
        if contains is not None:
            files = [file for file in files if contains in file]
        return files
    except Exception as e:
        return f"Si è verificato un errore: {e}"




