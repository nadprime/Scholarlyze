##########################################################
# Description: This file contains helper functions for a Flask-based web application.
# It includes utility functions for rendering error messages and enforcing user authentication.

# Functions:
# 1. apology(message, code=400):
#    - Renders an apology message to the user with a given HTTP status code.
#    - Escapes special characters in the message to ensure safe rendering.
#    - Reference: https://github.com/jacebrowning/memegen#special-characters
#
# 2. login_required(f):
#    - A decorator function that restricts access to routes unless the user is logged in.
#    - Redirects unauthenticated users to the login page.
#    - Reference: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
#
# Attribution:
# - The `apology` function references the Memegen Special Characters Guide for escaping special characters.
# - The `login_required` function is adapted from the Flask documentation.

#########################################################

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


