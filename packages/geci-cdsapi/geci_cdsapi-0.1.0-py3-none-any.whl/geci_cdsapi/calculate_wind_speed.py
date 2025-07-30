import numpy as np
import xarray as xr
import pandas as pd


def read_and_calculate_wind_speed(years, island, directory_path):
    paths_to_read = [f"{directory_path}/{island}_wind_{year}.nc" for year in years]
    nc = xr.open_mfdataset(paths_to_read)
    monthly_wind_dataset = calculate_monthly_wind_speed(nc)
    return monthly_wind_dataset.dropna(dim="valid_time")


def write_windspeed_dataset_to_csv(dataset, output_path):
    windspeed_df_longer = transform_to_longer_df(dataset)
    extract_month_and_year_into_columns(windspeed_df_longer)
    windspeed_df_longer.loc[:, ["Índice", "Año", "Mes/Periodo", "Valor"]].to_csv(
        output_path, index=False
    )


def extract_month_and_year_into_columns(windspeed_df_longer):
    windspeed_df_longer["Año"] = windspeed_df_longer["valid_time"].dt.year
    windspeed_df_longer["Mes/Periodo"] = windspeed_df_longer["valid_time"].dt.month_name().str[:3]


def transform_to_longer_df(dataset):
    windspeed_df = dataset.to_dataframe().reset_index()
    windspeed_df_longer = pd.melt(
        windspeed_df,
        id_vars=["valid_time"],
        value_vars=["u10", "v10", "wind_speed"],
        var_name="Índice",
        value_name="Valor",
    )

    return windspeed_df_longer


def calculate_monthly_wind_speed(nc):
    nc["wind_speed"] = calculate_wind_speed(nc)
    return mean_by_month(nc)


def calculate_wind_speed(dataset):
    return np.sqrt(dataset["u10"] ** 2 + dataset["v10"] ** 2)


def mean_by_month(dataset):
    spatial_mean = dataset.mean(dim=["latitude", "longitude"])
    return spatial_mean.resample(valid_time="ME").mean()
