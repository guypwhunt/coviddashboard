import pickle
import pandas as pd
from uk_covid19 import Cov19API
class timeseries():
    def __init__(self, file_name, columns, filters, structure):
        self.file_name = file_name
        with open(file_name, 'rb') as f:
            self.df = pickle.load(f)
        self.columns = columns
        self.filters = filters
        self.structure = structure
    def access_api(self):
        """ Accesses the PHE API"""
        # Create an API object
        api = Cov19API(filters=self.filters, structure=self.structure)
        # Get the API rsponse
        self.response = api.get_json()
    def wrangle_data(self):
        """ Parameters: rawdata - data from json file or API call. Returns a dataframe.
        Edit to include the code that wrangles the data, creates the dataframe and fills it in. """
        datalist=self.response['data']
        # Extract all dates from the datalist and sort them in order
        dates=[dictionary['date'] for dictionary in datalist]
        dates.sort()
        # Function to convert a date string into a pandas datetime object
        def parse_date(datestring):
            """ Convert a date string into a pandas datetime object """
            return pd.to_datetime(datestring, format="%Y-%m-%d")
        # Create a panda date for the first date in the series
        startdate=parse_date(dates[0])
        # Create a panda date for the last date in the series
        enddate=parse_date(dates[-1])
        # Create a list of dates from the start date to the end date
        index=pd.date_range(startdate, enddate, freq='D')
        # Create a timeseries of dates with the columns
        timeseriesdf=pd.DataFrame(index=index, columns=self.columns)
        # Update the timeseries with data for the columns ['cases', 'hospital', 'deaths']
        for entry in datalist:
            date=parse_date(entry['date'])
            for column in self.columns:
                if pd.isna(timeseriesdf.loc[date, column]): 
                    # Replace none values with 0 in our data 
                    value= float(entry[column]) if entry[column]!=None else 0.0
                    # Update the column with the correct data
                    timeseriesdf.loc[date, column]=value
        # Fill in any empty values with 0s
        timeseriesdf.fillna(0.0, inplace=True)
        self.df = timeseriesdf