"""
    CS 5001 Project Name: Where to live in SF?
    Xinyi Feng
    This is the pre-part for the main part "map_building_house_adding.py"
    This part processes data from a csv file "crime.scv" download from
    https://data.sfgov.org/Public-Safety/Police-Department-Incident-Reports-2018-to-Present/wg3w-h783/data
    Get zipcode with the count of crime event,and write into a new csv file named "crime_rate_output.csv"
    Please read ReadMe_directory.doc for more info
"""

import pandas as pd
import geopy


def get_zipcode(df, geolocator, lat_field, lon_field):
    """ Converts latitude and longitude into zipcodes
        :parameter:
        df: a pandas dataframe, with two columns longitude and latitude
        a Geopy library use OpenStreetMap nominatim
        https://geopy.readthedocs.io/en/stable/#geopy-is-not-a-service
        lat_field: name of the latitude column
        lon_field: name of the longitude column
        :returns:
        A number with 5 digit (zipcode)
        -1 when there is value err or key err raised
    """
    try:
        location = geolocator.reverse((df[lat_field], df[lon_field]))
        print(location)
        return location.raw['address']['postcode'][:5]
    except (ValueError, KeyError):
        return -1


def main():
    # reads data from original csv file named "crime.csv"
    data = pd.read_csv("data_files/crime.csv")
    # utilizes data in latitude and longitude columns
    df = data[['Latitude', 'Longitude']]
    geolocator = geopy.Nominatim(user_agent='xinyi_sf_map')
    # processes the first 100k rows
    zipcodes = df.head(100000).apply(
        get_zipcode,
        axis=1,
        geolocator=geolocator,
        lat_field='Latitude',
        lon_field='Longitude').value_counts().rename_axis('ZipCode').to_frame('Count')
    # writes into a new csv file for further use( with two columns: zipcode
    # and crime count)
    zipcodes.to_csv('data_files/crime_rate_output.csv')


if __name__ == "__main__":
    main()
