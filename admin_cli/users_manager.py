import pwd,grp
import spwd
import getpass
import crypt
import os

def verify_password(username,password):
    shadow_entry = spwd.getspnam(username)
    hashed_password = shadow_entry.sp_pwdp
    return crypt.crypt(password,hashed_password) == hashed_password
def users_list():
    users = [user.pw_name for user in  pwd.getpwall() if user.pw_uid >= 1000 and user.pw_name != "nobody"]
    return users

def users_without_files(users_list,path):
    users_without_files = []
    for user in users_list:
        user_file = os.path.join(path,user)
        if not os.path.exists(user_file):
            users_without_files.append(user)
    return users_without_files

def __user_exists(username):
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False

def __is_user_in_group(username,groupname):
    try:
        group_info = grp.getgrnam(groupname)
        return username in group_info.gr_mem
    except KeyError:
        return False

