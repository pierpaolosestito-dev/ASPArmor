#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LENGTH 1024
#define BUFFER_SIZE 1024
#define SELECT_PREFIX "#@select:"

#define TEMP_FILENAME "temp_file.tmp"

// Funzione per estrarre e trasformare il path
char *extract_and_replace_path(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Errore nell'apertura del file");
        return NULL;
    }

    static char transformed_path[MAX_LINE_LENGTH];
    char line[MAX_LINE_LENGTH];

    while (fgets(line, sizeof(line), file)) {
        char *brace_pos = strchr(line, '{');  // Trova il primo `{`
        if (brace_pos) {
            *brace_pos = '\0'; // Tronca la stringa prima del `{`
            
            // Rimuove eventuali spazi bianchi finali
            char *end = brace_pos - 1;
            while (end > line && isspace((unsigned char)*end)) {
                *end-- = '\0';
            }

            // Sostituisce i '/' con '.'
            for (char *p = line; *p; p++) {
                if (*p == '/') {
                    *p = '.';
                }
            }

            strcpy(transformed_path, line);
            fclose(file);
            return transformed_path;
        }
    }

    fclose(file);
    return NULL; // Se non trova il path
}

// Funzione per controllare ed eventualmente aggiungere la riga include if exists PRIMA della }
void check_and_add_include(const char *filename, const char *transformed_path) {
    if (!transformed_path) {
        fprintf(stderr, "Errore: path non trovato.\n");
        return;
    }

    char search_line[MAX_LINE_LENGTH];
    snprintf(search_line, sizeof(search_line), "include if exists <%s/mappings>", transformed_path);

    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Errore nell'apertura del file");
        return;
    }

    FILE *temp_file = fopen(TEMP_FILENAME, "w");
    if (!temp_file) {
        perror("Errore nella creazione del file temporaneo");
        fclose(file);
        return;
    }

    char line[MAX_LINE_LENGTH];
    int found = 0;
    int added = 0;

    while (fgets(line, sizeof(line), file)) {
        if (strstr(line, search_line)) {
            found = 1;
        }

        if (!found && strchr(line, '}') && !added) {
            fprintf(temp_file, "%s\n", search_line);
            added = 1;
        }

        fprintf(temp_file, "%s", line);
    }

    fclose(file);
    fclose(temp_file);

    if (!found) {
        if (remove(filename) != 0 || rename(TEMP_FILENAME, filename) != 0) {
            perror("Errore nella modifica del file");
        } else {
            printf("Aggiunta riga: %s\n", search_line);
        }
    } else {
        remove(TEMP_FILENAME);
        printf("La riga esiste già, nessuna modifica necessaria.\n");
    }
}


// Struttura per i valori di #@select:
typedef struct {
    char **values;
    size_t count;
} SelectList;

// Struttura per #@selectable
typedef struct {
    char *alias;
    char *rule;
} SelectableEntry;

typedef struct {
    SelectableEntry *entries;
    size_t count;
} SelectableList;

// Funzione per liberare la lista di #@select:
void free_select_list(SelectList *list) {
    if (!list) return;
    for (size_t i = 0; i < list->count; i++) {
        free(list->values[i]);
    }
    free(list->values);
}

// Funzione per liberare la lista di #@selectable
void free_selectable_list(SelectableList *list) {
    if (!list) return;
    for (size_t i = 0; i < list->count; i++) {
        free(list->entries[i].alias);
        free(list->entries[i].rule);
    }
    free(list->entries);
}

// Funzione per estrarre i valori da #@select: e restituire una lista dinamica
SelectList extract_select_values(const char *filename) {
    FILE *file = fopen(filename, "r");
    SelectList list = {NULL, 0};

    if (!file) {
        perror("Errore nell'apertura del file");
        return list;
    }

    char buffer[BUFFER_SIZE];

    while (fgets(buffer, BUFFER_SIZE, file)) {
        char *pos = strstr(buffer, SELECT_PREFIX);
        if (pos) {
            pos += strlen(SELECT_PREFIX); // Spostiamo il puntatore dopo "#@select:"
            while (*pos == ' ' || *pos == '\t') pos++; // Ignoriamo gli spazi

            // Tokenizza i valori separati da ','
            char *token = strtok(pos, ",\r\n");
            while (token) {
                list.values = realloc(list.values, (list.count + 1) * sizeof(char *));
                list.values[list.count] = strdup(token);
                list.count++;
                token = strtok(NULL, ",\r\n");
            }
            break; // Troviamo solo la prima occorrenza
        }
    }

    fclose(file);
    return list;
}

// Funzione per trovare righe #@selectable e restituire una struttura dati
SelectableList find_selectable_entries(const char *filename) {
    FILE *file = fopen(filename, "r");
    SelectableList list = {NULL, 0};

    if (!file) {
        perror("Errore nell'apertura del file");
        return list;
    }

    char line[MAX_LINE_LENGTH];
    int inside_multiline = 0;
    char alias[MAX_LINE_LENGTH] = {0};
    char rule[MAX_LINE_LENGTH] = {0};

    while (fgets(line, sizeof(line), file)) {
        char *start = strstr(line, "#@selectable{");
        if (start) {
            memset(alias, 0, sizeof(alias));
            memset(rule, 0, sizeof(rule));

            // Trova l'inizio e la fine dell'alias
            char *alias_start = strchr(start, '{');
            char *alias_end = strchr(start, '}');

            if (alias_start && alias_end && alias_end > alias_start) {
                strncpy(alias, alias_start + 1, alias_end - alias_start - 1);
                alias[alias_end - alias_start - 1] = '\0'; // Terminatore stringa

                // Se l'alias contiene "alias=", estrai solo il valore vero
                char *alias_token = strstr(alias, "alias=");
                if (alias_token) {
                    alias_token += 6;  // Salta "alias="
                    char *comma = strchr(alias_token, ',');  // Se ci sono altre info, tronca
                    if (comma) *comma = '\0';
                    strcpy(alias, alias_token);
                }
            }

            // Controlla se c'è già una regola sulla stessa riga
            char *rule_start = alias_end ? alias_end + 2 : NULL;  // Salta "} "
            if (rule_start && *rule_start != '\0' && *rule_start != '\n') {
                strncpy(rule, rule_start, MAX_LINE_LENGTH - 1);
                rule[strcspn(rule, "\n")] = '\0'; // Rimuove newline

                // Aggiungi alla lista
                list.entries = realloc(list.entries, (list.count + 1) * sizeof(SelectableEntry));
                list.entries[list.count].alias = strdup(alias);
                list.entries[list.count].rule = strdup(rule);
                list.count++;
            } else {
                // Inizia una regola multilinea
                inside_multiline = 1;
                strncpy(rule, "", MAX_LINE_LENGTH - 1);
            }
        } else if (inside_multiline) {
            // Continua a leggere la regola fino a #@end
            if (strstr(line, "#@end")) {
                inside_multiline = 0;
                // Aggiungi alla lista
                list.entries = realloc(list.entries, (list.count + 1) * sizeof(SelectableEntry));
                list.entries[list.count].alias = strdup(alias);
                list.entries[list.count].rule = strdup(rule);
                list.count++;
            } else {
                // Concatena la riga alla regola
                strncat(rule, line, MAX_LINE_LENGTH - strlen(rule) - 1);
            }
        }
    }

    fclose(file);
    return list;
}

// Funzione per verificare se un alias di #@selectable è presente in #@select:
char **check_alias_in_selectable(const SelectList *select_list, const SelectableList *selectable_list, size_t *match_count) {
    *match_count = 0;

    if (select_list->count == 0 || selectable_list->count == 0) {
        return NULL;  // Lista vuota se non ci sono dati da confrontare
    }

    char **matched_rules = NULL;

    for (size_t i = 0; i < select_list->count; i++) {
        for (size_t j = 0; j < selectable_list->count; j++) {
            if (strcmp(select_list->values[i], selectable_list->entries[j].alias) == 0) {
                matched_rules = realloc(matched_rules, (*match_count + 1) * sizeof(char *));
                matched_rules[*match_count] = strdup(selectable_list->entries[j].rule);
                (*match_count)++;
            }
        }
    }

    return matched_rules;
}

void inject_rules_into_file(const char *filename, char **matched_rules, size_t match_count) {
    if (match_count == 0 || matched_rules == NULL) {
        printf("Nessuna regola da iniettare.\n");
        return;
    }

    printf("Iniezione delle regole nel file: %s\n", filename);

    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Errore nell'apertura del file originale");
        return;
    }

    FILE *temp_file = fopen("temp_file.tmp", "w");
    if (!temp_file) {
        perror("Errore nella creazione del file temporaneo");
        fclose(file);
        return;
    }

    char line[MAX_LINE_LENGTH];
    int inserted = 0;

    while (fgets(line, sizeof(line), file)) {
        if (strchr(line, '}') && !inserted) {
            printf("Trovata chiusura '}', inserendo le regole...\n");

            for (size_t i = 0; i < match_count; i++) {
                fprintf(temp_file, "    %s\n", matched_rules[i]);
                printf("Regola iniettata: %s\n", matched_rules[i]);  // Debug
            }
            inserted = 1;
        }
        fprintf(temp_file, "%s", line);
    }

    fclose(file);
    fclose(temp_file);

    // Sovrascrivi il file originale
    if (remove(filename) != 0) {
        perror("Errore nella rimozione del file originale");
    } else if (rename("temp_file.tmp", filename) != 0) {
        perror("Errore nella rinomina del file temporaneo");
    } else {
        printf("Regole iniettate correttamente in %s\n", filename);
    }
}

// Struttura per contenere un array dinamico di stringhe
typedef struct {
    char **lines;
    size_t size;
} LineList;

#include <ctype.h>
#include <string.h>

// Funzione per rimuovere spazi all'inizio e alla fine di una stringa
char *trim(char *str) {
    char *end;

    // Trim spazi all'inizio
    while (isspace((unsigned char)*str)) str++;

    if (*str == 0)  // Se la stringa è vuota
        return str;

    // Trim spazi alla fine
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;

    // Aggiunge il terminatore
    *(end + 1) = '\0';

    return str;
}

// Funzione per aggiungere una riga alla lista
void add_line(LineList *list, const char *line) {
    list->lines = realloc(list->lines, (list->size + 1) * sizeof(char *));
    if (!list->lines) {
        perror("Errore di allocazione memoria");
        exit(EXIT_FAILURE);
    }
    list->lines[list->size] = strdup(line);
    if (!list->lines[list->size]) {
        perror("Errore di allocazione memoria per la stringa");
        exit(EXIT_FAILURE);
    }
    list->size++;
}

// Funzione per leggere il file e restituire le righe filtrate
LineList read_filtered_lines(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        perror("Errore apertura file");
        exit(EXIT_FAILURE);
    }

    LineList list = {NULL, 0};
    char line[MAX_LINE_LENGTH];

    int inside_block = 0;

    while (fgets(line, sizeof(line), file)) {
        // Rimuove il carattere di newline finale, se presente
        size_t len = strlen(line);
        if (len > 0 && line[len - 1] == '\n') {
            line[len - 1] = '\0';
        }

        // Controllo dell'inizio e della fine del blocco { }
        if (strchr(line, '{')) {
            inside_block = 1;
            continue;  // Salta la linea con '{'
        }
        if (strchr(line, '}')) {
            inside_block = 0;
            continue;  // Salta la linea con '}'
        }

        // Se siamo dentro il blocco, analizziamo la riga
        if (inside_block) {
            // Se non inizia con #, la includiamo
            char *trimmed_line = trim(line);

            
if (strncmp(trimmed_line, "#include", 8) == 0) {
    add_line(&list, trimmed_line);
} else if (trimmed_line[0] != '#') {
    add_line(&list, trimmed_line);
}
           
        }
    }

    fclose(file);
    return list;
}

// Funzione per stampare e liberare la lista
void free_list(LineList *list) {
    for (size_t i = 0; i < list->size; i++) {
        printf("%s\n", list->lines[i]);
        free(list->lines[i]);
    }
    free(list->lines);
}

void append_file(const char *first_filename, const char *second_filename) {
    FILE *first_file = fopen(first_filename, "r");
    if (!first_file) {
        perror("Errore nell'apertura del file sorgente");
        return;
    }

    FILE *second_file = fopen(second_filename, "a"); // Apri in modalità append
    if (!second_file) {
        perror("Errore nell'apertura del file di destinazione");
        fclose(first_file);
        return;
    }

    char buffer[1024];
    size_t bytes_read;

    // Copia il contenuto del primo file nel secondo
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), first_file)) > 0) {
        fwrite(buffer, 1, bytes_read, second_file);
    }

    fclose(first_file);
    fclose(second_file);
}
   void run_apparmor_parser(const char *path) {
    if (!path) {
        fprintf(stderr, "Errore: Il percorso specificato è nullo.\n");
        return;
    }

    // Comando per eseguire apparmor_parser in modalità di verifica (-r per il reload)
    char command[1024];
    snprintf(command, sizeof(command), "apparmor_parser -r \"%s\" 2>&1", path);

    // Apri un processo per eseguire il comando e catturare l'output
    FILE *pipe = popen(command, "r");
    if (!pipe) {
        perror("Errore nell'esecuzione di apparmor_parser");
        return;
    }

    // Legge e stampa l'output di errore in modo leggibile
    char buffer[1024];
    printf("\n--- Output di apparmor_parser ---\n");
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        printf("%s", buffer);
    }

    int status = pclose(pipe);
    if (status == -1) {
        perror("Errore nella chiusura del processo");
    } else if (WIFEXITED(status)) {
        int exit_code = WEXITSTATUS(status);
        if (exit_code != 0) {
            printf("\nAppArmor ha restituito un codice di errore: %d\n", exit_code);
        } else {
            printf("\nAppArmor ha caricato correttamente il profilo.\n");
        }
    }
}
   
// Main
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>

#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <file_input>\n", argv[0]);
        return EXIT_FAILURE;
    }
    
    char *transformed_path = extract_and_replace_path(argv[1]);
    if (transformed_path) {
        printf("Path trasformato: %s\n", transformed_path);
    }

    // Estrai #@selectable
    SelectableList selectable_list = find_selectable_entries(argv[1]);
    
    printf("\n--- Regole #@selectable trovate ---\n");
    for (size_t i = 0; i < selectable_list.count; i++) {
        printf("Alias: %s\nRegola: %s\n", selectable_list.entries[i].alias, selectable_list.entries[i].rule);
    }

    // INIZIO CICLO
    char dir_path[256];
    snprintf(dir_path, sizeof(dir_path), "/etc/apparmor.d/%s/", transformed_path);
    DIR *dir = opendir(dir_path);
    if (!dir) {
        perror("Errore nell'apertura della directory");
        return EXIT_FAILURE;
    }
    
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, "mappings") == 0 || strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        
        char user_path[256];
        snprintf(user_path, sizeof(user_path), "%s%s", dir_path, entry->d_name);

        // Estrai #@select:
        SelectList select_list = extract_select_values(user_path);

        printf("\n--- Valori trovati in #@select (%s): ---\n", entry->d_name);
        for (size_t i = 0; i < select_list.count; i++) {
            printf("%s\n", select_list.values[i]);
        }

        // Confronta gli alias trovati
        size_t match_count = 0;
        char **matched_rules = check_alias_in_selectable(&select_list, &selectable_list, &match_count);

        if (matched_rules) {
            printf("Numero di regole da iniettare: %lu\n", match_count);
            inject_rules_into_file(user_path, matched_rules, match_count);

            for (size_t i = 0; i < match_count; i++) {
                free(matched_rules[i]);
            }
            free(matched_rules);
        }

        // Filtra le righe dal file di input
        LineList result = read_filtered_lines(argv[1]);

        printf("Righe filtrate:\n");
        for (size_t i = 0; i < result.size; i++) {
            printf("%s\n", result.lines[i]);
        }

        // Usa le righe filtrate come regole da iniettare
        if (result.size > 0) {
            inject_rules_into_file(user_path, result.lines, result.size);
        }

        // Libera la memoria
        free_list(&result);

        // Append al file mappings
        char mappings_path[256];
        snprintf(mappings_path, sizeof(mappings_path), "%s/mappings", dir_path);
        append_file(user_path, mappings_path);

        // Libera la memoria allocata
        free_select_list(&select_list);
    }
    closedir(dir);

    free_selectable_list(&selectable_list);
  
    // Fine ciclo 
    check_and_add_include(argv[1], transformed_path);
    run_apparmor_parser(argv[1]);
    
    return EXIT_SUCCESS;
}

