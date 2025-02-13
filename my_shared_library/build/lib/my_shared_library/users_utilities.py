import os 
import pwd
import spwd 


def get_logged_user():
	uid = os.geteuid()
	current_user = pwd.getpwuid(uid).pw_name
	return current_user

def verify_password(username,password):
	shadow_entry = spwd.getpsnam(username)
	hashed_password = shadow_entry.sp_pwdp
	return crypt.crypt(password,hashed_password) == hashed_password

def users_list():
	users = [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000 and user.pw_name != "nobody"]
	return users 

def users_without_profiles(users_list,path):
	users_without_files = []
	for user in users_list:
		user_file = os.path.join(path,user)
		if not os.path.exists(user_file):
			users_without_files.append(user)
	return users_without_files

def user_exists(username):
	try:
		pwd.getpwnam(username)
		return True 
	except KeyError:
		return False

def user_belongs_to_group(username,groupname):
	try:
		group_info = grp.getgrnam(groupname)
		return username in group_info.gr_mem
	except KeyError:
		return False  
