def __process_selected_map_to_str(selected_map):
    __str = ""
    for chiave, valore in selected_map.items():
        # print(f"{chiave} -> {valore}")
        __str += f"{selected_map[chiave]['rule']}\n"
    return __str

def __process_base_perms_to_str(base_perms):
    return '\n'.join(base_perms)

def __mix_selected_rules(base_perms_str, selected_map_str, first_base_perms=True):
    if first_base_perms:
        return base_perms_str + "\n" + selected_map_str
    else:
        return selected_map_str + "\n" + base_perms_str

def __get_uncommon(mixed_list,filtered_content_list):
    uncommon = []
    for rule in mixed_list:
        if rule not in filtered_content_list:
            uncommon.append(rule)
    return uncommon

