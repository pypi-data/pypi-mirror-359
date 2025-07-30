# UU Battery Package
This is a package intended for interacting with the UU battery data handler project. For more information, see [UU-Battery-Data-Handler on GitHub]("https://github.com/fabianwilson/UU-Battery-Data-Handler").

**Installation:** `pip install uu-battery`

## Requires
- [Pandas]("https://pandas.pydata.org/") (`pip install pandas`)
- [Requests]("https://requests.readthedocs.io/en/latest/") (`pip install requests`)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (`pip install bs4`)
## Features
The package features a function `get_data(file_id)` which fetches data with a specific ID and outputs it as a pandas dataframe. The file ID can be obtained at https://researchcloud.kemi.uu.se/datasets, for more information please refer to [UU-Battery-Data-Handler on GitHub]("https://github.com/fabianwilson/UU-Battery-Data-Handler"). On the first call of the session, the user will be prompted for their UU joint-weblogin authentication details. Note that it may take a few seconds to contact the CAS servers to authenticate the user. The session is then valid for 2 hours if active or 1 hour if inactive and no further entering of credentials is needed during this time. To forcefully invalidate the session call `logout()`.

**Example code:**
```python
import pandas as pd
import uu_battery

file_id="6316ffd3-67f3-4bd0-98c5-2beb6e944938" #Obtain from the frontend

data=uu_battery.get_data(file_id)
print(data.head(5))
```