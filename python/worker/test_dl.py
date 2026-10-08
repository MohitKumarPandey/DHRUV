import os
import requests
from dotenv import load_dotenv
import sys
sys.path.append('.')
from ingestion.providers.providers import NSIDCProvider, CopernicusProvider
from datetime import datetime, timedelta

load_dotenv('e:/DHRUV/.env')

start_time = datetime.utcnow() - timedelta(days=2)
end_time = datetime.utcnow()

# Test NSIDC
print("--- NSIDC ---")
try:
    nsidc = NSIDCProvider()
    records = nsidc.fetch_data(start_time, end_time, {})
    if records and records[0].file_path:
        url = records[0].file_path
        print("URL:", url)
        # Authenticated download
        session = requests.Session()
        session.auth = (os.environ['EARTHDATA_USERNAME'], os.environ['EARTHDATA_PASSWORD'])
        r1 = session.get(url)
        if r1.status_code == 401:
            r1 = session.get(r1.url) # Redirects
        print("Download Status:", r1.status_code)
        if r1.status_code == 200:
            print("Size:", len(r1.content))
            with open('test_nsidc.nc', 'wb') as f:
                f.write(r1.content)
            print("NSIDC Downloaded")
except Exception as e:
    print("NSIDC failed:", str(e))

# Test Copernicus
print("--- COPERNICUS ---")
try:
    cop = CopernicusProvider()
    records = cop.fetch_data(start_time, end_time, {})
    if records and records[0].file_path:
        url = records[0].file_path
        print("URL:", url)
        # Authenticated download using Token
        token = os.environ['COPERNICUS_TOKEN']
        headers = {'Authorization': f'Bearer {token}'}
        r2 = requests.get(url, headers=headers)
        print("Download Status:", r2.status_code)
        if r2.status_code == 200:
            print("Size:", len(r2.content))
            with open('test_cop.zip', 'wb') as f:
                f.write(r2.content)
            print("Copernicus Downloaded")
except Exception as e:
    print("Copernicus failed:", str(e))
