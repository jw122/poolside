from google.appengine.api import users
import logging

def is_admin():
	user = users.get_current_user()
	if user and users.is_current_user_admin():
		return True
	else:
		return False
