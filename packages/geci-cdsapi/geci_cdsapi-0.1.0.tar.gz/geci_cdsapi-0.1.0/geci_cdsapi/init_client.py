import cdsapi
import os


def download_wind_netcdf_by_year(years, island, directory_path):
    client = init_client()
    dataset = "reanalysis-era5-single-levels"
    for year in years:
        request_params = construct_request(year, island)
        output_path = f"{directory_path}/{island}_wind_{year}.nc"
        client.retrieve(dataset, request_params, output_path)


def construct_request(year, island):
    years = [str(year)]
    areas = {"San Benito": [32.35, -120.3, 24.25, -110.9]}
    request_params = {
        "product_type": "reanalysis",
        "variable": ["10m_u_component_of_wind", "10m_v_component_of_wind"],
        "year": years,
        "month": ["07", "08", "09", "10", "11"],
        "day": [f"{i:02d}" for i in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(0, 24)],
        "format": "netcdf",
        "area": areas[island],
    }
    return request_params


def init_client():
    client = cdsapi.Client(url="https://cds.climate.copernicus.eu/api", key=load_access_key())
    return client


def load_access_key():
    return os.environ.get("CDSAPI_KEY")
