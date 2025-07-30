from geci_cdsapi.init_client import download_wind_netcdf_by_year
from geci_cdsapi.calculate_wind_speed import (
    read_and_calculate_wind_speed,
    write_windspeed_dataset_to_csv,
)
import geci_cdsapi

import typer
from pathlib import Path


cli = typer.Typer()


@cli.command()
def monthly_wind_average(
    start_year: int = typer.Option(),
    end_year: int = typer.Option(),
    island: str = typer.Option(),
    output_path: str = typer.Option(),
):
    years = [year for year in range(start_year, end_year + 1)]
    path = Path(output_path)
    directory_path = path.parent
    download_wind_netcdf_by_year(years, island, directory_path)
    wind_speed_dataset = read_and_calculate_wind_speed(years, island, directory_path)
    write_windspeed_dataset_to_csv(wind_speed_dataset, output_path)


@cli.command()
def version():
    print(geci_cdsapi.__version__)
