import requests
from datetime import datetime, timedelta
start_time = datetime.utcnow() - timedelta(days=2)
end_time = datetime.utcnow()
search_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Collection/Name eq 'SENTINEL-1' and ContentDate/Start ge {start_time.isoformat()}Z and ContentDate/Start le {end_time.isoformat()}Z&$top=1"
print(search_url)
r = requests.get(search_url)
print(r.status_code)
print(list(r.json().keys()))
print(len(r.json().get('value', [])))
