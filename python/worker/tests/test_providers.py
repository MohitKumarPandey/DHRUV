import datetime
from ingestion.providers import NSIDCProvider

def test_nsidc_provider_search():
    provider = NSIDCProvider()
    
    # We use a date in the past to ensure CMR returns results
    start_time = datetime.datetime(2023, 1, 1)
    end_time = datetime.datetime(2023, 1, 2)
    
    # Real external HTTP request to NASA CMR
    records = provider.fetch_data(start_time, end_time, bbox={})
    
    # If the network is available, it should return records
    assert len(records) > 0
    assert records[0].product_name == "G02135 (Sea Ice Index)"
    assert records[0].provider.name == "NSIDC"
