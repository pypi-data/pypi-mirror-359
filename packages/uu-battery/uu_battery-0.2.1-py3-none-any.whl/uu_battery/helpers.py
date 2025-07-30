import requests
from bs4 import BeautifulSoup
import getpass
import pandas as pd
from io import StringIO
import os
import json
from pathlib import Path

# CONSTANTS
DOWNLOAD_URL = "https://researchcloud.kemi.uu.se/api/download_file/?file_id="
CAS_LOGIN_URL = "https://weblogin.uu.se/idp/profile/cas/login"
TOKEN_PATH = Path.home() / ".uu_data_token"


### Helper Functions -------------------------------------------------------------------------------------------------------------
# Cache the token to avoid re-login
def save_token(token: str):
    with open(TOKEN_PATH, "w") as f:
        json.dump({"token": token}, f)

# Load the cached token if it exists
def load_token() -> str | None:
    if TOKEN_PATH.exists():
        try:
            with open(TOKEN_PATH, "r") as f:
                return json.load(f).get("token")
        except Exception:
            return None
    return None

def login_to_uu_cas(service_url: str) -> str:
    """
    Log in to the UU CAS system and return the session token.
    This function is tailored for the UU joint weblogin page,
    if the layout or the authentication system changes,
    the function needs to be updated accordingly.
    Last updated on 2025-07-03.

    Parameters:
    - service_url (str): The URL of the service to access after login.
    Returns:
    - str: The session token (MOD_AUTH_CAS_S cookie).
    Raises:
    - RuntimeError: If token retrieval fails, typically due to invalid credentials.
        This will however also raise in case the login page layout changes
        and the function needs to be updated.

    """

    session = requests.Session()
    cas_login_base = CAS_LOGIN_URL
   
   #Get the login page for joint weblogin
    login_url = f"{cas_login_base}?service={service_url}"
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the CSRF token and execution parameter from the login form
    csrf_token = soup.find("input", {"name": "csrf_token"})["value"]
    execution = soup.find("form")["action"].split("execution=")[-1]

    # Prompt user for credentials
    username = input("UU CAS Username: ")
    password = getpass.getpass("UU CAS Password: ")

    # Construct POST payload
    post_data = {
        "csrf_token": csrf_token,
        "execution": execution,
        "j_username": username,
        "j_password": password,
        "_eventId_proceed": "Log in",
    }

    # POST login form
    post_url = f"{cas_login_base}?execution={execution}&service={service_url}"
    session.post(post_url, data=post_data, allow_redirects=True)

    # Extract the MOD_AUTH_CAS_S cookie
    token = session.cookies.get("MOD_AUTH_CAS_S")
    if not token:
        # If token is not set, login failed
        # which in 99% of cases means invalid credentials.
        raise RuntimeError("Login failed — invalid credentials.")
    
    print("Login successful.")
    return token