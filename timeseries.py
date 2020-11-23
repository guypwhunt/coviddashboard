import json
import time
import pandas as pd
from uk_covid19 import Cov19API
class timeseries():
    def __init__(self, file_name, columns, filters, structure,series, scale, apibutton):
        self.file_name = file_name
        self.columns = columns
        self.filters = filters
        self.structure = structure
        self.series = series
        self.scale = scale
        self.apibutton = apibutton
        # If the file exists JSON will be loaded
        try:
            with open(self.file_name, "rt") as INFILE:
                self.json=json.load(INFILE)
        # If the file does not the API call will be made and save the response to the file
        except:
            self.access_api()
            self.save_json()
            with open(self.file_name, "rt") as INFILE:
                self.json=json.load(INFILE)
    def access_api(self):
        """ Accesses the PHE API"""
        # Create an API object
        api = Cov19API(filters=self.filters, structure=self.structure)
        # Get the API rsponse
        self.json = api.get_json()
    def wrangle_data(self):
        """ Parameters: rawdata - data from json file or API call. Returns a dataframe.
        Edit to include the code that wrangles the data, creates the dataframe and fills it in. """
        datalist=self.json['data']
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
    def save_json(self):
        """ Save JSON to file"""
        with open(self.file_name, "wt") as OUTF:
            json.dump(self.json, OUTF)
    def timeseries_graph(self, gcols, gscale):
        """Flicks between log scale and columns displayed on the graph"""
        self.gcols = gcols
        self.gscale = gscale
        if self.gscale=='linear':
            logscale=False
        else:
            logscale=True
        ncols=len(self.gcols)
        if ncols>0:
            self.df[list(self.gcols)].plot(logy=logscale)
        else:
            print("Click to select data for graph")
            print("(CTRL-Click to select more than one category)")
    def refresh_graph(self):
        """ We change the value of the widget in order to force a redraw of the graph;
        this is useful when the data have been updated. This is a bit of a gimmick; it
        needs to be customised for one of your widgets. """
        current=self.scale.value
        if current==self.scale.options[0]:
            other=self.scale.options[1]
        else:
            other=self.scale.options[0]
        self.scale.value=other # forces the redraw
        self.scale.value=current # now we can change it back"""
    def api_button_callback(self, button):
        """ Button callback - it must take the button as its para to accesses API, wrangles data, updates global variable df used for plotting. """
        # Try calling the api
        try:
            self.access_api()
            # Format the data for plotting
            self.wrangle_data()
            # Save the outputs to the JSON file for when the dashboard is next viewd
            self.save_json()
            # Trigger the graph to refresh
            self.refresh_graph()
            # Update the Button to show the API was successful
            self.apibutton.description='Successful!'
            self.apibutton.icon="check"
            self.apibutton.button_style='success'
            self.apibutton.disabled=True
            time.sleep(3)
            # Reset the Button 
            self.apibutton.description='Refresh Data'
            self.apibutton.icon="refresh"
            self.apibutton.button_style='primary'
            self.apibutton.disabled=False
        except:
            # Update the Button to show the API failed
            self.apibutton.description='Error'
            self.apibutton.icon="fa-exclamation-triangle"
            self.apibutton.button_style='warning'
            self.apibutton.disabled=True
            time.sleep(3)
            # Reset the Button
            self.apibutton.description='Refresh Data'
            self.apibutton.icon="refresh"
            self.apibutton.button_style='primary'
            self.apibutton.disabled=False