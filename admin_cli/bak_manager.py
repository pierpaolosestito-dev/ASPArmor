import os
import shutil
from config import APPARMOR_PATH
#APPARMOR_PATH = "/etc/apparmor.d/" #TODO: pydotenv

def create_backup_for_each_subprofile_in_order_to_work_on_copy_and_not_on_original(structure_name, subprofiles):
    directory_path = f"{APPARMOR_PATH}{structure_name}"
    for file_name in os.listdir(directory_path):
        # Costruisce il percorso completo del file
        file_path = os.path.join(directory_path, file_name)

        # Salta i file che terminano con .bak o che si chiamano "mappings"
        if file_name.endswith('.bak') or file_name == "mappings" or not os.path.isfile(file_path):
            continue

        # Controlla che sia un file (e non una directory)
        if os.path.isfile(file_path) and file_name in subprofiles:
            # Costruisce il percorso per il file di backup
            backup_path = f"{file_path}.bak"
            # Copia il contenuto del file originale nel file di backup
            shutil.copy(file_path, backup_path)
            print(f"Creato il backup: {backup_path}")

def copy_from_backup_file_to_original_after_process(structure_name, subprofiles):
    directory_path = f"{APPARMOR_PATH}{structure_name}"
    for file_name in os.listdir(directory_path):
        # Controlla se il file termina con .bak
        if file_name.endswith('.bak'):
            # Costruisce i percorsi completi per il file .bak e per il file originale
            bak_file_path = os.path.join(directory_path, file_name)
            original_file_path = os.path.join(directory_path, file_name[:-4])  # Rimuove ".bak" dal nome

            # Verifica che il file .bak sia effettivamente un file
            if os.path.isfile(bak_file_path) and file_name[:-4] in subprofiles:
                # Copia il contenuto del file .bak nel file originale
                shutil.copy(bak_file_path, original_file_path)
                #print(f"Ripristinato {original_file_path} dal file {bak_file_path}")

def delete_all_backup_for_each_subprofile(structure_name):
    directory_path = f"{APPARMOR_PATH}{structure_name}/"
    for file_name in os.listdir(directory_path):
        # Costruisce il percorso completo del file
        file_path = os.path.join(directory_path, file_name)

        # Verifica se il file termina con .bak ed è un file
        if file_name.endswith('.bak') and os.path.isfile(file_path):
            # Elimina il file
            os.remove(file_path)
            #print(f"File eliminato: {file_path}")