# %%
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests
from glob import glob

from pvlib import pvsystem, modelchain, location, irradiance
from pvlib.solarposition import get_solarposition
from pvlib import irradiance, solarposition

# %%
def get_hourly_weather_data_for_pvlib(stations, start_date, end_date, timezone = 'UTC'):
    '''
    Function to get hourly weather variables T (temperature) and
    Q (global radiation) from KNMI 
    
    Args: 
        stations   (str): NMI-stations separated by ':' 
        start_date (str): start date, format yyyymmdd
        end_date   (str): end date (included), format yyyymmdd
        timezone   (str, optional): timezone

    Returns:
        df: DataFrame with DateTime-index, columns T (temp), Q (global radiation) 
    '''

    url = 'https://www.daggegevens.knmi.nl/klimatologie/uurgegevens'

    data = {
        'start': start_date,
        'end': end_date,
        'vars': 'Q:T:FH',
        'stns': stations,
        'fmt': 'json'
        }

    response = requests.post(url, data = data)    
    weather_df = pd.DataFrame(response.json())
    # correct units
    weather_df['T'] = weather_df['T'] / 10          # is in 0.1 degrees C, to degrees C
    weather_df['Q'] = weather_df['Q'] * (1 / 0.36)  # is in J/m2, to W / m2
    weather_df['FH'] = weather_df['FH'] * 10 # from 0.1 m/s to m/s         
    
    # create date_time index, convert timezone
    weather_df['hour'] = weather_df['hour'] - 1     # is from 1-24, to 0-23
    weather_df['date_time'] = pd.to_datetime(weather_df['date']) + pd.to_timedelta(weather_df['hour'].astype(int), unit='h')
    weather_df.index = weather_df.date_time
    weather_df = weather_df.drop(['station_code', 'date', 'hour', 'date_time'], axis = 1)
    weather_df.index = weather_df.index.tz_convert(timezone)

    # shift date_time by 30 minutes, 'average time' during that hour
    # weather_df.index = weather_df.index.shift(freq="30min")

    return weather_df

def process_weather_data(weather_df: pd.DataFrame, lat: float, lon: float) -> pd.DataFrame:
    """
    Process weather data to calculate DNI and DHI.

    Parameters:
    - weather_df: DataFrame containing weather data with datetime index, temperature (T), and GHI (Q).
    - lat: Latitude of the location.
    - lon: Longitude of the location.

    Returns:
    - DataFrame: Processed weather data with added DNI, DHI, no NaN values.
    """
    # Get solar position for the dates / times
    solpos_df = solarposition.get_solarposition(
        weather_df.index, latitude=lat,
        longitude=lon, altitude=0,
        temperature=weather_df['T']
    )
    solpos_df.index = weather_df.index

    # Method 'Erbs' to go from GHI to DNI and DHI
    irradiance_df = irradiance.erbs(weather_df['Q'], solpos_df['zenith'], weather_df.index)
    irradiance_df['ghi'] = weather_df['Q']

    # Add DNI and DHI to weather_df
    columns = ['dni', 'dhi']
    weather_df[columns] = irradiance_df[columns]

    # Fill NaN values with 0
    weather_df.fillna(0, inplace=True)
    
    return weather_df
# %%
timezone = 'Europe/Amsterdam'

# Whole year of 2023
start_date = '20230101'
end_date = '20231231'
# Eindhoven KNMI STATION
station = '370'
lat = 51.449772459909
lon = 5.3770039280214
# Function get_hourly_weather_data_for_pvlib defined in full code overview below
weather_df = get_hourly_weather_data_for_pvlib(station, start_date, end_date, timezone)
weather_df = process_weather_data(weather_df, lat, lon)



# %%
def read_and_process_csv(file_path):
    # Read the CSV file, with headers
    df = pd.read_csv(file_path)

    # Convert time to UTC standard
    df['time'] = pd.to_datetime(df['time'], utc=True)
        
    # Convert 'W.mean_value' to float
    df['W.mean_value'] = df['W.mean_value'].astype(str).str.replace('"', '').astype(float)
        
    return df

def merge_csv_files(file_pattern):
    # Find all CSV files matching the pattern
    files = glob(file_pattern)
    
    # Process each file and combine them
    df_list = [read_and_process_csv(file) for file in files]
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Sort by time
    combined_df.sort_values('time', inplace=True)

    # Fill empty values with 0
    combined_df.fillna(0, inplace=True)
    
    return combined_df

quarterly_output_df = merge_csv_files('C:/Users/20193362/Desktop/datadujuan/*.csv')

# %%
def prepare_data_for_model(energy_outputs, weather_data):
    model_data = []

    # Process data day by day
    for day in range(365):  # Assuming you have a full year of data
        start_idx = day * 24
        end_idx = (day + 1) * 24

        # Extract daily weather data and energy outputs
        daily_weather = weather_data.iloc[start_idx:end_idx]
        daily_data = energy_outputs['p_mp'][start_idx:end_idx]

        if popt is not None:
            row = {
                # Store sequences as lists in the DataFrame cell
                'temperature_sequence': daily_weather['T'].tolist(),
                'wind_speed_sequence': daily_weather['FH'].tolist(),
                'dni_sequence': daily_weather['dni'].tolist(),
                'dhi_sequence': daily_weather['dhi'].tolist(),
                'global_irradiance_sequence': daily_weather['ghi'].tolist(),
                'gaussian': popt.tolist()
            }
            model_data.append(row)

    return pd.DataFrame(model_data)


# %%
# From quarterly solar output data to hourly
hourly_output_df = quarterly_output_df[quarterly_output_df['time'].dt.minute == 0]
hourly_output_df = hourly_output_df.set_index('time')


# %%'
# Create completely merged dataset
merge = hourly_output_df.join(weather_df)

# Delete incomplete rows 
merge = merge.dropna()

# Save as a csv file
merge.to_csv('result.csv', sep=',', index=True, encoding='utf-8')

# %%
prepare_data_for_model(hourly_output_df, weather_df)
