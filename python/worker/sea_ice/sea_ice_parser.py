import os
import datetime
import netCDF4
import numpy as np
from ingestion.providers.providers import ScientificRecord, ProviderEnum, DataQuality


def _extract_grid(nc_dataset):
    """Extract latitude, longitude and SIC arrays from an NSIDC NetCDF file.
    The official NSIDC SIC product uses variables:
        - latitude (degrees_north)
        - longitude (degrees_east)
        - sea_ice_concentration (percent, 0‑100, with fill value 255)
    """
    lat = nc_dataset.variables.get('latitude') or nc_dataset.variables.get('lat')
    lon = nc_dataset.variables.get('longitude') or nc_dataset.variables.get('lon')
    sic = nc_dataset.variables.get('sea_ice_concentration') or nc_dataset.variables.get('sic')
    if lat is None or lon is None or sic is None:
        raise ValueError('Required variables missing in NetCDF file')
    lat_arr = lat[:].astype(np.float32)
    lon_arr = lon[:].astype(np.float32)
    sic_arr = sic[:].astype(np.float32)
    # NSIDC uses 255 as fill/missing value
    sic_arr = np.where(sic_arr == 255, np.nan, sic_arr)
    return lat_arr, lon_arr, sic_arr


def parse_nsidc_netcdf(file_path: str, provider_name: str = 'NSIDC') -> ScientificRecord:
    """Parse a downloaded NSIDC sea‑ice NetCDF file and return a populated ScientificRecord.

    Parameters
    ----------
    file_path: str
        Absolute path to the NetCDF file.
    provider_name: str
        Human readable provider identifier (defaults to 'NSIDC').

    Returns
    -------
    ScientificRecord
        Record containing provenance and minimal quality flag. Grid data is **not** stored in the record –
        it is expected to be handed to downstream engines (e.g., SeaIceForecastEngine).
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"NetCDF file not found: {file_path}")

    with netCDF4.Dataset(file_path, 'r') as ds:
        lat_arr, lon_arr, sic_arr = _extract_grid(ds)
        # Basic sanity checks – at least one non‑nan value
        if np.isnan(sic_arr).all():
            quality = DataQuality.RED
        else:
            # Very naive quality: if >90% of values are non‑nan assume good
            coverage = 1 - np.isnan(sic_arr).mean()
            quality = DataQuality.GREEN if coverage > 0.9 else DataQuality.YELLOW

        # Derive timestamps from global attributes if present
        obs_time_str = ds.getncattr('time_coverage_start') if 'time_coverage_start' in ds.ncattrs() else None
        prod_time_str = ds.getncattr('production_date_time') if 'production_date_time' in ds.ncattrs() else None
        observation_time = datetime.datetime.fromisoformat(obs_time_str.rstrip('Z')) if obs_time_str else datetime.datetime.utcnow()
        processing_time = datetime.datetime.fromisoformat(prod_time_str.rstrip('Z')) if prod_time_str else datetime.datetime.utcnow()

        record = ScientificRecord(
            provider=ProviderEnum.NSIDC,
            product_name=ds.getncattr('title') if 'title' in ds.ncattrs() else 'NSIDC Sea Ice Concentration',
            observation_time=observation_time,
            processing_time=processing_time,
            spatial_resolution='{} km'.format(ds.getncattr('spatial_resolution') if 'spatial_resolution' in ds.ncattrs() else 'unknown'),
            geographic_coverage='Antarctic',
            quality_state=quality,
            product_version=ds.getncattr('version_id') if 'version_id' in ds.ncattrs() else 'unknown',
            retrieval_timestamp=datetime.datetime.utcnow(),
        )
        return record
