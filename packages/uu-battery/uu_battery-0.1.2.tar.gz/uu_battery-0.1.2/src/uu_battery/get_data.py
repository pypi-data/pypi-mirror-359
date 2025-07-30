import requests
import pandas as pd
from io import StringIO

def get_data(file_id: str, cas_key: str, base_url="https://researchcloud.kemi.uu.se/api/download_file/?file_id=") -> pd.DataFrame:
    """
    Fetch data from a given URL and return it as a pandas DataFrame.
    
    Parameters:
    - file_id (str): Id of the file to be fetched, get ID from the researchcloud frontend.
    - cas_key (str): The CAS key to be used in the request. Identifies the user session. Log in to the researchcloud frontend to get the key.
    - base_url (str): The base URL for the API endpoint.
    
    Returns:
    - pd.DataFrame: The fetched data as a DataFrame.
    """
    try:
        headers = {'Cookie': f'MOD_AUTH_CAS_S={cas_key}'}
        response = requests.get(base_url+file_id, headers=headers)
        
        if response.status_code == 200:
            try:
                return pd.read_csv(StringIO(response.text))
            except pd.errors.ParserError:
                print("Error parsing CSV data. The response may not be in the expected format. Response text:", response.text)
                return pd.DataFrame()
        else:
            raise ValueError(f"Failed to fetch data: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()