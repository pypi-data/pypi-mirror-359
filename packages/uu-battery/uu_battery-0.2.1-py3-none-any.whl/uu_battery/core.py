from .helpers import requests, pd, StringIO, os, TOKEN_PATH, DOWNLOAD_URL, CAS_LOGIN_URL, save_token, load_token, login_to_uu_cas

#### Main Functions ---------------------------------------------------------------------------------------------------------------

def logout():
    """
    Log out from the UU CAS session by clearing the token cache.
    """
    if TOKEN_PATH.exists():
        os.remove(TOKEN_PATH)
        print("Logged out successfully.")
    else:
        print("No active session found to log out.")

def get_data(file_id: str, session_key=None, base_url=DOWNLOAD_URL) -> pd.DataFrame:
    """
    Fetch data from a given URL and return it as a pandas DataFrame.
    
    Parameters:
    - file_id (str): Id of the file to be fetched, get ID from the researchcloud frontend.
    - cas_key (str): The CAS key to be used in the request. If not provided, it will attempt to load from cache.
    - base_url (str): The base URL for the API endpoint.
    
    Returns:
    - pd.DataFrame: The fetched data as a DataFrame.
    """
    try:
        # Construct the request
        data_url = base_url + file_id
        session = requests.Session()
        session_key=load_token() if session_key is None else session_key
        if session_key is not None:
            session.cookies.set("MOD_AUTH_CAS_S", session_key)

        # Attempt to send the request
        response = session.get(data_url)

        if response.status_code == 403 or "idp" in response.url:
            #Invalid session or not logged in, prompt for login
            session_token = login_to_uu_cas(data_url)
            session.cookies.set("MOD_AUTH_CAS_S", session_token)
            save_token(session_token) # cache the token for future use
            response = session.get(data_url) # resend the request with the new session token
        
        if response.status_code == 200:
            try:
                # Attempt to read the response as CSV
                return pd.read_csv(StringIO(response.text))
            except pd.errors.ParserError:
                print("Error parsing CSV data. The response may not be in the expected format. Response text:", response.text)
                return pd.DataFrame()
        if response.status_code == 403:
            # Here if CAS login is successful but the user is not whitelisted for the requested data
            raise ValueError("Access denied. Contact an administrator to get whitelisted.")
        else:
            raise ValueError(f"Failed to fetch data: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()
    except RuntimeError as e:
        print(f"An error occurred during login: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"{e}")
        return pd.DataFrame()