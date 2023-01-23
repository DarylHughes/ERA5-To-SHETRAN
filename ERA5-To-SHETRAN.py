# -*- coding: utf-8 -*-
"""
Date created:   2023.01.23
Last modified:  2023.01.23
@author:        Daryl Hughes


This script:
    - Downloads ERA5-Land data via the CDS API:
        - Download page: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-ERA5-land?tab=overview
        - Documentation: https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation
        - Request status: https://cds.climate.copernicus.eu/cdsapp#!/yourrequests
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

FunctionsLibrary    = 'C:/Users/DH/OneDrive - Heriot-Watt University/Documents/HydrosystemsModellerRA/Writing(Shared)/Paper1'
DirectoryIn         = 'C:/Users/DH/OneDrive - Heriot-Watt University/Documents/HydrosystemsModellerRA/HydroModelling/HydroInputData/PeTimeSeries/ERA5-Land/'
DirectoryOut        = 'C:/Users/DH/Downloads/'
FileNameIn          = 'evaporation_Essequibo_years2000-2021_hours00'               # Specify download file name
FileNameOut         = 'total_evaporation_Essequibo_years_2000-2021_hours00_cells'  # Specify output file name
ExtIn               = '.nc'
North               = 8.21                                                         # Set coordinates
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
import cdsapi
import pandas as pd
from netCDF4 import Dataset

os.chdir(FunctionsLibrary)                                                      # Sets working directory to enable custom functions to be used
from CustomFunctionsToSHETRAN import NetCDFPlotter
from CustomFunctionsToSHETRAN import NetCDFToSHETRAN


#%% Download data from Copernicus using API
'''
# name client
c = cdsapi.Client()

c.retrieve(
    'reanalysis-ERA5-land',
    {
        'variable': ['potential_evaporation',
                     'total_evaporation',
                     'evaporation_from_bare_soil',
                     'evaporation_from_open_water_surfaces_excluding_oceans'
                     'evaporation_from_vegetation_transpiration',
                     'evaporation_from_the_top_of_canopy',
                     ],
        'year': [   '2000',
            '2001', '2002', '2003',
            '2004', '2005', '2006',
            '2007', '2008', '2009',
            '2010', '2011', '2012',
            '2013', '2014', '2015',
            '2016', '2017', '2018',
            '2019', '2020', '2021',
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
    FileName + ExtIn)

'''

#%% Read and wrangle ERA5 data

# Read in ERA5 file
ERA5 = Dataset(DirectoryIn + FileNameIn + ExtIn)

# Interrogate data
ERA5.variables.keys()
ERA5.variables


# Create datetime index (ERA units are hours since 1900-01-01 00:00:00.0)
ERA5DateIndex = pd.DataFrame(pd.date_range(start='1900-01-01 00:00:00',
                                           end = '2022-01-01 00:00:00',
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
StartTime   = '2000-01-01 00:00:00'
EndTime     = '2010-01-01 00:00:00'
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
                LongitudeName   = 'longitude',
                LatitudeName    = 'latitude',
                Path            = DirectoryOut,
                File            = FileNameOut + '.csv',
                UnitConversion  = 1000)


#%% Close the file
ERA5.close()





