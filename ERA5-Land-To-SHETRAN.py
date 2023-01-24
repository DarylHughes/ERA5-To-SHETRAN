# -*- coding: utf-8 -*-
"""
Date created:   2023.01.23
Last modified:  2023.01.24
@author:        Daryl Hughes


This script:
    - Downloads ERA5-Land data via the CDS (Climate Data Store) API
    - Writes data to drive
    - Reads ERA5 data [m]
    - Plots data
    - Wrangles data into SHETRAN input file format

File information:
    - ERA5-Land file may contain multiple variables for the specified time period
    at hourly intervals, for the entire globe at 0.1 x 0.1 degree.
    - The variable of interest is 'total evaporation' in units m water equivalent
    - The file extension is '.nc'

Outputs are:
    - An evaporation map for a SHETRAN model (with some GIS processing)
    - An evaporation time series for a SHETRAN model
    
The user must define:
    - 'FunctionsLibrary' which contains custom functions
    - 'DirectoryIn' which contains the ASC files
    - 'DirectoryOut' which contains the output TXT files
    - 'FileNameIn' which is the download file name
    - 'FileNameOut' which is the output file name
    - 'ExtIn' which is the file extension of the downloaded WFDE5 data
    - 'North'  which is the northern limit of the data domain
    - 'South' which is the southern limit of the data domain
    - 'West' which is the western limit of the data domain
    - 'East' which is the eastern limit of the data domain
    
    
"""


#%% User-defined variables

FunctionsLibrary    = ''                                                        # Set to directory containing CustomFunctionsToSHETRAN.py
DirectoryIn         = ''                                                        # Set to directory containing raw data. NB string must terminate with '/'
DirectoryOut        = ''
FileNameIn          = ''                                                        # Specify download file name
FileNameOut         = ''                                                        # Specify output file name
ExtIn               = '.nc'
North               = 8.21                                                      # Set coordinates
South               = 1.09
West                = -62.94
East                = -57.67


# List of evaporation variables
EvapList = ['pev',                                                              # potential evaporation
            'e',                                                                # total evaporation
            'evabs',                                                            # bare soil evaporation
            'evaow',                                                            # open water evaporation
            'evavt',                                                            # vegetation transpiration
            'evatc']                                                            # top of canopy evaporation


#%% Import modules and functions

import os
import pandas as pd
from netCDF4 import Dataset                                                     # Package index page documentation https://pypi.org/project/netCDF4/

os.chdir(FunctionsLibrary)                                                      # Sets working directory to enable custom functions to be used
from CustomFunctionsToSHETRAN import NetCDFPlotter
from CustomFunctionsToSHETRAN import NetCDFToSHETRAN


#%% Download data from Copernicus using API
'''
Data can be downloaded using either:
    A) the web browser user interface (https://cds.climate.copernicus.eu/)
    B) the CDS (Climate Data Store) API:
        - Create CDS account:       https://cds.climate.copernicus.eu/
        - Install cdsapi package:   https://cds.climate.copernicus.eu/api-how-to
        - Install CDS API key:      https://confluence.ecmwf.int/display/CKB/How+to+install+and+use+CDS+API+on+Windows
        - Download page:            https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=form
        - Data documentation:       https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation
        - Check request status:     https://cds.climate.copernicus.eu/cdsapp#!/yourrequests
        - Run script below (once)

'''


'''
# Download script

import cdsapi                                                                   # Package index page https://pypi.org/project/cdsapi/

os.chdir(DirectoryIn)

# name client
c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-land',
    {
        'variable': ['total_evaporation',
                     ],
        'year': [   '2000',
            ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00',
        ],
        'area': [
            North, West, South, East,
        ],
        'format': 'netcdf',
    },
    FileNameIn + ExtIn)

os.chdir(FunctionsLibrary)

'''



#%% Read and wrangle ERA5 data

# Read in ERA5 file
ERA5 = Dataset(DirectoryIn + FileNameIn + ExtIn)

# Interrogate data
ERA5.variables.keys()
ERA5.variables

# Create datetime index (ERA units are hours since 1900-01-01 00:00:00.0)
ERA5DateIndex = pd.DataFrame(pd.date_range(start='1900-01-01 00:00:00',
                                           end = '2030-01-01 00:00:00',
                                           freq = 'H'))

# Loop through all days in ERA5 data and calculate absolute datetimes
TimeIndex   = []

# Calculate absolute datetime from ERA5 relative datetime
for Time in range(len(ERA5.variables['time'])):
    TimeIndex.append(ERA5DateIndex.loc[ERA5.variables['time'][Time]][0])        # Return time of ERA parameter in hours and match to date

# Create DataFrame of timeIndex
DfTimeIndex = pd.DataFrame(data     = TimeIndex,
                           columns  = ['dateTime'])

# Convert datetime to date index
StartTime   = TimeIndex[0]
EndTime     = TimeIndex[-1]
StartIdx    = DfTimeIndex.index[DfTimeIndex['dateTime']==StartTime].tolist()[0]
EndIdx      = DfTimeIndex.index[DfTimeIndex['dateTime']==EndTime].tolist()[0]


#%% Plot map of time point, and time series of point

NetCDFPlotter(Variable          = EvapList[1],
              Data              = ERA5,
              Time              = 0,
              Lon               = 0,
              Lat               = 0,
              South             = 0,
              North             = 72,
              West              = 0,
              East              = 53,
              UnitConversion    = 1000,
              )


#%% Wrangle Data into SHETRAN format using NetCDFToSHETRAN function

NetCDFToSHETRAN(Data            = ERA5,
                Variable        = EvapList[1],
                Dates           = DfTimeIndex['dateTime'],
                LongitudeName   = 'longitude',
                LatitudeName    = 'latitude',
                Path            = DirectoryOut,
                File            = FileNameOut + '.csv',
                UnitConversion  = 1000)


#%% Close the file
ERA5.close()





