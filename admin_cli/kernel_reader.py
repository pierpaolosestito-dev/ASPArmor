import pwd

from my_shared_library.info_dao import Info

def extract_enforce_profiles(row_to_start=-1):
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
    return enforce_records,len(lines)-1

def extract_info(users,enforces):
    filtered_profiles_info = []
    for user in users:
        for enforce in enforces:
            if "//" in enforce:
                splitted = enforce.split("//")
                if user in splitted[1]:
                    info = Info(user,splitted[0],enforce)
                    filtered_profiles_info.append(info)
    return filtered_profiles_info


def template_method_to_read_kernel_and_process(users,row_to_start = -1):
    enforce_profiles,last_row = extract_enforce_profiles(row_to_start)
    filtered_profiles_info = extract_info(users,enforce_profiles)
    return filtered_profiles_info,last_row


#print(template_method_to_read_kernel_and_process(users,130))





