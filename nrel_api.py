import pandas as pd
import numpy as np
import sys, os
import requests
import io

API_USER = 'naroman2@asu.edu'
API_KEY = 'xvwm5lypqAqWSxnwdny7IzPfrkHKfqg2gDFDV9nk'

class NrelApi():
    
    def initialize(self, lat, lon, yr, attr, leap_yr, int_val, utc, f_name, use, aff, email, ml):

        self.lattitude = lat
        self.longitude = lon
        self.year = yr
        self.attributes = attr
        self.leap_year = leap_yr
        self.interval = int_val
        self.utc_time = utc
        self.your_name = f_name
        self.reason_for_use = use
        self.affiliation = aff
        self.your_email = email
        self.mailing_list = ml

    def get_nrel_df(self) -> pd.DataFrame:

        # Declare url string
        url = f'''https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt=POINT({self.longitude}%20{self.lattitude})
            &names={self.year}&leap_day={self.leap_year}&interval={self.interval}&utc={self.utc_time}&full_name={self.your_name}&email={API_USER}&
            affiliation={self.affiliation}&mailing_list={self.mailing_list}&reason={self.reason_for_use}&api_key={API_KEY}&attributes={self.attributes}'''

        # info = pd.read_csv(url, nrows=1)
        df = requests.get(url).content
        df = pd.read_csv(io.StringIO(df.decode('utf-8')), skiprows = 2)
        return df
    

        