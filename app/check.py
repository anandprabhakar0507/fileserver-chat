from functools import wraps
from flask import session, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
		try:
			if session['user'] != 1:
				return redirect('/')
			return f(*args, **kwargs)
		except:
			return redirect('/')
    return decorated_function
