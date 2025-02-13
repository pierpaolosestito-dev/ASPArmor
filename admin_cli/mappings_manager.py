import os
import re
from datetime import datetime

from exceptions import StructureException
from config import APPARMOR_PATH
#APPARMOR_PATH = "/etc/apparmor.d/" #TODO: pydotenv
def clean_mappings_file(structure_name):
    try:
        with open(f"{APPARMOR_PATH}{structure_name}/mappings", 'w') as file:
            file.write("")
    except FileNotFoundError as fe:
        print(f"{fe}")

def generate_mappings_file(structure_name, executable_path, files_to_include = []):
    mappings_file_path = os.path.join(f"{APPARMOR_PATH}{structure_name}/", "mappings")
    profiles_that_we_upload_in_kernel_at_next_step = []
    try:
        if not os.path.exists(mappings_file_path):
            raise StructureException(f"Structure {structure_name} doesnt' exists.")
        if len(files_to_include) == 0:
            files_to_include = [
                f for f in os.listdir(f"{APPARMOR_PATH}{structure_name}")
                if os.path.isfile(os.path.join(f"{APPARMOR_PATH}{structure_name}/", f)) and
                   not f.endswith(".bak") and f != "mappings"
            ]

        if not files_to_include:
            raise StructureException(f"No valid files found in structure {structure_name}")

        with open(mappings_file_path,'w') as mappings_file:
            for filename in files_to_include:
                file_path = os.path.join(f"{APPARMOR_PATH}{structure_name}", filename)
                profiles_that_we_upload_in_kernel_at_next_step.append(f"{executable_path}//{filename}")
                with open(file_path,'r') as file:
                    mappings_file.write(file.read())
                    mappings_file.write("\n\n")
        return profiles_that_we_upload_in_kernel_at_next_step

    except FileNotFoundError as e:
        print(f"{e}")

def is_empty_mappings_file(structure_name):
    mappings_file_path = os.path.join(f"{APPARMOR_PATH}{structure_name}", "mappings")
    try:
        if not os.path.exists(mappings_file_path):
            raise StructureException("The file 'mappings' does not exists.")
        with open(mappings_file_path,'r') as mappings_file:
            content = mappings_file.read().strip()
            return len(content) == 0
    except Exception as e:
        return -1

def __replace_processed(original_content,new_string):
    search_pattern = r'# Processed at.*'
    original_content = [
        re.sub(search_pattern,new_string,line) for line in original_content

    ]
    return original_content

def sign_mappings(executable_sub_profiles_folder):
    try:
         path = os.path.join(f"apparmor.d/{executable_sub_profiles_folder}/",'mappings')
         original_content = ""
         current_datetime = datetime.now().strftime("%Y-%m-%d : %H:%M:%S")
         comment_line = f"# Processed at {current_datetime}"
         with open(path,'r') as file:
             original_content = file.readlines()

         #Forse non è efficientissimo fare '\n'.join(original_content)
         if "Processed at" in '\n'.join(original_content):

             original_content = __replace_processed(original_content,comment_line)
         else:
             original_content.insert(0,comment_line+"\n")

         with open(path,'w') as file2:
             file2.write(''.join(original_content))




    except FileNotFoundError:
        print("File doesn't exists")

